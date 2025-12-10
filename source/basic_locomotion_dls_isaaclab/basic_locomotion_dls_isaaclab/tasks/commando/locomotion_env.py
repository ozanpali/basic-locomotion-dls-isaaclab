# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from matplotlib import scale

import gymnasium as gym
import torch

import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
import isaaclab.utils.math as math_utils
from isaaclab.assets import Articulation, ArticulationCfg
from isaaclab.envs import DirectRLEnv, DirectRLEnvCfg
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensor, ContactSensorCfg, RayCaster, RayCasterCfg, patterns, Imu
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
#from basic_locomotion_dls_isaaclab.tasks.custom_events import scale_joint_torque

try:
    from ..custom_events import scale_joint_torque
except Exception:
    from basic_locomotion_dls_isaaclab.tasks.custom_events import scale_joint_torque


from .aliengo_env_cfg import AliengoFlatEnvCfg, AliengoRoughBlindEnvCfg, AliengoRoughVisionEnvCfg
from .go2_env_cfg import Go2FlatEnvCfg, Go2RoughVisionEnvCfg, Go2RoughBlindEnvCfg
from .hyqreal_env_cfg import HyQRealFlatEnvCfg, HyQRealRoughVisionEnvCfg, HyQRealRoughBlindEnvCfg
from .b2_env_cfg import B2FlatEnvCfg, B2RoughVisionEnvCfg, B2RoughBlindEnvCfg

from basic_locomotion_dls_isaaclab.tasks.supervised_learning_networks import SimpleNN

class LocomotionEnv(DirectRLEnv):
    cfg: AliengoFlatEnvCfg | AliengoRoughBlindEnvCfg | AliengoRoughVisionEnvCfg | Go2FlatEnvCfg | Go2RoughVisionEnvCfg | Go2RoughBlindEnvCfg | HyQRealFlatEnvCfg | HyQRealRoughVisionEnvCfg | HyQRealRoughBlindEnvCfg

    def __init__(self, cfg: AliengoFlatEnvCfg | AliengoRoughBlindEnvCfg | AliengoRoughVisionEnvCfg | Go2FlatEnvCfg | Go2RoughVisionEnvCfg | Go2RoughBlindEnvCfg | HyQRealFlatEnvCfg | HyQRealRoughVisionEnvCfg | HyQRealRoughBlindEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        # Joint position command (deviation from default joint positions)
        self._actions = torch.zeros(self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device)
        self._previous_actions = torch.zeros(
            self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device
        )
        self._previous_previous_actions = torch.zeros(
            self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device
        )

        # X/Y linear velocity and yaw angular velocity commands
        self._commands = torch.zeros(self.num_envs, 3, device=self.device)

        # Swing peak
        self._swing_peak = torch.tensor([0.0, 0.0, 0.0, 0.0], device=self.device).repeat(self.num_envs,1)
        self._swing_peak_periodic = torch.tensor([0.0, 0.0, 0.0, 0.0], device=self.device).repeat(self.num_envs,1)
        
        # Desired Hip Offset
        self._desired_hip_offset = torch.tensor([-self.cfg.desired_hip_offset, self.cfg.desired_hip_offset, -self.cfg.desired_hip_offset, self.cfg.desired_hip_offset], device=self.device)
        
        # Periodic gait
        self._step_freq = torch.tensor(self.cfg.desired_step_freq, device=self.device)
        self._duty_factor = torch.tensor(self.cfg.desired_duty_factor, device=self.device)
        self._phase_offset = torch.tensor(self.cfg.desired_phase_offset, device=self.device).repeat(self.num_envs,1)
        self._phase_signal = self._phase_offset.clone()# + self.step_dt * self._step_freq * torch.rand(self.num_envs, 1, device=self.device)*10.
        self._phase_signal = self._phase_signal % 1.0


        # Observation history
        self._observation_history = torch.zeros(self.num_envs, cfg.history_length, cfg.single_observation_space, device=self.device)

        # Per-leg, per-joint torque scaling activation mask [num_envs, 4 legs, 3 joints]
        # legs: [FL, FR, RL, RR]; joints: [hip, thigh, calf]
        # Note: _setup_scene may have already created and populated this via custom_events.
        if not hasattr(self, "_torque_scaled_mask_per_leg_joint"):
            self._torque_scaled_mask_per_leg_joint = torch.zeros(
                self.num_envs, 4, 3, dtype=torch.float, device=self.device
            )
            """# Informative init print: per-leg (FL, FR, RL, RR) x per-joint (hip, thigh, calf) torque scaling mask
            try:
                #shape = tuple(self._torque_scaled_mask_per_leg_joint.shape)
                #print(f"[init] _torque_scaled_mask_per_leg_joint allocated with shape={shape} (num_envs={self.num_envs}, legs=4, joints=3), device={self.device}")
            except Exception:
                pass"""

        ############################## LOOK HERE ##############################
        # Per-env failure type persisted across the episode (0: none, 1: FL, 2: FR, 3: RL, 4: RR)
        if not hasattr(self, "_failure_type"):
            self._failure_type = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)

        # RMA
        if(cfg.use_rma == True):
            self._rma_network = SimpleNN(cfg.rma_observation_space, cfg.rma_output_space)
            self._rma_network.to(self.device)
            self._observation_history_rma = torch.zeros(self.num_envs, cfg.history_length, cfg.single_rma_observation_space, device=self.device)
            if self.cfg.observation_noise_model:
                self._observation_noise_model_rma: NoiseModel = self.cfg.observation_noise_model.class_type(
                    self.cfg.observation_noise_model, num_envs=self.num_envs, device=self.device
                )

        # Learned State Estimator
        if(cfg.use_cuncurrent_state_est == True):
            self._cuncurrent_state_est_network = SimpleNN(cfg.cuncurrent_state_est_observation_space, cfg.cuncurrent_state_est_output_space)
            self._cuncurrent_state_est_network.to(self.device)
            self._observation_history_cuncurrent_state_est = torch.zeros(self.num_envs, cfg.history_length, cfg.single_cuncurrent_state_est_observation_space, device=self.device)
            if self.cfg.observation_noise_model:
                self._observation_noise_model_cuncurrent_state_est: NoiseModel = self.cfg.observation_noise_model.class_type(
                    self.cfg.observation_noise_model, num_envs=self.num_envs, device=self.device
                )

        # Logging
        self._episode_sums = {
            key: torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            for key in [
                "track_height_exp",
                "track_lin_vel_xy_exp",
                "track_lin_vel_z_l2",
                "track_orientation_l2",
                "track_ang_vel_xy_l2",
                "track_ang_vel_z_exp",

                "undesired_contacts",
                "action_rate_l2",
                "action_smoothness_l2",
                
                "joints_hip_pos_l2",
                "joints_thigh_pos_l2",
                "joints_calf_pos_l2",
                "joints_acc_l2",
                "joints_torques_l2",
                "joints_energy_l1",
                
                "feet_air_time",
                "feet_height_clearance_periodic",
                "feet_height_clearance",
                "feet_height_clearance_mujoco_periodic",
                "feet_height_clearance_mujoco",
                "feet_slide",
                "feet_contact_suggestion",
                "feet_to_base_distance_l2",
                "feet_to_hip_distance_l2",
                "feet_vertical_surface_contacts",

                "commando_base_orientation",
                "commando_undesired_contacts",
                "commando_feet_air_time",
                "commando_feet_slide",
                "commando_feet_to_hip_distance",
                "commando_joints_torques_l2",
                "commando_joints_acc_l2",
                "commando_joints_energy_l1",
                "commando_joints_hip_pos_l2",
                "commando_joints_thigh_pos_l2",
                "commando_joints_calf_pos_l2",
                "commando_action_rate_l2",
                "commando_action_smoothness_l2",
                "commando_track_height_exp",

                "feet_air_time_FL_failure",
                "feet_air_time_FR_failure",
                "feet_air_time_RL_failure",
                "feet_air_time_RR_failure",
            ]
        }
        # Get specific body indices
        self._base_id, _ = self._contact_sensor.find_bodies("base")
        self._feet_ids, _ = self._contact_sensor.find_bodies(".*foot")
        self._hip_ids, _ = self._contact_sensor.find_bodies(".*hip")
        self._thigh_ids, _ = self._contact_sensor.find_bodies(".*thigh")
        self._undesired_contact_body_ids = self._base_id + self._hip_ids + self._thigh_ids

        #commando specific undesired contact body ids(front hip thigh)
        self._commando_undesired_contact_body_ids = self._hip_ids[:2]

        self._feet_ids_robot, _ = self._robot .find_bodies(".*foot")
        self._hip_ids_robot, _ = self._robot.find_bodies(".*hip")


    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self._robot
        self._contact_sensor = ContactSensor(self.cfg.contact_sensor)
        self.scene.sensors["contact_sensor"] = self._contact_sensor

        # we add a height scanner for perceptive locomotion
        self._height_scanner = RayCaster(self.cfg.height_scanner)
        self.scene.sensors["height_scanner"] = self._height_scanner

        # we add an imu
        self._imu = Imu(self.cfg.imu)
        self.scene.sensors["imu"] = self._imu

        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        
        # clone, filter, and replicate
        self.scene.clone_environments(copy_from_source=False)
        self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        
        # add lights
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)


    def _pre_physics_step(self, actions: torch.Tensor):
        self._previous_previous_actions = self._previous_actions.clone()
        self._previous_actions = self._actions.clone()
        self._actions = actions.clone()
        
        # Clip the action
        self._actions = torch.clamp(self._actions, -self.cfg.desired_clip_actions, self.cfg.desired_clip_actions)

        # Filter the action
        if(self.cfg.use_filter_actions):
            alpha = 0.8
            temp = alpha * self._actions + (1 - alpha) * self._previous_actions
            self._processed_actions = self.cfg.action_scale * temp + self._robot.data.default_joint_pos
        else:
            self._processed_actions = self.cfg.action_scale * self._actions + self._robot.data.default_joint_pos


    def _apply_action(self):
        self._robot.set_joint_position_target(self._processed_actions)




    def _get_observations(self) -> dict:
        
        # This is a custom event, to be moved in custom_events.py
        self._get_new_random_commands()


        # Observation --------------------------------------------------------------------------------------
        clock_data = None
        if(self.cfg.use_clock_signal):
            clock_data = torch.vstack([self._phase_signal[:,0], self._phase_signal[:,1], self._phase_signal[:,2], self._phase_signal[:,3]]).T
            # all the envs that are not moving, we put -1
            should_move = torch.norm(self._commands[:, :3], dim=1) > 0.01
            clock_data[:, :] = clock_data[:, :]*should_move.unsqueeze(1).expand(-1, 4) + -1.0* ~should_move.unsqueeze(1).expand(-1, 4)
            

        # Choosing the main source of observation
        if(self.cfg.use_cuncurrent_state_est):
            # If Cuncurrent SE/Learned State Estimator, we predict linear and angular vel from IMU
            velocity_b = self._get_cuncurrent_state_estimation(clock_data)
            angular_velocity_b = self._imu.data.ang_vel_b
            projected_gravity_b = self._imu.data.projected_gravity_b
        elif(self.cfg.use_imu):
            # Using directly the IMU
            velocity_b = self._imu.data.lin_acc_b
            angular_velocity_b = self._imu.data.ang_vel_b
            projected_gravity_b = self._imu.data.projected_gravity_b
        else:
            #Using a model-based state estimation
            velocity_b = self._robot.data.root_lin_vel_b
            angular_velocity_b = self._robot.data.root_ang_vel_b
            projected_gravity_b = self._robot.data.projected_gravity_b
        
        
        # Standard Obs for the Actor/Critic
        obs = torch.cat(
            [
                tensor
                for tensor in (
                    velocity_b,
                    angular_velocity_b,
                    projected_gravity_b,
                    self._commands,
                    self._robot.data.joint_pos - self._robot.data.default_joint_pos,
                    self._robot.data.joint_vel,
                    self._actions,
                    clock_data,
                )
                if tensor is not None
            ],
            dim=-1,
        )
        if(self.cfg.use_observation_history):
            #the bottom element is the newest observation!!
            self._observation_history = torch.cat((self._observation_history[:,1:,:], obs.unsqueeze(1)), dim=1)
            obs = torch.flatten(self._observation_history, start_dim=1)


        # Add heightmap data to obs if needed
        if isinstance(self.cfg, AliengoRoughVisionEnvCfg) or isinstance(self.cfg, Go2RoughVisionEnvCfg) or isinstance(self.cfg, HyQRealRoughVisionEnvCfg) or isinstance(self.cfg, B2RoughVisionEnvCfg):
            height_data = (
                self._height_scanner.data.pos_w[:, 2].unsqueeze(1) - self._height_scanner.data.ray_hits_w[..., 2] - 0.5
            )
            height_data = torch.nan_to_num(height_data, nan=0.0, posinf=1.0, neginf=-1.0)
            height_data = height_data.clip(-1.0, 1.0)
            obs = torch.cat((obs, height_data), dim=-1)      


        # If RMA, we add some other predicted obs
        if(self.cfg.use_rma):
            # Predict the RMA observation
            obs_rma = self._get_rma(clock_data)
            obs = torch.cat((obs, obs_rma), dim=-1)


        # Append only the per-leg torque scaling flags (0/1) to the policy observation
        # Shape: [num_envs, 4]; order: [FL, FR, RL, RR]
        leg_any_scaled = (self._torque_scaled_mask_per_leg_joint.max(dim=2).values > 0.0).float()
        #print("Leg any scaled fed to observations:", leg_any_scaled.tolist())
        obs = torch.cat((obs, leg_any_scaled), dim=-1)

        
        # Append back-failed flag as one-hot to the observation instead of per-leg flags
        # back_failed_flag: 1 if any of RL/RR legs are torque-scaled, else 0
        # One-hot shape: [num_envs, 2] -> [no_back_fail, back_fail]
        # Directly append failure type one-hot (size 3): 0 = none, 1 = rear failure (RL & RR), 2 = front-left failure.
        # _failure_type is guaranteed by __init__ / _reset_idx; assert for clarity.
        """assert hasattr(self, "_failure_type"), "_failure_type must be initialized in __init__ before observations are gathered."
        #failure_type_clamped = torch.clamp(self._failure_type, 0, 2)
        failure_type_onehot = torch.nn.functional.one_hot(self._failure_type, num_classes=6).to(dtype=obs.dtype, device=obs.device)
        obs = torch.cat((obs, failure_type_onehot), dim=-1)"""
        #print("Failure type onehot added to obs:", failure_type_onehot.cpu().numpy())  #Failure type onehot added to obs: [0. 0. 1.] for front-left failure
        #print("Back-failed onehot added to obs:", back_failed_onehot[0].cpu().numpy())  #Back-failed onehot added to obs: [0. 1.]


        # Final observations dictionary
        observations = {"policy": obs}    
        

        # Critic OBS could be different if needed
        if(self.cfg.use_asymmetric_ppo):
            obs_critic = self._get_privileged_observation()
            observations["critic"] = torch.cat((obs, obs_critic), dim=-1)
        # ------------------------------------------------------------------------------------------


        # AMP related observation if used
        if(self.cfg.use_amp):
            obs_amp = torch.cat(
                [
                    tensor
                    for tensor in (
                        #self._robot.data.root_quat_w,
                        self._robot.data.joint_pos,
                        self._robot.data.joint_vel,
                        self._robot.data.root_lin_vel_b,
                        # self._robot.data.root_ang_vel_b,
                    )
                    if tensor is not None
                ],
                dim=-1,
            )
            observations["amp"] = obs_amp

        #print("Observation: ", observations["policy"][0].cpu().numpy())
        return observations


    def _get_rewards(self) -> torch.Tensor:

        # Create a binary per-leg mask (0/1) indicating whether ANY joint on the leg has torque scaling active
        # Shape: [num_envs, 4]; dtype: int (for clear logical use); cast to float when multiplying with rewards
        leg_any_scaled_int = (self._torque_scaled_mask_per_leg_joint.max(dim=2).values > 0.0).int()
        # Compute a per-env gating factor that is 1.0 only when no leg is failed (no scaling active), else 0.0
        # Vectorized for GPU: product over legs of (1 - flag)
        gating_factor = (1.0 - leg_any_scaled_int.float()).prod(dim=1)  # torch.float, shape [num_envs]
        # Explicit variable for "4-leg" mode: True when there is NO leg failure (all four legs active)
        four_leg_active_bool = (leg_any_scaled_int.sum(dim=1) == 0)  # torch.bool tensor shape [num_envs]
        four_leg_active = four_leg_active_bool.float()  # float version for reward scaling if needed
        # NOTE: gating_factor == four_leg_active; kept both for clarity until refactor
        # Front-left (FL) leg failure active (first index is 1)
        fl_failed_bool = (leg_any_scaled_int[:, 0] > 0)  # torch.bool tensor shape [num_envs]
        fl_failed = fl_failed_bool.float()  # float representation if needed for reward scaling
        # Front-right (FR) leg failure active (second index)
        fr_failed_bool = (leg_any_scaled_int[:, 1] > 0)  # torch.bool, shape [num_envs]
        fr_failed = fr_failed_bool.float()  # torch.float, shape [num_envs]
        # Rear-left (RL) leg failure active (third index)
        rl_failed_bool = (leg_any_scaled_int[:, 2] > 0)  # torch.bool, shape [num_envs]
        rl_failed = rl_failed_bool.float()  # torch.float, shape [num_envs]
        # Rear-right (RR) leg failure active (fourth index)
        rr_failed_bool = (leg_any_scaled_int[:, 3] > 0)  # torch.bool, shape [num_envs]
        rr_failed = rr_failed_bool.float()  # torch.float, shape [num_envs]

        # "Only" flags: true when this leg is failed AND all other legs are NOT failed
        # These are useful to detect mutually-exclusive single-leg failure cases.
        # Each *_only_failed_bool is a torch.bool tensor with shape [num_envs].
        try:
            fl_only_failed_bool = fl_failed_bool & ~(fr_failed_bool | rl_failed_bool | rr_failed_bool)  # torch.bool, shape [num_envs]
            fr_only_failed_bool = fr_failed_bool & ~(fl_failed_bool | rl_failed_bool | rr_failed_bool)  # torch.bool, shape [num_envs]
            rl_only_failed_bool = rl_failed_bool & ~(fl_failed_bool | fr_failed_bool | rr_failed_bool)  # torch.bool, shape [num_envs]
            rr_only_failed_bool = rr_failed_bool & ~(fl_failed_bool | fr_failed_bool | rl_failed_bool)  # torch.bool, shape [num_envs]
        except Exception:
            # Fallback in case tensors are not boolean or shapes mismatch; coerce and compute safely
            fl_only_failed_bool = (leg_any_scaled_int[:, 0] > 0) & (
                (leg_any_scaled_int[:, 1] == 0) & (leg_any_scaled_int[:, 2] == 0) & (leg_any_scaled_int[:, 3] == 0)
            )  # torch.bool, shape [num_envs]
            fr_only_failed_bool = (leg_any_scaled_int[:, 1] > 0) & (
                (leg_any_scaled_int[:, 0] == 0) & (leg_any_scaled_int[:, 2] == 0) & (leg_any_scaled_int[:, 3] == 0)
            )  # torch.bool, shape [num_envs]
            rl_only_failed_bool = (leg_any_scaled_int[:, 2] > 0) & (
                (leg_any_scaled_int[:, 0] == 0) & (leg_any_scaled_int[:, 1] == 0) & (leg_any_scaled_int[:, 3] == 0)
            )  # torch.bool, shape [num_envs]
            rr_only_failed_bool = (leg_any_scaled_int[:, 3] > 0) & (
                (leg_any_scaled_int[:, 0] == 0) & (leg_any_scaled_int[:, 1] == 0) & (leg_any_scaled_int[:, 2] == 0)
            )  # torch.bool, shape [num_envs]

        # Float versions for reward scaling/aggregation
        # Each *_only_failed is a torch.float tensor with shape [num_envs].
        fl_only_failed = fl_only_failed_bool.float()  # torch.float, shape [num_envs]
        fr_only_failed = fr_only_failed_bool.float()  # torch.float, shape [num_envs]
        rl_only_failed = rl_only_failed_bool.float()  # torch.float, shape [num_envs]
        rr_only_failed = rr_only_failed_bool.float()  # torch.float, shape [num_envs]

        # --- Per-environment reward case id (6 cases) ---
        # Cases (int):
        # 0 = all four legs active (no scaling)
        # 1 = FL-only failed
        # 2 = FR-only failed
        # 3 = RL-only failed
        # 4 = RR-only failed
        # 5 = both rear legs failed (commando)
        case_id = torch.full((self.num_envs,), 0, dtype=torch.long, device=self.device)
        case_id[four_leg_active_bool] = 0
        case_id[fl_only_failed_bool] = 1
        case_id[fr_only_failed_bool] = 2
        case_id[rl_only_failed_bool] = 3
        case_id[rr_only_failed_bool] = 4
        # rear-both (commando) takes precedence over single-leg flags where both rear legs are scaled
        rear_both_mask = (leg_any_scaled_int[:, 2] > 0) & (leg_any_scaled_int[:, 3] > 0)
        case_id[rear_both_mask] = 5
        # store for debugging/inspection
        self._reward_case = case_id
        # Flag that is 1.0 only if BOTH rear legs (RL and RR) are failed (torque-scaled), else 0.0
        # Rear leg indices are 2 (RL) and 3 (RR) in leg_any_scaled_int columns [FL, FR, RL, RR]
        back_failed_flag = ((leg_any_scaled_int[:, 2] > 0) & (leg_any_scaled_int[:, 3] > 0)).float()  # torch.float, shape [num_envs]
        #print("Back-failed flag:", back_failed_flag.tolist())  # Back-failed flag: [0. 1.]
        #print("RL leg scaled:", leg_any_scaled_int[:, 2].tolist())  # RL leg scaled: [0, 1, 0, ...]
        #print("RR leg scaled:", leg_any_scaled_int[:, 3].tolist())  # RR leg scaled: [0, 1, 0, ...]
        # track_height
        height_data_scanner = self._height_scanner.data.ray_hits_w[..., 2]
        height_data_scanner = torch.nan_to_num(height_data_scanner, nan=0.0, posinf=1.0, neginf=-1.0)
        height_data_scanner = torch.clip(height_data_scanner, min=-5, max=5) # Handle inf values
        mean_height_ray = torch.mean(height_data_scanner, dim=1)

        height_error = torch.square(self.cfg.desired_base_height + mean_height_ray - self._robot.data.root_state_w[:, 2])
        height_error_mapped = torch.exp(-height_error / 0.01)
        

        # --- Front-hip height above local terrain under each front hip ---
        # Use the ray hits (x,y,z) produced by the height scanner and find the closest
        # ray hit in XY to each front hip. This gives a per-front-hip ground z estimate
        # so we can compute hip_z_world - ground_z.
        # Note: height_data_scanner is the z component of ray_hits_w and has been
        # cleaned (nan -> 0, clipped) above.
        # Prefer per-hip nearest-ray ground lookup when scanner data is available and well-formed.
        rays = getattr(self._height_scanner.data, "ray_hits_w", None)
        if (
            rays is not None
            and isinstance(rays, torch.Tensor)
            and rays.numel() > 0
            and rays.shape[-1] >= 2
            and rays.shape[1] > 0
        ):
            rays_xy = rays[..., :2]  # [N, n_rays, 2]
            # hip positions in world XY for front hips (FL, FR)
            hip_xy = self._robot.data.body_pos_w[:, self._hip_ids_robot[:2], :2]  # [N, 2, 2]

            # Compute squared distances between each front hip and all rays: [N, 2, n_rays]
            d2 = torch.sum((hip_xy.unsqueeze(2) - rays_xy.unsqueeze(1)) ** 2, dim=-1)
            nearest_idx = torch.argmin(d2, dim=2)  # [N, 2]
            nearest_idx = nearest_idx.long()

            # Gather ground z for the nearest rays (height_data_scanner is [N, n_rays])
            ground_z = height_data_scanner.gather(1, nearest_idx)  # [N, 2]

            hip_z_world = self._robot.data.body_pos_w[:, self._hip_ids_robot[:2], 2]  # [N, 2]
            front_hip_height_above_ground = hip_z_world - ground_z
            # Clean potential numerical issues
            front_hip_height_above_ground = torch.nan_to_num(
                front_hip_height_above_ground, nan=0.0, posinf=5.0, neginf=-5.0
            )
            front_hip_height_above_ground_mean = torch.mean(front_hip_height_above_ground, dim=1)
        else:
            # Fallback: if scanner data not available or malformed, fall back to world z of hips minus mean ray
            hip_z_world = self._robot.data.body_pos_w[:, self._hip_ids_robot[:2], 2]
            front_hip_height_above_ground = hip_z_world - mean_height_ray.unsqueeze(1)
            front_hip_height_above_ground = torch.nan_to_num(
                front_hip_height_above_ground, nan=0.0, posinf=5.0, neginf=-5.0
            )
            front_hip_height_above_ground_mean = torch.mean(front_hip_height_above_ground, dim=1)

        # Compute front-hip height error (desired - actual above-ground) and map it like base height
        # Compute front-hip height error (desired - actual above-ground) and map it like base height
        if hasattr(self.cfg, "desired_front_hip_height"):
            desired_front = self.cfg.desired_front_hip_height
        else:
            desired_front = self.cfg.desired_base_height
        front_hip_height_error = torch.square(desired_front - front_hip_height_above_ground_mean)
        commando_front_hip_height_error_mapped = torch.exp(-front_hip_height_error / 0.01)
        

        # linear velocity tracking
        lin_vel_error = torch.sum(torch.square(self._commands[:, :2] - self._robot.data.root_lin_vel_b[:, :2]), dim=1)
        lin_vel_error_mapped = torch.exp(-lin_vel_error / 0.25)
        

        # z velocity tracking
        z_vel_error = torch.square(self._robot.data.root_lin_vel_b[:, 2])


        # flat orientation
        #base_orientation = torch.sum(torch.square(self._robot.data.projected_gravity_b[:, :2]), dim=1)


        # terrain orientation
        height_map_resolution = self._height_scanner.cfg.pattern_cfg.resolution
        height_map_x_points = int(round(self._height_scanner.cfg.pattern_cfg.size[0] / height_map_resolution)) + 1
        height_map_y_points = int(round(self._height_scanner.cfg.pattern_cfg.size[1] / height_map_resolution))
        distance_between_front_and_back = (height_map_x_points/2)* height_map_resolution

        cols_back = torch.arange(0, height_data_scanner.shape[1], height_map_x_points).unsqueeze(1) + torch.arange(int(height_map_x_points/2))
        cols_back = cols_back.flatten().to(height_data_scanner.device)
        selected_height_data_back = height_data_scanner[:, cols_back]

        cols_front = torch.arange(int(height_map_x_points/2), height_data_scanner.shape[1], height_map_x_points).unsqueeze(1) + torch.arange(int(height_map_x_points/2))
        cols_front = cols_front.flatten().to(height_data_scanner.device)
        selected_height_data_front = height_data_scanner[:, cols_front]

        mean_height_ray_front = torch.mean(selected_height_data_front, dim=1)
        mean_height_ray_back = torch.mean(selected_height_data_back, dim=1)
        delta_z = mean_height_ray_front - mean_height_ray_back
        delta_s = torch.tensor(distance_between_front_and_back).to(self.device)
        terrain_pitch = -torch.atan2(delta_z, delta_s)
        #terrain_pitch = torch.atan2(torch.sin(terrain_pitch), torch.cos(terrain_pitch))

        cols_right = torch.arange(0, height_data_scanner.shape[1]//2, 1).unsqueeze(1) 
        cols_right = cols_right.flatten().to(height_data_scanner.device)
        selected_height_data_right = height_data_scanner[:, cols_right]

        cols_left = torch.arange(0, height_data_scanner.shape[1]//2, 1).unsqueeze(1) + height_data_scanner.shape[1]//2
        cols_left = cols_left.flatten().to(height_data_scanner.device)
        selected_height_data_left = height_data_scanner[:, cols_left]

        delta_z_roll = torch.mean(selected_height_data_left, dim=1) - torch.mean(selected_height_data_right, dim=1)
        delta_s_roll = torch.tensor((height_map_y_points-1)* height_map_resolution).to(self.device)
        terrain_roll = torch.atan2(delta_z_roll, delta_s_roll)
        # TODO check if we need roll in base frame
        

        root_roll_w, root_pitch_w, _ = math_utils.euler_xyz_from_quat(self._robot.data.root_quat_w)
        root_roll_w = torch.atan2(torch.sin(root_roll_w), torch.cos(root_roll_w))
        root_pitch_w = torch.atan2(torch.sin(root_pitch_w), torch.cos(root_pitch_w))
        
        base_orientation =  torch.square(terrain_pitch - root_pitch_w)# + torch.square(terrain_roll - root_roll_w)


        # commando orientation (front roll only)
        commando_base_orientation = torch.square(terrain_roll - root_roll_w)

        # angular velocity x/y tracking
        ang_vel_error = torch.sum(torch.square(self._robot.data.root_ang_vel_b[:, :2]), dim=1)


        # yaw rate tracking
        yaw_rate_error = torch.square(self._commands[:, 2] - self._robot.data.root_ang_vel_b[:, 2])
        yaw_rate_error_mapped = torch.exp(-yaw_rate_error / 0.25)
        
        
        # action rate
        action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)
        action_smoothness = torch.sum(torch.square(self._actions - 2*self._previous_actions + self._previous_previous_actions), dim=1)
        
        
        # Commando (front-only) action metrics: consider only FL and FR joints across hip/thigh/calf
        # Joint ordering: hips[0:4]=[FL,FR,RL,RR], thighs[4:8]=[FL,FR,RL,RR], calves[8:12]=[FL,FR,RL,RR]
        front_action_indices = [0, 1, 4, 5, 8, 9]
        commando_action_rate = torch.sum(
            torch.square(self._actions[:, front_action_indices] - self._previous_actions[:, front_action_indices]), dim=1
        )
        commando_action_smoothness = torch.sum(
            torch.square(
                self._actions[:, front_action_indices]
                - 2 * self._previous_actions[:, front_action_indices]
                + self._previous_previous_actions[:, front_action_indices]
            ),
            dim=1,
        )
        
        
        # undersired contacts
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        is_contact = (
            torch.max(torch.norm(net_contact_forces[:, :, self._undesired_contact_body_ids], dim=-1), dim=1)[0] > 1.0
        )
        contacts = torch.sum(is_contact, dim=1)


        # commando undersired contacts (front hips)
        commando_is_contact = (
            torch.max(torch.norm(net_contact_forces[:, :, self._commando_undesired_contact_body_ids], dim=-1), dim=1)[0] > 1.0
        )
        commando_contacts = torch.sum(commando_is_contact, dim=1)
        

        # joint acceleration
        joints_accel = torch.sum(torch.square(self._robot.data.joint_acc), dim=1)

        
        # commando joint acceleration (front legs only across all joint types)
        commando_front_only_accel = torch.cat(
            [
                self._robot.data.joint_acc[:, 0:2],   # hips FL, FR
                self._robot.data.joint_acc[:, 4:6],   # thighs FL, FR
                self._robot.data.joint_acc[:, 8:10],  # calves FL, FR
            ],
            dim=1,
        )
        commando_joints_accel = torch.sum(torch.square(commando_front_only_accel), dim=1)

        
        # joint torques
        joints_torques = torch.sum(torch.square(self._robot.data.applied_torque), dim=1)

        
        # commando joint torques (front legs only across all joint types)
        # Joint layout is grouped by type across legs:
        #   hips:   indices [0:4]   -> [FL, FR, RL, RR]
        #   thighs: indices [4:8]   -> [FL, FR, RL, RR]
        #   calves: indices [8:12]  -> [FL, FR, RL, RR]
        # For front-only, select FL, FR from each group and stack them: [0:2], [4:6], [8:10]
        commando_front_only_torques = torch.cat(
            [
                self._robot.data.applied_torque[:, 0:2],   # hips FL, FR
                self._robot.data.applied_torque[:, 4:6],   # thighs FL, FR
                self._robot.data.applied_torque[:, 8:10],  # calves FL, FR
            ],
            dim=1,
        )
        commando_joints_torques = torch.sum(torch.square(commando_front_only_torques), dim=1)
        

        # energy = torque * velocity
        joints_energy = torch.sum(torch.abs(self._robot.data.applied_torque * self._robot.data.joint_vel), dim=1)

        
        # commando joint energy (front legs only across all joint types)
        commando_front_only_joint_vel = torch.cat(
            [
                self._robot.data.joint_vel[:, 0:2],   # hips FL, FR
                self._robot.data.joint_vel[:, 4:6],   # thighs FL, FR
                self._robot.data.joint_vel[:, 8:10],  # calves FL, FR
            ],
            dim=1,
        )
        commando_joints_energy = torch.sum(torch.abs(commando_front_only_torques * commando_front_only_joint_vel), dim=1)
        
        
        # hip position
        hip_joints_position = self._robot.data.joint_pos[:,0:4]
        hip_joints_position_error = torch.square(hip_joints_position - self._robot.data.default_joint_pos[:,0:4])
        hip_joints_position_reward = torch.sum(hip_joints_position_error,dim=1)


        # commando hip position (exclude back hips RL and RR; use only front hips FL and FR -> indices 0 and 1)
        commando_hip_joints_position = self._robot.data.joint_pos[:, 0:2]
        commando_hip_joints_position_error = torch.square(
            commando_hip_joints_position - self._robot.data.default_joint_pos[:, 0:2]
        )
        commando_hip_joints_position_reward = torch.sum(commando_hip_joints_position_error, dim=1)


        # thigh position
        thigh_joints_position = self._robot.data.joint_pos[:,4:8]
        thigh_joints_position_error = torch.square(thigh_joints_position - self._robot.data.default_joint_pos[:,4:8])
        thigh_joints_position_reward = torch.sum(thigh_joints_position_error,dim=1)


        # commando thigh position (front-only: indices 4 and 5)
        commando_thigh_joints_position = self._robot.data.joint_pos[:, 4:6]
        commando_thigh_joints_position_error = torch.square(
            commando_thigh_joints_position - self._robot.data.default_joint_pos[:, 4:6]
        )
        #print("default_thigh:", self._robot.data.default_joint_pos[:, 4:6].cpu().numpy()) # default_thigh: [[0.9 0.9] [0.9 0.9]]
        commando_thigh_joints_position_reward = torch.sum(commando_thigh_joints_position_error, dim=1)


        # calf position
        calf_joints_position = self._robot.data.joint_pos[:,8:12]
        calf_joints_position_error = torch.square(calf_joints_position - self._robot.data.default_joint_pos[:,8:12])
        calf_joints_position_reward = torch.sum(calf_joints_position_error,dim=1)


        # commando calf position (front-only: indices 8 and 9)
        commando_calf_joints_position = self._robot.data.joint_pos[:, 8:10]
        commando_calf_joints_position_error = torch.square(
            commando_calf_joints_position - self._robot.data.default_joint_pos[:, 8:10]
        )
        commando_calf_joints_position_reward = torch.sum(commando_calf_joints_position_error, dim=1)


        # feet airtime
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        last_air_time = self._contact_sensor.data.last_air_time[:, self._feet_ids]
        feet_air_time = torch.sum((last_air_time - 0.5) * first_contact, dim=1) * (
            torch.norm(self._commands[:, :2], dim=1) > 0.1
        )


        # RL and RR feet failure airtime combined
        active_feet_excluding_RL_RR = [0, 1]
        commando_feet_air_time = torch.sum(
            (last_air_time[:, active_feet_excluding_RL_RR] - 0.5) * first_contact[:, active_feet_excluding_RL_RR], dim=1
        ) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)


        # FL feet failure airtime
        active_feet_excluding_FL = [1, 2, 3]
        feet_air_time_excluding_FL = torch.sum(
            (last_air_time[:, active_feet_excluding_FL] - 0.5) * first_contact[:, active_feet_excluding_FL], dim=1
        ) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)
        # Contact flags (reuse forces tensor). Threshold > 1.0 indicates contact.
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        fl_in_air = (~contacts_foot[:, 0]).float()
        fl_contact = contacts_foot[:, 0].float()
        fl_air_reward = 10.0 * fl_in_air
        fl_penalty = -10.0 * fl_contact
        feet_air_time_FL_failure = (feet_air_time_excluding_FL + fl_air_reward + fl_penalty)

        # FR feet failure airtime
        active_feet_excluding_FR = [0, 2, 3]
        feet_air_time_excluding_FR = torch.sum(
            (last_air_time[:, active_feet_excluding_FR] - 0.5) * first_contact[:, active_feet_excluding_FR], dim=1
        ) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)
        # Contact flags (reuse forces tensor). Threshold > 1.0 indicates contact.
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        fr_in_air = (~contacts_foot[:, 1]).float()
        fr_contact = contacts_foot[:, 1].float()
        fr_air_reward = 10.0 * fr_in_air
        fr_penalty = -10.0 * fr_contact
        feet_air_time_FR_failure = (feet_air_time_excluding_FR + fr_air_reward + fr_penalty)

        # RL feet failure airtime
        active_feet_excluding_RL = [0, 1, 3]
        feet_air_time_excluding_RL = torch.sum(
            (last_air_time[:, active_feet_excluding_RL] - 0.5) * first_contact[:, active_feet_excluding_RL], dim=1
        ) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)
        # Contact flags (reuse forces tensor). Threshold > 1.0 indicates contact.
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        rl_in_air = (~contacts_foot[:, 2]).float()
        rl_contact = contacts_foot[:, 2].float()
        rl_air_reward = 10.0 * rl_in_air
        rl_penalty = -10.0 * rl_contact
        feet_air_time_RL_failure = (feet_air_time_excluding_RL + rl_air_reward + rl_penalty)

        # RR feet failure airtime
        active_feet_excluding_RR = [0, 1, 2]
        feet_air_time_excluding_RR = torch.sum(
            (last_air_time[:, active_feet_excluding_RR] - 0.5) * first_contact[:, active_feet_excluding_RR], dim=1
        ) * (torch.norm(self._commands[:, :2], dim=1) > 0.1)
        # Contact flags (reuse forces tensor). Threshold > 1.0 indicates contact.
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        rr_in_air = (~contacts_foot[:, 3]).float()
        rr_contact = contacts_foot[:, 3].float()
        rr_air_reward = 10.0 * rr_in_air
        rr_penalty = -10.0 * rr_contact
        feet_air_time_RR_failure = (feet_air_time_excluding_RR + rr_air_reward + rr_penalty)


        # feet slide
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        body_vel = self._robot.data.body_lin_vel_w[:, self._feet_ids_robot, :2]
        feet_slide = torch.sum(body_vel.norm(dim=-1) * contacts_foot, dim=1)


        # commando feet slide (front-only: exclude RL and RR => use indices 0,1)
        contacts_foot_front = contacts_foot[:, 0:2]
        body_vel_front_norm = body_vel.norm(dim=-1)[:, 0:2]
        commando_feet_slide = torch.sum(body_vel_front_norm * contacts_foot_front, dim=1)


        # feet periodical contacts suggestion
        should_move = torch.norm(self._commands[:, :3], dim=1) > 0.01
        self._phase_signal += self.step_dt * self._step_freq
        self._phase_signal = self._phase_signal % 1.0
        contact_periodic_on = self._phase_signal < self._duty_factor
        feet_contact_suggestion = (torch.sum(contact_periodic_on*contacts_foot, dim=1) + \
                                   torch.sum(~contact_periodic_on*~contacts_foot, dim=1))*should_move/4.0
        feet_contact_suggestion += (torch.sum(contacts_foot, dim=1)*~should_move/4.0)
        

        # feet height clearance mujoco (done)
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        is_contact = (torch.max(torch.norm(net_contact_forces[:, :, self._feet_ids], dim=-1), dim=1)[0] > 1.0)

        self._swing_peak = torch.max(self._swing_peak, self._robot.data.body_pos_w[:, self._feet_ids_robot, 2].clone()) 
        self._swing_peak *= ~is_contact # reset if the foot is in contact
        target_height = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1)
        feet_height_clearance_mujoco = torch.sum(torch.square(self._swing_peak / target_height - 1.0) *  first_contact, dim=-1)
 
        # feet height clearance mujoco periodic(combinations for swing peak location & feet_z_target_error)
        self._swing_peak_periodic = torch.max(self._swing_peak_periodic, self._robot.data.body_pos_w[:, self._feet_ids_robot, 2].clone())
        self._swing_peak_periodic *= ~contact_periodic_on # reset if the foot is in contact periodic phase
        feet_z_target_error_mujoco = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._swing_peak_periodic #self._robot.data.body_pos_w[:, self._feet_ids_robot, 2]
        #feet_z_target_error_mujoco = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._robot.data.body_pos_w[:, self._feet_ids_robot, 2]
        feet_z_target_error_mujoco = torch.clamp(feet_z_target_error_mujoco, min=.0, max=self.cfg.desired_feet_height)
        feet_height_clearance_mujoco_periodic_FL = torch.exp(-feet_z_target_error_mujoco[:,0]/ 0.01) * should_move * ~contact_periodic_on[:,0] #first_contact[:,0]
        feet_height_clearance_mujoco_periodic_FR = torch.exp(-feet_z_target_error_mujoco[:,1]/ 0.01) * should_move * ~contact_periodic_on[:,1] #first_contact[:,1]
        feet_height_clearance_mujoco_periodic_RL = torch.exp(-feet_z_target_error_mujoco[:,2]/ 0.01) * should_move * ~contact_periodic_on[:,2] #first_contact[:,2]
        feet_height_clearance_mujoco_periodic_RR = torch.exp(-feet_z_target_error_mujoco[:,3]/ 0.01) * should_move * ~contact_periodic_on[:,3] #first_contact[:,3]
        feet_height_clearance_mujoco_periodic = feet_height_clearance_mujoco_periodic_FL + feet_height_clearance_mujoco_periodic_FR
        feet_height_clearance_mujoco_periodic += feet_height_clearance_mujoco_periodic_RL + feet_height_clearance_mujoco_periodic_RR


        # feet height clearance periodic
        feet_z_target_error = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._swing_peak_periodic #self._robot.data.body_pos_w[:, self._feet_ids_robot, 2]
        feet_z_target_error = torch.clamp(feet_z_target_error, min=.0, max=self.cfg.desired_feet_height)
 
        feet_height_clearance_periodic_FL = torch.exp(-feet_z_target_error[:,0]/ 0.01) * should_move * ~contact_periodic_on[:,0]
        feet_height_clearance_periodic_FR = torch.exp(-feet_z_target_error[:,1]/ 0.01) * should_move * ~contact_periodic_on[:,1]
        feet_height_clearance_periodic_RL = torch.exp(-feet_z_target_error[:,2]/ 0.01) * should_move * ~contact_periodic_on[:,2]
        feet_height_clearance_periodic_RR = torch.exp(-feet_z_target_error[:,3]/ 0.01) * should_move * ~contact_periodic_on[:,3]
        feet_height_clearance_periodic = feet_height_clearance_periodic_FL + feet_height_clearance_periodic_FR
        feet_height_clearance_periodic += feet_height_clearance_periodic_RL + feet_height_clearance_periodic_RR


        # feet height clearance standard
        foot_velocity_tanh = torch.tanh(2.0 * torch.norm(self._robot.data.body_lin_vel_w[:, self._feet_ids_robot, :2], dim=2))
        feet_height_clearance = torch.exp(-torch.sum(feet_z_target_error * foot_velocity_tanh, dim=1)/ 0.01) * should_move


        # feet to com distance
        feet_to_base_distance_x = torch.square(torch.mean(self._robot.data.body_pos_w[:, self._feet_ids_robot, 0], dim=1) - self._robot.data.root_state_w[:, 0])
        feet_to_base_distance_y = torch.square(torch.mean(self._robot.data.body_pos_w[:, self._feet_ids_robot, 1], dim=1) - self._robot.data.root_state_w[:, 1])
        feet_to_base_distance = -torch.sqrt(feet_to_base_distance_x + feet_to_base_distance_y)


        # feet to hip distance
        ROT_W2H = math_utils.matrix_from_quat(math_utils.yaw_quat(self._robot.data.root_quat_w))
        feet_to_base_w = self._robot.data.body_pos_w[:, self._feet_ids_robot, :3] - self._robot.data.root_state_w[:, :3].unsqueeze(1)
        feet_to_base_h = torch.matmul(ROT_W2H.transpose(1,2), feet_to_base_w.transpose(1, 2))
        
        hip_to_base_w = self._robot.data.body_pos_w[:, self._hip_ids_robot, :3] - self._robot.data.root_state_w[:, :3].unsqueeze(1)
        hip_to_base_h = torch.matmul(ROT_W2H.transpose(1,2), hip_to_base_w.transpose(1, 2))
        
        desired_hip_offset = self._desired_hip_offset
        # feet_to_hip_distance_x = torch.square(feet_to_base_h[:, 0] - hip_to_base_h[:, 0])
        # feet_to_hip_distance_y = torch.square(feet_to_base_h[:, 1] + desired_hip_offset.unsqueeze(0) - hip_to_base_h[:, 1])
        # feet_to_hip_distance = -torch.mean(torch.sqrt(feet_to_hip_distance_x + feet_to_hip_distance_y), dim=1)


        # up is original feet to hip distance reward, gpt(but modified to exclude failed legs from the average)
        # # Compute per-leg distances in hip frame, then masked average across legs
        delta_x = feet_to_base_h[:, 0] - hip_to_base_h[:, 0]
        delta_y = feet_to_base_h[:, 1] + desired_hip_offset.unsqueeze(0) - hip_to_base_h[:, 1]
        per_leg_dist = torch.sqrt(delta_x.pow(2) + delta_y.pow(2))  # [N,4]
        include_mask = (leg_any_scaled_int == 0)  # shape [N,4], bool
        #print("Include mask for feet to hip distance:", include_mask.int().tolist())
        # include_mask = torch.ones(self.num_envs, 4, dtype=torch.bool, device=self.device)
        # ft = self._failure_type.to(device=self.device)
        # fl_mask = ft == 2 #(ft >= 1) & (ft <= 7)
        # fr_mask = ft == 3 #(ft >= 8) & (ft <= 14)
        # rl_mask = ft == 4 #(ft >= 15) & (ft <= 21)
        # rr_mask = ft == 5 #(ft >= 22) & (ft <= 28)
        # include_mask[:, 0] &= ~fl_mask
        # include_mask[:, 1] &= ~fr_mask
        # include_mask[:, 2] &= ~rl_mask
        # include_mask[:, 3] &= ~rr_mask

        include_mask_f = include_mask.float()
        #print(include_mask_f)
        feet_to_hip_distance = -((per_leg_dist * include_mask_f).sum(dim=1) / include_mask_f.sum(dim=1).clamp(min=1.0))

        back_offset = torch.tensor([-0.01, -0.01, 0.0, 0.0], device=self.device)
        commando_desired_hip_offset = desired_hip_offset + back_offset
        # compute per-leg distances using the commando desired hip offset for the y component
        commando_delta_x = feet_to_base_h[:, 0] - hip_to_base_h[:, 0]
        commando_delta_y = feet_to_base_h[:, 1] + commando_desired_hip_offset.unsqueeze(0) - hip_to_base_h[:, 1]
        commando_per_leg_dist = torch.sqrt(commando_delta_x.pow(2) + commando_delta_y.pow(2))
        commando_front_dist_mean = commando_per_leg_dist[:, 0:2].mean(dim=1)
        commando_feet_to_hip_distance = -commando_front_dist_mean
         

        # Penalize feet hitting vertical surfaces  
        forces_z = torch.abs(self._contact_sensor.data.net_forces_w[:, self._feet_ids, 2])
        forces_xy = torch.linalg.norm(self._contact_sensor.data.net_forces_w[:, self._feet_ids, :2], dim=2)
        feet_vertical_surface_contacts = torch.any(forces_xy > 4 * forces_z, dim=1).float()
        feet_vertical_surface_contacts *= torch.clamp(-self._robot.data.projected_gravity_b[:, 2], 0, 0.7) / 0.7

        #print self._torque_scaled_mask_per_leg_joint.max(dim=2).values[:, 0]
        #print("Torque scaling mask FL leg joints:", leg_any_scaled_int[:, 0])
        #print("Torque scaling mask FR leg joints:", leg_any_scaled_int[:, 1])
        #print("Torque scaling mask RL leg joints:", leg_any_scaled_int[:, 2])
        #print("Torque scaling mask RR leg joints:", leg_any_scaled_int[:, 3])
        #print(" \n")
        
        
        #print Feet air time
        #print("Feet air time:", (feet_air_time * gating_factor * self.cfg.feet_air_time_reward_scale * self.step_dt).tolist())
        #print Feet air time excl FL
        #print("Feet air time excl FL:", (feet_air_time_FL_failure * self.cfg.feet_air_time_FL_failure_reward_scale * self.step_dt * (leg_any_scaled_int[:, 0].float())).tolist())

        #print("Torque scaling mask FR leg joints:", self._torque_scaled_mask_per_leg_joint.max(dim=2).values[:, 1])
        #print("Torque scaling mask RL leg joints:", self._torque_scaled_mask_per_leg_joint.max(dim=2).values[:, 2])
        #print("Torque scaling mask RR leg joints:", self._torque_scaled_mask_per_leg_joint.max(dim=2).values[:, 3])
        #print(" \n")

        # Toggle undesired contact rewards based on rear-leg failures:
        # If BOTH rear legs (RL and RR) are failed (torque-scaled), enable commando variant and disable non-commando.
        # Otherwise, enable non-commando and disable commando.
        back_failed_flag = ((leg_any_scaled_int[:, 2] > 0) & (leg_any_scaled_int[:, 3] > 0)).float()

        rewards = {
            "track_height_exp": height_error_mapped * self.cfg.height_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "track_lin_vel_xy_exp": lin_vel_error_mapped * self.cfg.lin_vel_reward_scale * self.step_dt,
            "track_lin_vel_z_l2": z_vel_error * self.cfg.z_vel_reward_scale * self.step_dt,
            "track_orientation_l2": base_orientation * self.cfg.orientation_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "track_ang_vel_xy_l2": ang_vel_error * self.cfg.ang_vel_reward_scale * self.step_dt,
            "track_ang_vel_z_exp": yaw_rate_error_mapped * self.cfg.yaw_rate_reward_scale * self.step_dt,

            "undesired_contacts": contacts * self.cfg.undersired_contact_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "action_rate_l2": action_rate * self.cfg.action_rate_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "action_smoothness_l2": action_smoothness * self.cfg.action_smoothness_reward_scale * self.step_dt * (1.0 - back_failed_flag),

            "joints_hip_pos_l2": hip_joints_position_reward * self.cfg.joints_hip_position_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "joints_thigh_pos_l2": thigh_joints_position_reward * self.cfg.joints_thigh_position_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "joints_calf_pos_l2": calf_joints_position_reward * self.cfg.joints_calf_position_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "joints_acc_l2": joints_accel * self.cfg.joints_accel_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "joints_torques_l2": joints_torques * self.cfg.joints_torque_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "joints_energy_l1": joints_energy * self.cfg.joints_energy_reward_scale * self.step_dt * (1.0 - back_failed_flag),

            "feet_air_time": feet_air_time * self.cfg.feet_air_time_reward_scale * self.step_dt * (1.0 - back_failed_flag) * gating_factor,
            
            "feet_height_clearance": feet_height_clearance * self.cfg.feet_height_clearance_reward_scale * self.step_dt * gating_factor,
            "feet_height_clearance_periodic": feet_height_clearance_periodic * self.cfg.feet_height_clearance_periodic_reward_scale * self.step_dt,
            "feet_height_clearance_mujoco": feet_height_clearance_mujoco * self.cfg.feet_height_clearance_mujoco_reward_scale * self.step_dt,
            "feet_height_clearance_mujoco_periodic": feet_height_clearance_mujoco_periodic * self.cfg.feet_height_clearance_mujoco_periodic_reward_scale * self.step_dt,
            
            "feet_slide": feet_slide * self.cfg.feet_slide_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "feet_contact_suggestion": feet_contact_suggestion * self.cfg.feet_contact_suggestion_reward_scale * self.step_dt,
            "feet_to_base_distance_l2": feet_to_base_distance * self.cfg.feet_to_base_distance_reward_scale * self.step_dt,
            "feet_to_hip_distance_l2": feet_to_hip_distance * self.cfg.feet_to_hip_distance_reward_scale * self.step_dt * (1.0 - back_failed_flag),
            "feet_vertical_surface_contacts": feet_vertical_surface_contacts * self.cfg.feet_vertical_surface_contacts_reward_scale * self.step_dt,
            # (front-hip height error mapped is used above as track_height_exp)
            
            #commando rewards
            # Gate terms by whether any torque scaling (hip/thigh/calf) is active on the corresponding leg
            "commando_base_orientation": commando_base_orientation * self.cfg.commando_base_orientation_reward_scale * self.step_dt * back_failed_flag,
            "commando_undesired_contacts": commando_contacts * self.cfg.commando_undesired_contact_reward_scale * self.step_dt * back_failed_flag,
            "commando_feet_air_time": commando_feet_air_time * self.cfg.commando_feet_air_time_reward_scale * self.step_dt * back_failed_flag,# * ( (leg_any_scaled_int[:, 2] + leg_any_scaled_int[:, 3]) > 0 ).float()
            "commando_feet_slide": commando_feet_slide * self.cfg.commando_feet_slide_reward_scale * self.step_dt * back_failed_flag,
            "commando_feet_to_hip_distance": commando_feet_to_hip_distance * self.cfg.commando_feet_to_hip_distance_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_torques_l2": commando_joints_torques * self.cfg.commando_joints_torque_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_acc_l2": commando_joints_accel * self.cfg.commando_joints_accel_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_energy_l1": commando_joints_energy * self.cfg.commando_joints_energy_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_hip_pos_l2": commando_hip_joints_position_reward * self.cfg.commando_joints_hip_position_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_thigh_pos_l2": commando_thigh_joints_position_reward * self.cfg.commando_joints_thigh_position_reward_scale * self.step_dt * back_failed_flag,
            "commando_joints_calf_pos_l2": commando_calf_joints_position_reward * self.cfg.commando_joints_calf_position_reward_scale * self.step_dt * back_failed_flag,
            "commando_action_rate_l2": commando_action_rate * self.cfg.commando_action_rate_reward_scale * self.step_dt * back_failed_flag,
            "commando_action_smoothness_l2": commando_action_smoothness * self.cfg.commando_action_smoothness_reward_scale * self.step_dt * back_failed_flag,
            # Use front-hip height error (mapped) as the single height tracking reward
            "commando_track_height_exp": commando_front_hip_height_error_mapped * self.cfg.commando_front_hip_height_reward_scale * self.step_dt * back_failed_flag,
            
            # 3 leg rewards 
            "feet_air_time_FL_failure": feet_air_time_FL_failure * self.cfg.feet_air_time_FL_failure_reward_scale * self.step_dt * (leg_any_scaled_int[:, 0].float()) * (1.0 - back_failed_flag),
            "feet_air_time_RL_failure": feet_air_time_RL_failure * self.cfg.feet_air_time_RL_failure_reward_scale * self.step_dt * (leg_any_scaled_int[:, 2].float()) * (1.0 - back_failed_flag),
            "feet_air_time_FR_failure": feet_air_time_FR_failure * self.cfg.feet_air_time_FR_failure_reward_scale * self.step_dt * (leg_any_scaled_int[:, 1].float()) * (1.0 - back_failed_flag),
            "feet_air_time_RR_failure": feet_air_time_RR_failure * self.cfg.feet_air_time_RR_failure_reward_scale * self.step_dt * (leg_any_scaled_int[:, 3].float()) * (1.0 - back_failed_flag),
       }
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0)
        
        # Logging
        for key, value in rewards.items():
            self._episode_sums[key] += value
        return reward


    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        # Only consider front hips for termination; ignore base and rear hips
        front_hip_ids = self._hip_ids[:2]
        died_check_front_hips = torch.any(
            torch.max(torch.norm(net_contact_forces[:, :, front_hip_ids], dim=-1), dim=1)[0] > 1.0,
            dim=1,
        )

        # Check contacts for base and all hips (used when failure_type != 29)
        died_check_base = torch.any(
            torch.max(torch.norm(net_contact_forces[:, :, self._base_id], dim=-1), dim=1)[0] > 1.0,
            dim=1,
        )
        died_check_hips = torch.any(
            torch.max(torch.norm(net_contact_forces[:, :, self._hip_ids], dim=-1), dim=1)[0] > 1.0,
            dim=1,
        )
        died_non29 = torch.logical_or(died_check_base, died_check_hips)

        # Per-environment selection: if an env's failure_type == 29, use front-hip check,
        # otherwise use base OR hips check.
        # Per-env flag: True where failure_type == 29 (both rear legs disabled)
        is_rear_both = self._failure_type == 1

        # Ensure boolean tensors are same device/dtype and select per-env
        died = torch.where(is_rear_both, died_check_front_hips, died_non29)
       # Check if the robot is out of bounds of the terrain
        """if(self._terrain.cfg.terrain_generator is not None):
            # obtain the size of the sub-terrains
            terrain_gen_cfg = self._terrain.cfg.terrain_generator
            grid_width, grid_length = terrain_gen_cfg.size
            n_rows, n_cols = terrain_gen_cfg.num_rows, terrain_gen_cfg.num_cols
            border_width = terrain_gen_cfg.border_width
            # compute the size of the map
            map_width = n_rows * grid_width + 2 * border_width
            map_height = n_cols * grid_length + 2 * border_width

            # check if the agent is out of bounds
            distance_buffer = 3.
            x_out_of_bounds = torch.abs(self._robot.data.root_state_w[:, 0]) > 0.5 * map_width - distance_buffer
            y_out_of_bounds = torch.abs(self._robot.data.root_state_w[:, 1]) > 0.5 * map_height - distance_buffer
            out_of_bounds = torch.logical_or(x_out_of_bounds, y_out_of_bounds)
            time_out = torch.logical_or(time_out, out_of_bounds) #HACK"""
        
        return died, time_out


    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._robot._ALL_INDICES

        if(self._terrain.cfg.terrain_generator is not None and self._terrain.cfg.terrain_generator.curriculum == True):
            # Curriculum based on the distance the robot walked
            distance = torch.norm(self._robot.data.root_state_w[env_ids, :2] - self._terrain.env_origins[env_ids, :2], dim=1)
            # robots that walked far enough progress to harder terrains
            move_up = distance > self._terrain.cfg.terrain_generator.size[0] / 2
            # robots that walked less than half of their required distance go to simpler terrains
            move_down = distance < torch.norm(self._commands[env_ids, :2], dim=1) * self.max_episode_length_s * 0.5
            move_down *= ~move_up
            # update terrain levels
            self._terrain.update_env_origins(env_ids, move_up, move_down)

        self._robot.reset(env_ids)
        super()._reset_idx(env_ids)
        if len(env_ids) == self.num_envs: 
            # Spread out the resets to avoid spikes in training when many environments reset at a similar time
            self.episode_length_buf[:] = torch.randint_like(self.episode_length_buf, high=int(self.max_episode_length))
        self._actions[env_ids] = 0.0
        self._previous_actions[env_ids] = 0.0
        self._previous_previous_actions[env_ids] = 0.0
        
        # Sample new commands
        self._commands[env_ids] = torch.zeros_like(self._commands[env_ids]).uniform_(-1.0, 1.0)
        # Per-command base scaling
        self._commands[env_ids, 0] *= 0.5
        self._commands[env_ids, 1] *= 0.25 
        self._commands[env_ids, 2] *= 0.3 

        # Reset swing peak
        self._swing_peak[env_ids] = torch.tensor([0.0, 0.0, 0.0, 0.0], device=self.device)
        self._swing_peak_periodic[env_ids] = torch.tensor([0.0, 0.0, 0.0, 0.0], device=self.device)
        
        # Reset contact periodic
        self._phase_signal[env_ids] = self._phase_offset[env_ids].clone()# + self.step_dt * self._step_freq * torch.rand(env_ids.shape[0], 1, device=self.device)*10.
        self._phase_signal[env_ids] = self._phase_signal[env_ids]  % 1.0

        # Reset noise
        if(self.cfg.use_cuncurrent_state_est):
            if self.cfg.observation_noise_model:
                self._observation_noise_model_cuncurrent_state_est.reset(env_ids)
        
        if(self.cfg.use_rma):
            if self.cfg.observation_noise_model:
                self._observation_noise_model_rma.reset(env_ids)

        # Reset robot state
        joint_pos = self._robot.data.default_joint_pos[env_ids]
        joint_vel = self._robot.data.default_joint_vel[env_ids]
        default_root_state = self._robot.data.default_root_state[env_ids]
        default_root_state[:, :3] += self._terrain.env_origins[env_ids]
        default_root_state[:, 3:7] = math_utils.random_yaw_orientation(env_ids.shape[0], device=self.device)
        self._robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self._robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self._robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)
        
        # Logging
        extras = dict()
        for key in self._episode_sums.keys():
            episodic_sum_avg = torch.mean(self._episode_sums[key][env_ids])
            extras["Episode_Reward/" + key] = episodic_sum_avg / self.max_episode_length_s
            self._episode_sums[key][env_ids] = 0.0
        self.extras["log"] = dict()
        self.extras["log"].update(extras)
        extras = dict()
        extras["Episode_Termination/base_contact"] = torch.count_nonzero(self.reset_terminated[env_ids]).item()
        extras["Episode_Termination/time_out"] = torch.count_nonzero(self.reset_time_outs[env_ids]).item()
        
        if(self._terrain.cfg.terrain_generator is not None and self._terrain.cfg.terrain_generator.curriculum == True):
            extras["Episode_Curriculum/terrain_levels"] = torch.mean(self._terrain.terrain_levels.float())
        
        self.extras["log"].update(extras)

        # --- Apply per-episode randomized leg failure mask (torque scaling) ---
        # Six-way failure sampling:
        # 0: no failure
        # 1: rear failure (disable RL & RR)
        # 2: front-left failure (disable FL thigh & calf)
        # 3: front-right failure (disable FR thigh & calf)
        # 4: rear-left failure (disable RL thigh & calf)
        # 5: rear-right failure (disable RR thigh & calf)
        # Configure categorical probabilities via cfg.failure_type_probs = [p0, p1, p2, p3, p4, p5]
        probs_cfg = getattr(self.cfg, "failure_type_probs",[0.0, 1.0, 0.0, 0.0, 0.0, 0.0]) # [1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0, 1.0/6.0])
        probs = torch.tensor(probs_cfg, dtype=torch.float, device=self.device)
        probs = torch.clip(probs, min=0.0)
        total = probs.sum()
        if total <= 0:
            probs = torch.tensor([0.0, 1.0, 0.0, 0.0, 0.0, 0.0] , dtype=torch.float, device=self.device)
            total = probs.sum()
        probs = probs / total
        # Sample fail_type per env from categorical distribution
        # torch.multinomial expects probs on CPU for older versions; guard as needed
        indices = torch.multinomial(probs, num_samples=len(env_ids), replacement=True)
        fail_type = indices.to(torch.long)
        # Persist failure type for these envs until next reset
        self._failure_type[env_ids] = fail_type

        # Always assign NO failure (code 0) for every env in env_ids
        #fail_type = torch.zeros(len(env_ids), device=self.device, dtype=torch.long)
        #self._failure_type[env_ids] = fail_type

        self._rear_joint_indices = [2, 3, 6, 7, 10, 11]
        self._front_joint_indices = [0, 1, 4, 5, 8, 9]  # for possible future use

        rear_joint_indices = self._rear_joint_indices
        front_joint_indices = self._front_joint_indices
        # Use the failure assignment sampled for THIS reset batch only
        # (don't touch envs outside env_ids; restore defaults only where current fail_type==0)
        failure_type_subset = fail_type  # shape: [len(env_ids)]
        rear_failed_mask = failure_type_subset == 1
        # Zero gains for rear-failed envs
        if torch.any(rear_failed_mask):
            rear_failed_envs = env_ids[rear_failed_mask]
            default_stiffness_restore = self._robot.data.default_joint_stiffness[rear_failed_envs]
            default_damping_restore = self._robot.data.default_joint_damping[rear_failed_envs]
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rear_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rear_failed_envs)
            self._robot.write_joint_stiffness_to_sim(0.0, joint_ids=rear_joint_indices, env_ids=rear_failed_envs)
            self._robot.write_joint_damping_to_sim(0.0, joint_ids=rear_joint_indices, env_ids=rear_failed_envs)
            # Also activate the per-leg, per-joint torque-scaled mask for RL/RR as in custom_events.scale_joint_torque
            # Legs: RL=2, RR=3; Joints: hip=0, thigh=1, calf=2
            self._torque_scaled_mask_per_leg_joint[rear_failed_envs, 0, :] = 0.0
            self._torque_scaled_mask_per_leg_joint[rear_failed_envs, 1, :] = 0.0
            self._torque_scaled_mask_per_leg_joint[rear_failed_envs, 2, :] = 1.0
            self._torque_scaled_mask_per_leg_joint[rear_failed_envs, 3, :] = 1.0
            
            # Also attempt to apply actuator-side torque scaling (set efforts -> 0.0) for rear joints
            # Use the shared helper in tasks.custom_events.scale_joint_torque when available so
            # actuator.compute is patched in a consistent way across the codebase.
            # Import helper (prefer relative import within package; fallback to absolute)

            # RL joints: indices at positions 0,2,4 in rear_joint_indices
            rl_joint_ids = [rear_joint_indices[0], rear_joint_indices[2], rear_joint_indices[4]]
            rl_names = ["RL_hip_joint", "RL_thigh_joint", "RL_calf_joint"]
            # RR joints: indices at positions 1,3,5 in rear_joint_indices
            rr_joint_ids = [rear_joint_indices[1], rear_joint_indices[3], rear_joint_indices[5]]
            rr_names = ["RR_hip_joint", "RR_thigh_joint", "RR_calf_joint"]
            fl_joint_ids = [front_joint_indices[0], front_joint_indices[2], front_joint_indices[4]]
            fl_names = ["FL_hip_joint", "FL_thigh_joint", "FL_calf_joint"]
            fr_joint_ids = [front_joint_indices[1], front_joint_indices[3], front_joint_indices[5]]
            fr_names = ["FR_hip_joint", "FR_thigh_joint", "FR_calf_joint"]
            # Apply zero scaling to rear legs for the failed envs
            scale_joint_torque(
                env=self,
                env_ids=rear_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=fl_joint_ids, joint_names=fl_names),
                scale=1.0,
            )
            scale_joint_torque(
                env=self,
                env_ids=rear_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=fr_joint_ids, joint_names=fr_names),
                scale=1.0,
            )
            scale_joint_torque(
                env=self,
                env_ids=rear_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=rl_joint_ids, joint_names=rl_names),
                scale=0.0,
            )
            scale_joint_torque(
                env=self,
                env_ids=rear_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=rr_joint_ids, joint_names=rr_names),
                scale=0.0,
            )
            
        # Restore defaults for non-failed envs
        # fine  fix all joints for non-failed envs
        fine_mask = failure_type_subset == 0
        if torch.any(fine_mask):
            normal_envs = env_ids[fine_mask]
            default_stiffness_restore = self._robot.data.default_joint_stiffness[normal_envs]
            default_damping_restore = self._robot.data.default_joint_damping[normal_envs]
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=normal_envs)
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=normal_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=normal_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=normal_envs)

            # # Reset mask for non-failed envs
            # self._torque_scaled_mask_per_leg_joint[normal_envs, :, :] = 0.0
            # # Also attempt to restore actuator-side torque scaling (set efforts -> 1.0) for all joints

            whole_joint_ids = [0,1,2,3,4,5,6,7,8,9,10,11]
            whole_names = [
                "FL_hip_joint", "FR_hip_joint",
                "RL_hip_joint", "RR_hip_joint",
                "FL_thigh_joint", "FR_thigh_joint",
                "RL_thigh_joint", "RR_thigh_joint",
                "FL_calf_joint", "FR_calf_joint",
                "RL_calf_joint", "RR_calf_joint",
            ]

            scale_joint_torque(
                env=self,
                env_ids=normal_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=whole_joint_ids, joint_names=whole_names),
                scale=1.0,
            )

        # FL failure
        fl_failed_mask = failure_type_subset == 2
        if torch.any(fl_failed_mask):
            fl_failed_envs = env_ids[fl_failed_mask]
            all_leg_names = [
                "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
                "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
                "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
                "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint",
            ]
            scale_joint_torque(
                env=self,
                env_ids=env_ids,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=slice(None), joint_names=all_leg_names),
                scale=1.0,
            )

            # Apply per-leg failures for envs where failure_type_subset == 2 (FL only)
            # Map leg codes to name prefixes
            leg_map = [("FL", 2)]
            for leg_prefix, code in leg_map:
                fl_failed_mask = failure_type_subset == code
                if not fl_failed_mask.any():
                    continue
                fl_failed_envs = env_ids[fl_failed_mask]
                # Find joint indices for this leg and scale them to zero
                # Scale only thigh and calf (exclude hip)
                pattern = rf"{leg_prefix}_(thigh|calf)_joint"
                leg_joint_ids, _ = self._robot.find_joints(pattern)
                if leg_joint_ids is None:
                    continue
                # Prefer passing plain Python lists into the config to avoid unnecessary GPU<->CPU hops
                if isinstance(leg_joint_ids, torch.Tensor):
                    leg_joint_ids_list = leg_joint_ids.detach().cpu().tolist()
                else:
                    # Ensure it's a list (find_joints may already return a list)
                    leg_joint_ids_list = list(leg_joint_ids)
                # Only scale thigh and calf (exact names)
                joint_names = [f"{leg_prefix}_thigh_joint", f"{leg_prefix}_calf_joint"]
                scale_joint_torque(
                    env=self,
                    env_ids=fl_failed_envs,
                    asset_cfg=SceneEntityCfg(
                        name="robot",
                        joint_ids=leg_joint_ids_list,
                        joint_names=joint_names,
                    ),
                    scale=0.0,
                )
            # default_stiffness_restore = self._robot.data.default_joint_stiffness[fl_failed_envs]
            # default_damping_restore = self._robot.data.default_joint_damping[fl_failed_envs]
            # self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=fl_failed_envs)
            # self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=fl_failed_envs)
            # self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=fl_failed_envs)
            # self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=fl_failed_envs)

            # # Deactivate the mask for RL/RR on envs assigned no-failure this reset
            # self._torque_scaled_mask_per_leg_joint[normal_envs, :, :] = 0.0

            # whole_joint_ids = [0,1,2,3,4,5,6,7,8,9,10,11]
            # whole_names = [
            #     "FL_hip_joint", "FR_hip_joint",
            #     "RL_hip_joint", "RR_hip_joint",
            #     "FL_thigh_joint", "FR_thigh_joint",
            #     "RL_thigh_joint", "RR_thigh_joint",
            #     "FL_calf_joint", "FR_calf_joint",
            #     "RL_calf_joint", "RR_calf_joint",
            # ]

            # scale_joint_torque(
            #     env=self,
            #     env_ids=fl_failed_envs,
            #     asset_cfg=SceneEntityCfg(name="robot", joint_ids=whole_joint_ids, joint_names=whole_names),
            #     scale=1.0,
            # )

            # # Also activate the per-leg,
            # fl_joint_ids = [4, 8] # thigh and calf
            # fl_joint_names = ["FL_thigh_joint", "FL_calf_joint"]
            # scale_joint_torque(
            #     env=self,
            #     env_ids=fl_failed_envs,
            #     asset_cfg=SceneEntityCfg(
            #         name="robot",
            #         joint_ids=fl_joint_ids,
            #         joint_names=fl_joint_names,
            #     ),
            #     scale=0.0,
            # )

        # FR failure (disable FR thigh & calf)
        fr_failed_mask = failure_type_subset == 3
        if torch.any(fr_failed_mask):
            fr_failed_envs = env_ids[fr_failed_mask]
            default_stiffness_restore = self._robot.data.default_joint_stiffness[fr_failed_envs]
            default_damping_restore = self._robot.data.default_joint_damping[fr_failed_envs]
            # Restore defaults on all joints for these envs first
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=fr_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=fr_failed_envs)
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=fr_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=fr_failed_envs)

            # Scale all joints to 1.0 first
            whole_joint_ids = [0,1,2,3,4,5,6,7,8,9,10,11]
            whole_names = [
                "FL_hip_joint", "FR_hip_joint",
                "RL_hip_joint", "RR_hip_joint",
                "FL_thigh_joint", "FR_thigh_joint",
                "RL_thigh_joint", "RR_thigh_joint",
                "FL_calf_joint", "FR_calf_joint",
                "RL_calf_joint", "RR_calf_joint",
            ]
            scale_joint_torque(
                env=self,
                env_ids=fr_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=whole_joint_ids, joint_names=whole_names),
                scale=1.0,
            )

            # Deactivate FR thigh & calf
            fr_joint_ids = [5, 9]  # FR thigh and calf
            fr_joint_names = ["FR_thigh_joint", "FR_calf_joint"]
            scale_joint_torque(
                env=self,
                env_ids=fr_failed_envs,
                asset_cfg=SceneEntityCfg(
                    name="robot",
                    joint_ids=fr_joint_ids,
                    joint_names=fr_joint_names,
                ),
                scale=0.0,
            )

        # RL failure (disable RL thigh & calf)
        rl_failed_mask = failure_type_subset == 4
        if torch.any(rl_failed_mask):
            rl_failed_envs = env_ids[rl_failed_mask]
            default_stiffness_restore = self._robot.data.default_joint_stiffness[rl_failed_envs]
            default_damping_restore = self._robot.data.default_joint_damping[rl_failed_envs]
            # Restore defaults on all joints for these envs first
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=rl_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=rl_failed_envs)
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rl_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rl_failed_envs)

            # Scale all joints to 1.0 first
            whole_joint_ids = [0,1,2,3,4,5,6,7,8,9,10,11]
            whole_names = [
                "FL_hip_joint", "FR_hip_joint",
                "RL_hip_joint", "RR_hip_joint",
                "FL_thigh_joint", "FR_thigh_joint",
                "RL_thigh_joint", "RR_thigh_joint",
                "FL_calf_joint", "FR_calf_joint",
                "RL_calf_joint", "RR_calf_joint",
            ]
            scale_joint_torque(
                env=self,
                env_ids=rl_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=whole_joint_ids, joint_names=whole_names),
                scale=1.0,
            )

            # Deactivate RL thigh & calf
            rl_joint_ids = [6, 10]
            rl_joint_names = ["RL_thigh_joint", "RL_calf_joint"]
            scale_joint_torque(
                env=self,
                env_ids=rl_failed_envs,
                asset_cfg=SceneEntityCfg(
                    name="robot",
                    joint_ids=rl_joint_ids,
                    joint_names=rl_joint_names,
                ),
                scale=0.0,
            )

        # RR failure (disable RR thigh & calf)
        rr_failed_mask = failure_type_subset == 5
        if torch.any(rr_failed_mask):
            rr_failed_envs = env_ids[rr_failed_mask]
            default_stiffness_restore = self._robot.data.default_joint_stiffness[rr_failed_envs]
            default_damping_restore = self._robot.data.default_joint_damping[rr_failed_envs]
            # Restore defaults on all joints for these envs first
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=rr_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._rear_joint_indices], joint_ids=self._rear_joint_indices, env_ids=rr_failed_envs)
            self._robot.write_joint_stiffness_to_sim(default_stiffness_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rr_failed_envs)
            self._robot.write_joint_damping_to_sim(default_damping_restore[:, self._front_joint_indices], joint_ids=self._front_joint_indices, env_ids=rr_failed_envs)

            # Scale all joints to 1.0 first
            whole_joint_ids = [0,1,2,3,4,5,6,7,8,9,10,11]
            whole_names = [
                "FL_hip_joint", "FR_hip_joint",
                "RL_hip_joint", "RR_hip_joint",
                "FL_thigh_joint", "FR_thigh_joint",
                "RL_thigh_joint", "RR_thigh_joint",
                "FL_calf_joint", "FR_calf_joint",
                "RL_calf_joint", "RR_calf_joint",
            ]
            scale_joint_torque(
                env=self,
                env_ids=rr_failed_envs,
                asset_cfg=SceneEntityCfg(name="robot", joint_ids=whole_joint_ids, joint_names=whole_names),
                scale=1.0,
            )

            # Deactivate RR thigh & calf
            rr_joint_ids = [7, 11]
            rr_joint_names = ["RR_thigh_joint", "RR_calf_joint"]
            scale_joint_torque(
                env=self,
                env_ids=rr_failed_envs,
                asset_cfg=SceneEntityCfg(
                    name="robot",
                    joint_ids=rr_joint_ids,
                    joint_names=rr_joint_names,
                ),
                scale=0.0,
            )
        
            
        # ------------------------------------------------------------------



    def _get_new_random_commands(self):
        
        # Change direction while moving
        resample_time = self.episode_length_buf == self.max_episode_length - 400
        commands_resample = torch.zeros_like(self._commands).uniform_(-1.0, 1.0)
        commands_resample[:, 0] *= 0.5
        commands_resample[:, 1] *= 0.25 
        commands_resample[:, 2] *= 0.3 
        self._commands[:, :3] = self._commands[:, :3] * ~resample_time.unsqueeze(1).expand(-1, 3) + commands_resample * resample_time.unsqueeze(1).expand(-1, 3)

        # Stop
        rest_time = torch.logical_and(
            self.episode_length_buf >= self.max_episode_length - 250,
            self.episode_length_buf < self.max_episode_length - 150
        )
        self._commands[:, :3] *= ~rest_time.unsqueeze(1).expand(-1, 3)

        # Move again
        resample_time_2 = self.episode_length_buf == self.max_episode_length - 150
        commands_resample_2 = torch.zeros_like(self._commands).uniform_(-1.0, 1.0)
        commands_resample_2[:, 0] *= 0.5
        commands_resample_2[:, 1] *= 0.25 
        commands_resample_2[:, 2] *= 0.3 
        self._commands[:, :3] = self._commands[:, :3] * ~resample_time_2.unsqueeze(1).expand(-1, 3) + commands_resample_2 * resample_time_2.unsqueeze(1).expand(-1, 3)        

        # Took some envs, and put to zero the vel
        if self.num_envs > 100:
            num_fixed_envs = 100
            fixed_env_ids = torch.arange(num_fixed_envs, device=self.device)
            self._commands[fixed_env_ids, :3] *= 0.0


    def _get_cuncurrent_state_estimation(self, clock_data):
        # Using a supervised learning state estimation
        obs_cuncurrent_state_est = torch.cat(
            [
                tensor
                for tensor in (
                    self._imu.data.lin_acc_b,
                    self._imu.data.ang_vel_b,
                    self._robot.data.projected_gravity_b,
                    self._commands,
                    self._robot.data.joint_pos - self._robot.data.default_joint_pos,
                    self._robot.data.joint_vel,
                    self._actions,
                    clock_data,
                )
                if tensor is not None
            ],
            dim=-1,
        )
        #the bottom element is the newest observation!!
        self._observation_history_cuncurrent_state_est = torch.cat((self._observation_history_cuncurrent_state_est[:,1:,:], obs_cuncurrent_state_est.unsqueeze(1)), dim=1)
        obs_cuncurrent_state_est = torch.flatten(self._observation_history_cuncurrent_state_est, start_dim=1)     

        # Add noise to the observation - this is usually done in direct_rl.py in IsaacLab, but 
        # the obs of cuncurrent SE does not pass from there - its prediciton yes instead!
        if self.cfg.observation_noise_model:          
            obs_cuncurrent_state_est = self._observation_noise_model_cuncurrent_state_est(obs_cuncurrent_state_est)   

        # Saving data
        output_cuncurrent_state_est = self._robot.data.root_lin_vel_b
        self._cuncurrent_state_est_network.dataset.add_sample(obs_cuncurrent_state_est, output_cuncurrent_state_est)

        # Prediction
        num_episode_from_start = self.common_step_counter / 24. #self.max_episode_length #HACK this should be taken from rsl rl
        num_final_episode_from_start = 8000.
        if num_episode_from_start > self.cfg.cuncurrent_state_est_ep_saving_interval:
            with torch.no_grad(): 
                prediction_cuncurrent_state_est = self._cuncurrent_state_est_network(obs_cuncurrent_state_est)
            linear_velocity_b = prediction_cuncurrent_state_est[:, :3]
        else:
            linear_velocity_b = self._robot.data.root_lin_vel_b

        # Train at some interval
        if (num_episode_from_start % self.cfg.cuncurrent_state_est_ep_saving_interval == 0 and 
            num_episode_from_start > self.cfg.cuncurrent_state_est_ep_saving_interval - 1 and 
                num_episode_from_start < num_final_episode_from_start - 500):  # Adjust the interval as needed
            self._cuncurrent_state_est_network.train_network(batch_size=self.cfg.cuncurrent_state_est_batch_size, 
                                                            epochs=self.cfg.cuncurrent_state_est_train_epochs, 
                                                            learning_rate=self.cfg.cuncurrent_state_est_lr, device=self.device)
            # Save the network
            self._cuncurrent_state_est_network.save_network("cuncurrent_state_estimator.pth", self.device)    

        return linear_velocity_b  


    def _get_rma(self, clock_data):
        # Learning privileged information via supervised learning
        obs_rma = torch.cat(
            [
                tensor
                for tensor in (
                    self._imu.data.lin_acc_b,
                    self._imu.data.ang_vel_b,
                    self._robot.data.projected_gravity_b,
                    self._commands,
                    self._robot.data.joint_pos - self._robot.data.default_joint_pos,
                    self._robot.data.joint_vel,
                    self._actions,
                    clock_data,
                )
                if tensor is not None
            ],
            dim=-1,
        )
        #the bottom element is the newest observation!!
        self._observation_history_rma = torch.cat((self._observation_history_rma[:,1:,:], obs_rma.unsqueeze(1)), dim=1)
        obs = torch.flatten(self._observation_history_rma, start_dim=1)

        # Add noise to the observation - this is usually done in direct_rl.py in IsaacLab, but 
        # the obs of cuncurrent SE does not pass from there - its prediciton yes instead!
        if self.cfg.observation_noise_model:          
            obs = self._observation_noise_model_rma(obs.clone())  
        
        outputs_rma = self._get_privileged_observation()

        self._rma_network.dataset.add_sample(obs, outputs_rma)

        # Prediction
        num_episode_from_start = self.common_step_counter / 24. #self.max_episode_length #HACK this should be taken from rsl rl
        num_final_episode_from_start = 8000.
        if num_episode_from_start > self.cfg.rma_ep_saving_interval:
            with torch.no_grad(): 
                prediction_rma = self._rma_network(obs)
            obs_rma = prediction_rma
        else:
            obs_rma = outputs_rma

        # Train at some interval
        if (num_episode_from_start % self.cfg.rma_ep_saving_interval == 0 and 
            num_episode_from_start > self.cfg.rma_ep_saving_interval - 1 and 
                num_episode_from_start < num_final_episode_from_start - 500):  # Adjust the interval as needed
            self._rma_network.train_network(batch_size=self.cfg.rma_batch_size, 
                                            epochs=self.cfg.rma_train_epochs, 
                                            learning_rate=self.cfg.rma_lr, 
                                            device=self.device)
            # Save the network
            self._rma_network.save_network("rma.pth", self.device)
        
        return obs_rma


    def _get_privileged_observation(self):
        asset_cfg = SceneEntityCfg("robot", joint_names=[".*"])
        asset: Articulation = self.scene[asset_cfg.name]
        hip_static_friction = asset.actuators["hip"].friction_static
        thigh_static_friction = asset.actuators["thigh"].friction_static
        calf_static_friction = asset.actuators["calf"].friction_static
        
        hip_dynamic_friction = asset.actuators["hip"].friction_dynamic
        thigh_dynamic_friction = asset.actuators["thigh"].friction_dynamic
        calf_dynamic_friction = asset.actuators["calf"].friction_dynamic

        hip_armature = asset.actuators["hip"].armature
        thigh_armature = asset.actuators["thigh"].armature
        calf_armature = asset.actuators["calf"].armature

        hip_stiffness = asset.actuators["hip"].stiffness
        thigh_stiffness = asset.actuators["thigh"].stiffness
        calf_stiffness = asset.actuators["calf"].stiffness

        hip_damping = asset.actuators["hip"].damping
        thigh_damping = asset.actuators["thigh"].damping
        calf_damping = asset.actuators["calf"].damping

        #asset_cfg_base = SceneEntityCfg("robot", body_names="base")
        #asset_base = self.scene[asset_cfg_base.name]
        #masses = asset_base.root_physx_view.get_masses()
        #inertias = asset_base.root_physx_view.get_inertias()

        default_stiffness = asset.data.default_joint_stiffness[0][0]
        default_damping = asset.data.default_joint_damping[0][0]


        # height error
        height_data_scanner = self._height_scanner.data.ray_hits_w[..., 2]
        height_data_scanner = torch.nan_to_num(height_data_scanner, nan=0.0, posinf=1.0, neginf=-1.0)
        height_data_scanner = torch.clip(height_data_scanner, min=-5, max=5) # Handle inf values
        mean_height_ray = torch.mean(height_data_scanner, dim=1)
        height_error = torch.abs(self.cfg.desired_base_height + mean_height_ray - self._robot.data.root_state_w[:, 2])


        # terrain orientation
        height_map_resolution = self._height_scanner.cfg.pattern_cfg.resolution
        height_map_x_points = int(round(self._height_scanner.cfg.pattern_cfg.size[0] / height_map_resolution)) + 1
        height_map_y_points = int(round(self._height_scanner.cfg.pattern_cfg.size[1] / height_map_resolution))
        distance_between_front_and_back = (height_map_x_points/2)* height_map_resolution

        cols_back = torch.arange(0, height_data_scanner.shape[1], height_map_x_points).unsqueeze(1) + torch.arange(int(height_map_x_points/2))
        cols_back = cols_back.flatten().to(height_data_scanner.device)
        selected_height_data_back = height_data_scanner[:, cols_back]

        cols_front = torch.arange(int(height_map_x_points/2), height_data_scanner.shape[1], height_map_x_points).unsqueeze(1) + torch.arange(int(height_map_x_points/2))
        cols_front = cols_front.flatten().to(height_data_scanner.device)
        selected_height_data_front = height_data_scanner[:, cols_front]

        mean_height_ray_front = torch.mean(selected_height_data_front, dim=1)
        mean_height_ray_back = torch.mean(selected_height_data_back, dim=1)
        delta_z = mean_height_ray_front - mean_height_ray_back
        delta_s = torch.tensor(distance_between_front_and_back).to(self.device)
        terrain_pitch = -torch.atan2(delta_z, delta_s)

        obs_privileged = torch.cat(( 
                            #hip_stiffness/default_stiffness, thigh_stiffness/default_stiffness, calf_stiffness/default_stiffness, #P gain
                            #hip_damping/default_damping, thigh_damping/default_damping, calf_damping/default_damping, #D gain
                            height_error.unsqueeze(1),
                            terrain_pitch.unsqueeze(1),
                            #masses, inertias,
                            #hip_static_friction, thigh_static_friction, calf_static_friction,  
                            #hip_dynamic_friction, thigh_dynamic_friction, calf_dynamic_friction, 
                            #hip_armature, thigh_armature, calf_armature
                            ) 
                        , dim=-1)
        return obs_privileged