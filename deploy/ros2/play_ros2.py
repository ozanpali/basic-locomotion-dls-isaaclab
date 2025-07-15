# Description: This script is used to run the policy on the real robot

# Authors:
# Giulio Turrisi

import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Joy
from dls2_msgs.msg import BaseStateMsg, BlindStateMsg, ControlSignalMsg, TrajectoryGeneratorMsg

import time
import numpy as np
np.set_printoptions(precision=3, suppress=True)

import threading

import copy

# Gym and Simulation related imports
import mujoco
from gym_quadruped.quadruped_env import QuadrupedEnv
from gym_quadruped.utils.quadruped_utils import LegsAttr

import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../")

# Locomotion Policy imports
from locomotion_policy_wrapper import LocomotionPolicyWrapper

# Set the priority of the process
pid = os.getpid()
print("PID: ", pid)
os.system("renice -n -21 -p " + str(pid))
os.system("echo -20 > /proc/" + str(pid) + "/autogroup")
#for real time, launch it with chrt -r 99 python3 run_controller.py

USE_MUJOCO_RENDER = False
USE_MUJOCO_SIMULATION = False

USE_FIXED_LOOP_TIME = False
USE_SATURATED_LOOP_TIME = False

USE_SCHEDULER = True # This enable a call to the run function every tot seconds by using a ros2 timer
RL_FREQ = 50 # this is only valid if USE_SCHEDULER is True

USE_SMOOTH_VELOCITY = True

class Quadruped_RL_Collection_Node(Node):
    def __init__(self):
        super().__init__('Basic_Locomotion_DLS_IsaacLab_Node')
        # Subscribers and Publishers
        self.subscription_base_state = self.create_subscription(BaseStateMsg,"/dls2/base_state", self.get_base_state_callback, 1)
        self.subscription_blind_state = self.create_subscription(BlindStateMsg,"/dls2/blind_state", self.get_blind_state_callback, 1)
        self.subscription_joy = self.create_subscription(Joy,"joy", self.get_joy_callback, 1)
        self.publisher_trajectory_generator = self.create_publisher(TrajectoryGeneratorMsg,"dls2/trajectory_generator", 1)
        if(USE_SCHEDULER):
            self.timer = self.create_timer(1.0/RL_FREQ, self.compute_rl_control)


        # Safety check to not do anything until a first base and blind state are received
        self.first_message_base_arrived = False
        self.first_message_joints_arrived = False 

        # Timing stuff
        self.loop_time = 0.002
        self.last_start_time = None

        # Base State
        self.position = np.zeros(3)
        self.orientation = np.zeros(4)
        self.linear_velocity = np.zeros(3)
        self.angular_velocity = np.zeros(3)

        # Blind State
        self.joint_positions = np.array([0.0, 1.21, -2.794, 0.0, 1.21, -2.794, 0.0, 1.21, -2.794, 0.0, 1.21, -2.794])
        self.joint_velocities = np.zeros(12)
        self.feet_contact = np.zeros(4)

        # Mujoco env
        robot_name = "aliengo"
        scene_name = "flat" #random-boxes
        simulation_dt = 0.002


        # Create the quadruped robot environment -----------------------------------------------------------
        self.env = QuadrupedEnv(
            robot=robot_name,
            scene=scene_name,
            sim_dt=simulation_dt,
            base_vel_command_type="human",  # "forward", "random", "forward+rotate", "human"
        )
        self.env.reset(random=False)


        
        self.last_render_time = time.time()
        if USE_MUJOCO_RENDER:
            self.env.render()

        
        # Initialization of variables used in the main control loop --------------------------------
        self.locomotion_policy = LocomotionPolicyWrapper(env=self.env)


        self.stand_up_and_down_actions = LegsAttr(*[np.zeros((1, int(self.env.mjModel.nu/4))) for _ in range(4)])
        self.stand_up_and_down_actions.FL = np.array([0.,   1.201, -2.791])
        self.stand_up_and_down_actions.FR = np.array([0.,   1.201, -2.791])
        self.stand_up_and_down_actions.RL = np.array([0.,   1.201, -2.791])
        self.stand_up_and_down_actions.RR = np.array([0.,   1.201, -2.791])
        self.Kp_stand_up_and_down = 25.
        self.Kd_stand_up_and_down = 2.

        # Interactive Command Line ----------------------------
        from console import Console
        self.console = Console(controller_node=self)
        thread_console = threading.Thread(target=self.console.interactive_command_line)
        thread_console.daemon = True
        thread_console.start()

    
    def get_joy_callback(self, msg):
        """
        Callback function to handle joystick input. Joystick used is a 
        Logitech F710 Wireless Gamepad, with D modality and Model Light OFF.
        """
        self.env._ref_base_lin_vel_H[0] = msg.axes[1]/3.5  # Forward/Backward
        self.env._ref_base_lin_vel_H[1] = msg.axes[0]/3.5  # Left/Right
        self.env._ref_base_ang_yaw_dot = msg.axes[3]/2.  # Yaw


        #kill the node if the button is pressed
        if msg.buttons[8] == 1:
            self.get_logger().info("Joystick button pressed, shutting down the node.")
            self.destroy_node()
            rclpy.shutdown()
            exit(0)




    def get_base_state_callback(self, msg):
        
        self.position = np.array(msg.position)
        # For the quaternion, the order is [w, x, y, z] on mujoco, and [x, y, z, w] on DLS2
        self.orientation = np.roll(np.array(msg.orientation), 1)
        self.linear_velocity = np.array(msg.linear_velocity)
        # For the angular velocity, mujoco is in the base frame, and DLS2 is in the world frame
        self.angular_velocity = np.array(msg.angular_velocity) 

        self.first_message_base_arrived = True



    def get_blind_state_callback(self, msg):
        
        self.joint_positions = np.array(msg.joints_position)
        self.joint_velocities = np.array(msg.joints_velocity)
        self.feet_contact = np.array(msg.feet_contact)

        # Fix convention DLS2
        self.joint_positions[0] = -self.joint_positions[0]
        self.joint_positions[6] = -self.joint_positions[6]
        self.joint_velocities[0] = -self.joint_velocities[0]
        self.joint_velocities[6] = -self.joint_velocities[6]

        self.first_message_joints_arrived = True

        if(not USE_SCHEDULER):
            if(self.last_start_time is not None):
                start_time = time.perf_counter()
                if(start_time - self.last_start_time > 1./RL_FREQ):
                    self.compute_rl_control()
            else:
                self.compute_rl_control()
        


    def compute_rl_control(self):
        # Update the loop time
        if(USE_FIXED_LOOP_TIME):
            simulation_dt = 1./RL_FREQ
            start_time = time.perf_counter()
            if(self.last_start_time is not None):
                self.loop_time = (start_time - self.last_start_time)
            self.last_start_time = start_time
        elif(USE_SATURATED_LOOP_TIME):
            start_time = time.perf_counter()
            if(self.last_start_time is not None):
                self.loop_time = (start_time - self.last_start_time)
            self.last_start_time = start_time
            simulation_dt = self.loop_time
            if(simulation_dt > 1./(RL_FREQ-10)):
                simulation_dt = 0.025
        else:
            start_time = time.perf_counter()
            if(self.last_start_time is not None):
                self.loop_time = (start_time - self.last_start_time)
            self.last_start_time = start_time
            simulation_dt = self.loop_time

        # Safety check to not do anything until a first base and blind state are received
        if(not USE_MUJOCO_SIMULATION and self.first_message_base_arrived==False and self.first_message_joints_arrived==False):
            return

        old_base_lin_vel = self.env.base_lin_vel(frame='base')

        # Update the mujoco model
        if(not USE_MUJOCO_SIMULATION):
            self.env.mjData.qpos[0:3] = copy.deepcopy(self.position)
            self.env.mjData.qpos[3:7] = copy.deepcopy(self.orientation)
            self.env.mjData.qvel[0:3] = copy.deepcopy(self.linear_velocity)
            self.env.mjData.qvel[3:6] = copy.deepcopy(self.angular_velocity)
            self.env.mjData.qpos[7:] = copy.deepcopy(self.joint_positions)
            self.env.mjData.qvel[6:] = copy.deepcopy(self.joint_velocities)
            self.env.mjModel.opt.timestep = simulation_dt
            mujoco.mj_forward(self.env.mjModel, self.env.mjData)     

        env = self.env
        locomotion_policy = self.locomotion_policy
        
        qpos, qvel = env.mjData.qpos, env.mjData.qvel
        base_lin_vel = env.base_lin_vel(frame='base')
        base_ang_vel = env.base_ang_vel(frame='base')
        base_ori_euler_xyz = env.base_ori_euler_xyz
        heading_orientation_SO3 = env.heading_orientation_SO3
        base_quat_wxyz = qpos[3:7]
        base_pos = env.base_pos

        if(USE_SMOOTH_VELOCITY):
            base_lin_vel = 0.5*base_lin_vel + 0.5*old_base_lin_vel

        joints_pos = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        joints_pos.FL = qpos[env.legs_qpos_idx.FL]
        joints_pos.FR = qpos[env.legs_qpos_idx.FR]
        joints_pos.RL = qpos[env.legs_qpos_idx.RL]
        joints_pos.RR = qpos[env.legs_qpos_idx.RR]
    
        joints_vel = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        joints_vel.FL = qvel[env.legs_qvel_idx.FL]
        joints_vel.FR = qvel[env.legs_qvel_idx.FR]
        joints_vel.RL = qvel[env.legs_qvel_idx.RL]
        joints_vel.RR = qvel[env.legs_qvel_idx.RR]
        ref_base_lin_vel, ref_base_ang_vel = env.target_base_vel()


        if(self.console.isDown):
            desired_joint_pos = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
            desired_joint_pos.FL = self.stand_up_and_down_actions.FL
            desired_joint_pos.FR = self.stand_up_and_down_actions.FR
            desired_joint_pos.RL = self.stand_up_and_down_actions.RL
            desired_joint_pos.RR = self.stand_up_and_down_actions.RR

            # Impedence Loop
            Kp = self.Kp_stand_up_and_down
            Kd = self.Kd_stand_up_and_down
            

        elif(self.console.isRLActivated):

            desired_joint_pos = locomotion_policy.compute_control(base_pos=base_pos, 
                                                                    base_ori_euler_xyz=base_ori_euler_xyz, base_quat_wxyz=base_quat_wxyz,
                                                                    base_lin_vel=base_lin_vel, base_ang_vel=base_ang_vel,
                                                                    heading_orientation_SO3=heading_orientation_SO3,
                                                                    joints_pos=joints_pos, joints_vel=joints_vel,
                                                                    ref_base_lin_vel=ref_base_lin_vel, ref_base_ang_vel=ref_base_ang_vel)
            
            # Impedence Loop
            Kp = locomotion_policy.Kp
            Kd = locomotion_policy.Kd


        else:
            return


        
        if USE_MUJOCO_SIMULATION:
            for j in range(10): #Hardcoded for now, if RL is 50Hz, this runs the simulation at 500Hz
                joints_pos.FL = qpos[env.legs_qpos_idx.FL]
                joints_pos.FR = qpos[env.legs_qpos_idx.FR]
                joints_pos.RL = qpos[env.legs_qpos_idx.RL]
                joints_pos.RR = qpos[env.legs_qpos_idx.RR]
            
                joints_vel.FL = qvel[env.legs_qvel_idx.FL]
                joints_vel.FR = qvel[env.legs_qvel_idx.FR]
                joints_vel.RL = qvel[env.legs_qvel_idx.RL]
                joints_vel.RR = qvel[env.legs_qvel_idx.RR]

                error_joints_pos = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
                error_joints_pos.FL = desired_joint_pos.FL - joints_pos.FL
                error_joints_pos.FR = desired_joint_pos.FR - joints_pos.FR
                error_joints_pos.RL = desired_joint_pos.RL - joints_pos.RL
                error_joints_pos.RR = desired_joint_pos.RR - joints_pos.RR
                
                tau = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
                tau.FL = Kp * (error_joints_pos.FL) - Kd * joints_vel.FL
                tau.FR = Kp * (error_joints_pos.FR) - Kd * joints_vel.FR
                tau.RL = Kp * (error_joints_pos.RL) - Kd * joints_vel.RL
                tau.RR = Kp * (error_joints_pos.RR) - Kd * joints_vel.RR

                # Limit tau between tau_limits
                for leg in ["FL", "FR", "RL", "RR"]:
                    tau_min, tau_max = locomotion_policy.tau_limits[leg][:, 0], locomotion_policy.tau_limits[leg][:, 1]
                    tau[leg] = np.clip(tau[leg], tau_min, tau_max)
                
                action = np.zeros(self.env.mjModel.nu)
                action[self.env.legs_tau_idx.FL] = tau.FL.reshape((3,))
                action[self.env.legs_tau_idx.FR] = tau.FR.reshape((3,))
                action[self.env.legs_tau_idx.RL] = tau.RL.reshape((3,))
                action[self.env.legs_tau_idx.RR] = tau.RR.reshape((3,))
                self.env.step(action=action)

        

        # Fix convention DLS2 and send PD target
        desired_joint_pos.FL[0] = -desired_joint_pos.FL[0]
        desired_joint_pos.RL[0] = -desired_joint_pos.RL[0] 

        trajectory_generator_msg = TrajectoryGeneratorMsg()
        trajectory_generator_msg.stance_legs[0] = not self.console.isRLActivated
        trajectory_generator_msg.stance_legs[1] = not self.console.isRLActivated
        trajectory_generator_msg.stance_legs[2] = not self.console.isRLActivated
        trajectory_generator_msg.stance_legs[3] = not self.console.isRLActivated
        trajectory_generator_msg.joints_position = np.concatenate([desired_joint_pos.FL, desired_joint_pos.FR, desired_joint_pos.RL, desired_joint_pos.RR], axis=0).flatten()
        
        desired_joint_vel = LegsAttr(*[np.zeros((1, int(env.mjModel.nu/4))) for _ in range(4)])
        trajectory_generator_msg.joints_velocity = np.concatenate([desired_joint_vel.FL, desired_joint_vel.FR, desired_joint_vel.RL, desired_joint_vel.RR], axis=0).flatten()

        #trajectory_generator_msg.kp = np.ones(12)*Kp
        #trajectory_generator_msg.kd = np.ones(12)*Kd
        self.publisher_trajectory_generator.publish(trajectory_generator_msg)
        
        
        
        # Render the simulation -----------------------------------------------------------------------------------
        if USE_MUJOCO_RENDER:
            RENDER_FREQ = 30
            # Render only at a certain frequency -----------------------------------------------------------------
            if time.time() - self.last_render_time > 1.0 / RENDER_FREQ or self.env.step_num == 1:
                self.env.render()
                self.last_render_time = time.time()




#---------------------------
if __name__ == '__main__':
    print('Hello from quadruped_rl_collection.')
    rclpy.init()
    quadruped_rl_collection_node = Quadruped_RL_Collection_Node()

    rclpy.spin(quadruped_rl_collection_node)
    quadruped_rl_collection_node.destroy_node()
    rclpy.shutdown()

    print("Quadruped-RL-Collection node is stopped")
    exit(0)