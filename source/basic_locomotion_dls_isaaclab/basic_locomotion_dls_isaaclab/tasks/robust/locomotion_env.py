# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

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
        
        # Desired Hip Offset
        self._desired_hip_offset = torch.tensor([-self.cfg.desired_hip_offset, self.cfg.desired_hip_offset, -self.cfg.desired_hip_offset, self.cfg.desired_hip_offset], device=self.device)
        
        # Periodic gait
        if(cfg.desired_gait == "trot"):
            self._step_freq = 1.4
            self._duty_factor = 0.65
            self._phase_offset = torch.tensor([0.0, 0.5, 0.5, 0.0], device=self.device).repeat(self.num_envs,1)
            self._velocity_gait_multiplier = 1.0
        elif(cfg.desired_gait == "crawl"):
            self._step_freq = 0.5
            self._duty_factor = 0.8
            self._phase_offset = torch.tensor([0.0, 0.5, 0.75, 0.25], device=self.device).repeat(self.num_envs,1)
            self._velocity_gait_multiplier = 0.5
        elif(cfg.desired_gait == "pace"):
            self._step_freq = 1.4
            self._duty_factor = 0.7
            self._phase_offset = torch.tensor([0.8, 0.3, 0.8, 0.3], device=self.device).repeat(self.num_envs,1)
            self._velocity_gait_multiplier = 1.0
        elif(cfg.desired_gait == "multigait"):
            #TODO: implement multigait
            raise NotImplementedError("Multigait not implemented yet")
        self._phase_signal = self._phase_offset.clone()# + self.step_dt * self._step_freq * torch.rand(self.num_envs, 1, device=self.device)*10.
        self._phase_signal = self._phase_signal % 1.0


        # Observation history
        self._observation_history = torch.zeros(self.num_envs, cfg.history_length, cfg.single_observation_space, device=self.device)

        # RMA
        if(cfg.use_rma == True):
            self._rma_network = SimpleNN(cfg.rma_observation_space, cfg.rma_output_space)
            self._rma_network.to(self.device)
            self._observation_history_rma = torch.zeros(self.num_envs, cfg.history_length, cfg.single_rma_observation_space, device=self.device)

        # Learned State Estimator
        if(cfg.use_cuncurrent_state_est == True):
            self._cuncurrent_state_est_network = SimpleNN(cfg.cuncurrent_state_est_observation_space, cfg.cuncurrent_state_est_output_space)
            self._cuncurrent_state_est_network.to(self.device)
            self._observation_history_cuncurrent_state_est = torch.zeros(self.num_envs, cfg.history_length, cfg.single_cuncurrent_state_est_observation_space, device=self.device)


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
                "feet_height_clearance",
                "feet_height_clearance_mujoco",
                "feet_slide",
                "feet_contact_suggestion",
                "feet_to_base_distance_l2",
                "feet_to_hip_distance_l2",
                "feet_vertical_surface_contacts",
            ]
        }
        # Get specific body indices
        self._base_id, _ = self._contact_sensor.find_bodies("base")
        self._feet_ids, _ = self._contact_sensor.find_bodies(".*foot")
        self._hip_ids, _ = self._contact_sensor.find_bodies(".*hip")
        self._thigh_ids, _ = self._contact_sensor.find_bodies(".*thigh")
        self._undesired_contact_body_ids = self._base_id + self._hip_ids + self._thigh_ids

        
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

        
        return observations


    def _get_rewards(self) -> torch.Tensor:

        # track_height
        height_data_scanner = self._height_scanner.data.ray_hits_w[..., 2]
        height_data_scanner = torch.nan_to_num(height_data_scanner, nan=0.0, posinf=1.0, neginf=-1.0)
        height_data_scanner = torch.clip(height_data_scanner, min=-5, max=5) # Handle inf values
        mean_height_ray = torch.mean(height_data_scanner, dim=1)

        height_error = torch.square(self.cfg.desired_base_height + mean_height_ray - self._robot.data.root_state_w[:, 2])
        height_error_mapped = torch.exp(-height_error / 0.01)


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
        
        root_roll_w, root_pitch_w, _ = math_utils.euler_xyz_from_quat(self._robot.data.root_quat_w)
        root_roll_w = torch.atan2(torch.sin(root_roll_w), torch.cos(root_roll_w))
        root_pitch_w = torch.atan2(torch.sin(root_pitch_w), torch.cos(root_pitch_w))
        
        base_orientation =  torch.square(terrain_pitch - root_pitch_w)# + torch.square(0 - root_roll_w)


        # angular velocity x/y tracking
        ang_vel_error = torch.sum(torch.square(self._robot.data.root_ang_vel_b[:, :2]), dim=1)


        # yaw rate tracking
        yaw_rate_error = torch.square(self._commands[:, 2] - self._robot.data.root_ang_vel_b[:, 2])
        yaw_rate_error_mapped = torch.exp(-yaw_rate_error / 0.25)
        
        
        # action rate
        action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)
        action_smoothness = torch.sum(torch.square(self._actions - 2*self._previous_actions + self._previous_previous_actions), dim=1)
        
        
        # undersired contacts
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        is_contact = (
            torch.max(torch.norm(net_contact_forces[:, :, self._undesired_contact_body_ids], dim=-1), dim=1)[0] > 1.0
        )
        contacts = torch.sum(is_contact, dim=1)
        

        # joint acceleration
        joints_accel = torch.sum(torch.square(self._robot.data.joint_acc), dim=1)


        # joint torques
        joints_torques = torch.sum(torch.square(self._robot.data.applied_torque), dim=1)


        # energy = torque * velocity
        joints_energy = torch.sum(torch.abs(self._robot.data.applied_torque * self._robot.data.joint_vel), dim=1)

        
        # hip position
        hip_joints_position = self._robot.data.joint_pos[:,0:4]
        hip_joints_position_error = torch.square(hip_joints_position - self._robot.data.default_joint_pos[:,0:4])
        hip_joints_position_reward = torch.sum(hip_joints_position_error,dim=1)


        # thigh position
        thigh_joints_position = self._robot.data.joint_pos[:,4:8]
        thigh_joints_position_error = torch.square(thigh_joints_position - self._robot.data.default_joint_pos[:,4:8])
        thigh_joints_position_reward = torch.sum(thigh_joints_position_error,dim=1)


        # calf position
        calf_joints_position = self._robot.data.joint_pos[:,8:12]
        calf_joints_position_error = torch.square(calf_joints_position - self._robot.data.default_joint_pos[:,8:12])
        calf_joints_position_reward = torch.sum(calf_joints_position_error,dim=1)


        # feet airtime
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        last_air_time = self._contact_sensor.data.last_air_time[:, self._feet_ids]
        feet_air_time = torch.sum((last_air_time - 0.5) * first_contact, dim=1) * (
            torch.norm(self._commands[:, :2], dim=1) > 0.1
        )


        # feet slide
        contacts_foot = self._contact_sensor.data.net_forces_w_history[:, :, self._feet_ids, :].norm(dim=-1).max(dim=1)[0] > 1.0
        body_vel = self._robot.data.body_lin_vel_w[:, self._feet_ids_robot, :2]
        feet_slide = torch.sum(body_vel.norm(dim=-1) * contacts_foot, dim=1)
        feet_slide = torch.exp(-feet_slide / 0.1)


        # feet periodical contacts suggestion
        should_move = torch.norm(self._commands[:, :3], dim=1) > 0.01
        self._phase_signal += self.step_dt * self._step_freq
        self._phase_signal = self._phase_signal % 1.0
        contact_periodic_on = self._phase_signal < self._duty_factor
        feet_contact_suggestion = (torch.sum(contact_periodic_on*contacts_foot, dim=1) + \
                                   torch.sum(~contact_periodic_on*~contacts_foot, dim=1))*should_move/4.0
        feet_contact_suggestion += (torch.sum(contacts_foot, dim=1)*~should_move/4.0)
        


        # feet height clearance mujoco
        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._feet_ids]
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        is_contact = (torch.max(torch.norm(net_contact_forces[:, :, self._feet_ids], dim=-1), dim=1)[0] > 1.0)
        self._swing_peak = torch.max(self._swing_peak, self._robot.data.body_pos_w[:, self._feet_ids_robot, 2].clone()) 
        #target_height = self.cfg.desired_feet_height + mean_height_ray.unsqueeze(1).expand(-1, 4)
        #feet_height_clearance_mujoco = torch.sum(torch.square(self._swing_peak / target_height - 1.0) *  first_contact, dim=-1)
        feet_z_target_error_mujoco = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._swing_peak
        feet_z_target_error_mujoco = torch.clamp(feet_z_target_error_mujoco, min=.0, max=self.cfg.desired_feet_height)
        feet_height_clearance_mujoco_FL = torch.exp(-feet_z_target_error_mujoco[:,0]/ 0.01) * should_move * ~contact_periodic_on[:,0] #first_contact[:,0]
        feet_height_clearance_mujoco_FR = torch.exp(-feet_z_target_error_mujoco[:,1]/ 0.01) * should_move * ~contact_periodic_on[:,1] #first_contact[:,1]
        feet_height_clearance_mujoco_RL = torch.exp(-feet_z_target_error_mujoco[:,2]/ 0.01) * should_move * ~contact_periodic_on[:,2] #first_contact[:,2]
        feet_height_clearance_mujoco_RR = torch.exp(-feet_z_target_error_mujoco[:,3]/ 0.01) * should_move * ~contact_periodic_on[:,3] #first_contact[:,3]
        feet_height_clearance_mujoco = feet_height_clearance_mujoco_FL + feet_height_clearance_mujoco_FR + feet_height_clearance_mujoco_RL + feet_height_clearance_mujoco_RR
        #self._swing_peak *= ~is_contact # reset if the foot is in contact
        self._swing_peak *= ~contact_periodic_on # reset if the foot is in contact periodic phase

        # feet height clearance periodic
        feet_z_target_error = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._robot.data.body_pos_w[:, self._feet_ids_robot, 2]
        #feet_z_target_error = self.cfg.desired_feet_height + torch.cat((mean_height_ray_front.unsqueeze(1).expand(-1, 2), mean_height_ray_back.unsqueeze(1).expand(-1, 2)), dim=1) - self._swing_peak
        feet_z_target_error = torch.clamp(feet_z_target_error, min=.0, max=self.cfg.desired_feet_height)
 
        feet_height_clearance_FL = torch.exp(-feet_z_target_error[:,0]/ 0.01) * should_move * ~contact_periodic_on[:,0]
        feet_height_clearance_FR = torch.exp(-feet_z_target_error[:,1]/ 0.01) * should_move * ~contact_periodic_on[:,1]
        feet_height_clearance_RL = torch.exp(-feet_z_target_error[:,2]/ 0.01) * should_move * ~contact_periodic_on[:,2]
        feet_height_clearance_RR = torch.exp(-feet_z_target_error[:,3]/ 0.01) * should_move * ~contact_periodic_on[:,3]
        feet_height_clearance = feet_height_clearance_FL + feet_height_clearance_FR + feet_height_clearance_RL + feet_height_clearance_RR

        # feet height clearance standard
        #foot_velocity_tanh = torch.tanh(2.0 * torch.norm(self._robot.data.body_lin_vel_w[:, self._feet_ids_robot, :2], dim=2))
        #feet_height_clearance = torch.exp(-torch.sum(feet_z_target_error * foot_velocity_tanh, dim=1)/ 0.01) * should_move


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
        feet_to_hip_distance_x = torch.square(feet_to_base_h[:, 0] - hip_to_base_h[:, 0])
        feet_to_hip_distance_y = torch.square(feet_to_base_h[:, 1] + desired_hip_offset.unsqueeze(0) - hip_to_base_h[:, 1])
        feet_to_hip_distance = -torch.mean(torch.sqrt(feet_to_hip_distance_x + feet_to_hip_distance_y), dim=1)
        

        # Penalize feet hitting vertical surfaces  
        forces_z = torch.abs(self._contact_sensor.data.net_forces_w[:, self._feet_ids, 2])
        forces_xy = torch.linalg.norm(self._contact_sensor.data.net_forces_w[:, self._feet_ids, :2], dim=2)
        feet_vertical_surface_contacts = torch.any(forces_xy > 4 * forces_z, dim=1).float()
        feet_vertical_surface_contacts *= torch.clamp(-self._robot.data.projected_gravity_b[:, 2], 0, 0.7) / 0.7


        rewards = {
            "track_height_exp": height_error_mapped * self.cfg.height_reward_scale * self.step_dt,
            "track_lin_vel_xy_exp": lin_vel_error_mapped * self.cfg.lin_vel_reward_scale * self.step_dt,
            "track_lin_vel_z_l2": z_vel_error * self.cfg.z_vel_reward_scale * self.step_dt,
            "track_orientation_l2": base_orientation * self.cfg.orientation_reward_scale * self.step_dt,
            "track_ang_vel_xy_l2": ang_vel_error * self.cfg.ang_vel_reward_scale * self.step_dt,
            "track_ang_vel_z_exp": yaw_rate_error_mapped * self.cfg.yaw_rate_reward_scale * self.step_dt,

            "undesired_contacts": contacts * self.cfg.undersired_contact_reward_scale * self.step_dt,
            "action_rate_l2": action_rate * self.cfg.action_rate_reward_scale * self.step_dt,
            "action_smoothness_l2": action_smoothness * self.cfg.action_smoothness_reward_scale * self.step_dt,

            "joints_hip_pos_l2": hip_joints_position_reward * self.cfg.joints_hip_position_reward_scale * self.step_dt,
            "joints_thigh_pos_l2": thigh_joints_position_reward * self.cfg.joints_thigh_position_reward_scale * self.step_dt,
            "joints_calf_pos_l2": calf_joints_position_reward * self.cfg.joints_calf_position_reward_scale * self.step_dt,
            "joints_acc_l2": joints_accel * self.cfg.joints_accel_reward_scale * self.step_dt,
            "joints_torques_l2": joints_torques * self.cfg.joints_torque_reward_scale * self.step_dt,
            "joints_energy_l1": joints_energy * self.cfg.joints_energy_reward_scale * self.step_dt,

            "feet_air_time": feet_air_time * self.cfg.feet_air_time_reward_scale * self.step_dt,
            "feet_height_clearance": feet_height_clearance * self.cfg.feet_height_clearance_reward_scale * self.step_dt,
            "feet_height_clearance_mujoco": feet_height_clearance_mujoco * self.cfg.feet_height_clearance_mujoco_reward_scale * self.step_dt,
            "feet_slide": feet_slide * self.cfg.feet_slide_reward_scale * self.step_dt,
            "feet_contact_suggestion": feet_contact_suggestion * self.cfg.feet_contact_suggestion_reward_scale * self.step_dt,
            "feet_to_base_distance_l2": feet_to_base_distance * self.cfg.feet_to_base_distance_reward_scale * self.step_dt,
            "feet_to_hip_distance_l2": feet_to_hip_distance * self.cfg.feet_to_hip_distance_reward_scale * self.step_dt,
            "feet_vertical_surface_contacts": feet_vertical_surface_contacts * self.cfg.feet_vertical_surface_contacts_reward_scale * self.step_dt,
        }
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0)
        
        # Logging
        for key, value in rewards.items():
            self._episode_sums[key] += value
        return reward


    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        net_contact_forces = self._contact_sensor.data.net_forces_w_history
        died_check_base = torch.any(torch.max(torch.norm(net_contact_forces[:, :, self._base_id], dim=-1), dim=1)[0] > 1.0, dim=1)
        died_check_hips = torch.any(torch.max(torch.norm(net_contact_forces[:, :, self._hip_ids], dim=-1), dim=1)[0] > 1.0, dim=1) 
        died = torch.logical_or(died_check_base, died_check_hips)
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
        self._commands[env_ids, 0] *= 0.5 * self._velocity_gait_multiplier
        self._commands[env_ids, 1] *= 0.25 
        self._commands[env_ids, 2] *= 0.3 

        # Reset swing peak
        self._swing_peak[env_ids] = torch.tensor([0.0, 0.0, 0.0, 0.0], device=self.device)
        
        # Reset contact periodic
        self._phase_signal[env_ids] = self._phase_offset[env_ids].clone()# + self.step_dt * self._step_freq * torch.rand(env_ids.shape[0], 1, device=self.device)*10.
        self._phase_signal[env_ids] = self._phase_signal[env_ids]  % 1.0

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



    def _get_new_random_commands(self):
        resample_time = self.episode_length_buf == self.max_episode_length - 200
        commands_resample = torch.zeros_like(self._commands).uniform_(-1.0, 1.0)
        commands_resample[:, 0] *= 0.5 * self._velocity_gait_multiplier
        commands_resample[:, 1] *= 0.25 
        commands_resample[:, 2] *= 0.3 
        self._commands[:, :3] = self._commands[:, :3] * ~resample_time.unsqueeze(1).expand(-1, 3) + commands_resample * resample_time.unsqueeze(1).expand(-1, 3)

        # Stop
        rest_time = self.episode_length_buf >= self.max_episode_length - 50
        self._commands[:, :3] *= ~rest_time.unsqueeze(1).expand(-1, 3)        

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
            obs_cuncurrent_state_est = self._observation_noise_model(obs_cuncurrent_state_est)   

        # Saving data
        output_cuncurrent_state_est = self._robot.data.root_lin_vel_b
        self._cuncurrent_state_est_network.dataset.add_sample(obs_cuncurrent_state_est, output_cuncurrent_state_est)

        # Prediction
        num_episode_from_start = self.common_step_counter / 24. #self.max_episode_length #HACK this should be taken from rsl rl
        num_final_episode_from_start = 8000.
        if num_episode_from_start > self.cfg.cuncurrent_state_est_ep_saving_interval:
            prediction_cuncurrent_state_est = self._cuncurrent_state_est_network(obs_cuncurrent_state_est)
            linear_velocity_b = prediction_cuncurrent_state_est[:, :3]
        else:
            linear_velocity_b = self._robot.data.root_lin_vel_b

        # Train at some interval
        if num_episode_from_start % self.cfg.cuncurrent_state_est_ep_saving_interval == 0 and num_episode_from_start > self.cfg.cuncurrent_state_est_ep_saving_interval - 1:  # Adjust the interval as needed
            self._cuncurrent_state_est_network.train_network(batch_size=self.cfg.cuncurrent_state_est_batch_size, 
                                                            epochs=self.cfg.cuncurrent_state_est_train_epochs, 
                                                            learning_rate=self.cfg.cuncurrent_state_est_lr, device=self.device)
        if num_episode_from_start == num_final_episode_from_start - 10:
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
            obs = self._observation_noise_model(obs.clone())  
        
        outputs_rma = self._get_privileged_observation()

        self._rma_network.dataset.add_sample(obs, outputs_rma)

        # Prediction
        num_episode_from_start = self.common_step_counter / 24. #self.max_episode_length #HACK this should be taken from rsl rl
        num_final_episode_from_start = 8000.
        if num_episode_from_start > self.cfg.rma_ep_saving_interval:
            prediction_rma = self._rma_network(obs)
            obs_rma = prediction_rma
        else:
            obs_rma = outputs_rma

        # Train at some interval
        if num_episode_from_start % self.cfg.cuncurrent_state_est_ep_saving_interval == 0 and num_episode_from_start > self.cfg.rma_ep_saving_interval - 1:  # Adjust the interval as needed
            self._rma_network.train_network(batch_size=self.cfg.rma_batch_size, 
                                            epochs=self.cfg.rma_rma_train_epochs, 
                                            learning_rate=self.cfg.rma_lr, 
                                            device=self.device)
        if num_episode_from_start == num_final_episode_from_start - 10:
            # Save the network
            self._cuncurrent_state_est_network.save_network("cuncurrent_state_estimator.pth", self.device)
        
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


        obs_privileged = torch.cat(( 
                            hip_stiffness/default_stiffness, thigh_stiffness/default_stiffness, calf_stiffness/default_stiffness, #P gain
                            hip_damping/default_damping, thigh_damping/default_damping, calf_damping/default_damping, #D gain
                            #masses, inertias,
                            hip_static_friction, thigh_static_friction, calf_static_friction,  
                            hip_dynamic_friction, thigh_dynamic_friction, calf_dynamic_friction, 
                            hip_armature, thigh_armature, calf_armature) 
                        , dim=-1)
        return obs_privileged