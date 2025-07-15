# Description: Wrapper of the locomotion policy

# Authors:
# Giulio Turrisi

import time
import copy
import numpy as np
np.set_printoptions(precision=3, suppress=True)

from tqdm import tqdm
import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../")
sys.path.append(dir_path+"/../scripts/rsl_rl")

# Gym and Simulation related imports
from gym_quadruped.quadruped_env import QuadrupedEnv
from gym_quadruped.utils.quadruped_utils import LegsAttr


import onnxruntime as ort

policy_path = dir_path + "/../tested_policies/aliengo/8k_128_128_128_stop"
policy_path = policy_path + "/exported/policy.onnx"
policy = ort.InferenceSession(policy_path)

import torch


class LocomotionPolicyWrapper:
    def __init__(self, env):
        # Torque and desired joint vector
        self.tau = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        self.desired_joint_pos = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])

        # Torque limits
        tau_soft_limits_scalar = 0.9
        self.tau_limits = LegsAttr(
            FL=env.mjModel.actuator_ctrlrange[env.legs_tau_idx.FL]*tau_soft_limits_scalar,
            FR=env.mjModel.actuator_ctrlrange[env.legs_tau_idx.FR]*tau_soft_limits_scalar,
            RL=env.mjModel.actuator_ctrlrange[env.legs_tau_idx.RL]*tau_soft_limits_scalar,
            RR=env.mjModel.actuator_ctrlrange[env.legs_tau_idx.RR]*tau_soft_limits_scalar)
        

        # RL controller initialization -------------------------------------------------------------
        self.action_scale = 0.5
        self.rl_actions = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        self.past_rl_actions = np.zeros(env.mjModel.nu)
        
        self.default_joint_pos = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        self.default_joint_pos.FL = np.array([0, 0.9, -1.8])
        self.default_joint_pos.FR = np.array([0, 0.9, -1.8])
        self.default_joint_pos.RL = np.array([0, 0.9, -1.8])
        self.default_joint_pos.RR = np.array([0, 0.9, -1.8])


        self.RL_FREQ = 50  # Hz
        self.Kp = 25.
        self.Kd = 2.

        self.observation_space = 48

        self.use_clock_signal = True
        if(self.use_clock_signal):
            self.observation_space += 4


        self.step_freq = 1.4
        self.duty_factor = 0.65
        self.full_stance_phase_signal = (np.array([0.5, 1.0, 1.0, 0.5]) + self.step_freq * (1 / (self.RL_FREQ))) % 1.0
        self.phase_signal = np.array([0.5, 1.0, 1.0, 0.5])

        self.desired_clip_actions = 3.0

        self.use_action_filter = True


        self.use_observation_history = True
        self.history_length = 5
        if(self.use_observation_history):
            self.observation_space = self.observation_space * self.history_length
        single_observation_space = int(self.observation_space/self.history_length)
        self._observation_history = np.zeros((self.history_length, single_observation_space), dtype=np.float32)

        self.use_vision = False
        if(self.use_vision):
            self.observation_space = 235


    def compute_control(self, base_pos, base_ori_euler_xyz, base_quat_wxyz,
                        base_lin_vel, base_ang_vel, heading_orientation_SO3,
                        joints_pos, joints_vel,
                        ref_base_lin_vel, ref_base_ang_vel,
                        heightmap_data=None):

        # Update Observation ----------------------        
        # Get the projected gravity in the base frame
        GRAVITY_VEC_W = torch.tensor((0, 0, -9.81), dtype=torch.double)
        GRAVITY_VEC_W = GRAVITY_VEC_W / GRAVITY_VEC_W.norm(p=2, dim=-1).clamp(min=1e-9, max=None).unsqueeze(-1)
        q = torch.tensor(base_quat_wxyz).view(1, 4)
        v = GRAVITY_VEC_W.clone().detach().view(1, 3)
        q_w = q[..., 0]
        q_vec = q[..., 1:]
        a = v * (2.0 * q_w**2 - 1.0).unsqueeze(-1)
        b = torch.cross(q_vec, v, dim=-1) * q_w.unsqueeze(-1) * 2.0
        # for two-dimensional tensors, bmm is faster than einsum
        if q_vec.dim() == 2:
            c = q_vec * torch.bmm(q_vec.view(q.shape[0], 1, 3), v.view(q.shape[0], 3, 1)).squeeze(-1) * 2.0
        else:
            c = q_vec * torch.einsum("...i,...i->...", q_vec, v).unsqueeze(-1) * 2.0
        base_projected_gravity =  a - b + c
        base_projected_gravity = base_projected_gravity.numpy().flatten()
        

        # Get the reference base velocity in the world frame
        ref_base_lin_vel_h = heading_orientation_SO3.T@ref_base_lin_vel
        
            
        # Fill the observation vector
        joints_pos_delta = joints_pos - self.default_joint_pos
        obs = np.concatenate([
            base_lin_vel,
            base_ang_vel,
            base_projected_gravity,
            ref_base_lin_vel_h[0:2],
            [ref_base_ang_vel[2]],
            [joints_pos_delta.FL[0]], [joints_pos_delta.FR[0]], [joints_pos_delta.RL[0]], [joints_pos_delta.RR[0]],
            [joints_pos_delta.FL[1]], [joints_pos_delta.FR[1]], [joints_pos_delta.RL[1]], [joints_pos_delta.RR[1]],
            [joints_pos_delta.FL[2]], [joints_pos_delta.FR[2]], [joints_pos_delta.RL[2]], [joints_pos_delta.RR[2]],
            [joints_vel.FL[0]], [joints_vel.FR[0]], [joints_vel.RL[0]], [joints_vel.RR[0]],
            [joints_vel.FL[1]], [joints_vel.FR[1]], [joints_vel.RL[1]], [joints_vel.RR[1]],
            [joints_vel.FL[2]], [joints_vel.FR[2]], [joints_vel.RL[2]], [joints_vel.RR[2]],
            self.past_rl_actions.copy(),
        ])


        # Phase Signal
        if(self.use_clock_signal):
            self.phase_signal += self.step_freq * (1 / (self.RL_FREQ))
            self.phase_signal = self.phase_signal % 1.0
            obs = np.concatenate((obs, self.phase_signal), axis=0)

            commands = np.array([ref_base_lin_vel_h[0], ref_base_lin_vel_h[1], ref_base_ang_vel[2]], dtype=np.float32)
            if(np.linalg.norm(commands) < 0.01):
                obs[48:52] = -1.0
                #self.phase_signal = copy.deepcopy(self.full_stance_phase_signal)
        
        if(self.use_observation_history):
            #the bottom element is the newest observation!!
            past = self._observation_history[1:,:]
            self._observation_history = np.vstack((past, obs))
            obs = self._observation_history.flatten()

        
        if(self.use_vision):
            # Rotate, the first element for Isaac is bottom right, for us bottom up
            heightmap_data_isaac_convention = np.zeros((heightmap_data[..., 2].shape[0]*heightmap_data[..., 2].shape[1],), dtype=np.float32)
            for j in range(heightmap_data[..., 2].shape[1]):
                heightmap_data_isaac_convention[j*heightmap_data[..., 2].shape[0]:(j+1)*heightmap_data[..., 2].shape[0]] = heightmap_data[..., 2][:, j, 0][::-1]
            
            #print("heightmap_data[..., 2][:, j, 0]: ", heightmap_data[..., 2][:, 0, 0])
            #print("heightmap_data: ", heightmap_data_isaac_convention)
            height_data = (base_pos[2] - heightmap_data_isaac_convention - 0.5)
            height_data = height_data.clip(-1.0, 1.0)
            obs = np.concatenate((obs, height_data), axis=0)
            
        obs = obs.reshape(1, -1)
        obs = obs.astype(np.float32)
        rl_action_temp = policy.run(None, {'obs': obs})[0][0]
        rl_action_temp = np.clip(rl_action_temp, -self.desired_clip_actions, self.desired_clip_actions)
        
        if(self.use_action_filter):
            alpha = 0.8
            past_rl_actions_temp = self.past_rl_actions.copy()
            self.past_rl_actions = rl_action_temp.copy()
            rl_action_temp = alpha * rl_action_temp + (1-alpha) * past_rl_actions_temp
        else:
            self.past_rl_actions = rl_action_temp.copy()


        self.rl_actions.FL = np.array([rl_action_temp[0], rl_action_temp[4], rl_action_temp[8]])
        self.rl_actions.FR = np.array([rl_action_temp[1], rl_action_temp[5], rl_action_temp[9]])
        self.rl_actions.RL = np.array([rl_action_temp[2], rl_action_temp[6], rl_action_temp[10]])
        self.rl_actions.RR = np.array([rl_action_temp[3], rl_action_temp[7], rl_action_temp[11]])


        # Impedence Loop
        self.desired_joint_pos.FL = self.default_joint_pos.FL + self.rl_actions.FL*self.action_scale
        self.desired_joint_pos.FR = self.default_joint_pos.FR + self.rl_actions.FR*self.action_scale
        self.desired_joint_pos.RL = self.default_joint_pos.RL + self.rl_actions.RL*self.action_scale
        self.desired_joint_pos.RR = self.default_joint_pos.RR + self.rl_actions.RR*self.action_scale

        
        return self.desired_joint_pos

