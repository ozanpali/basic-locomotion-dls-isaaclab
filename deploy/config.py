import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../")
sys.path.append(dir_path+"/../scripts/rsl_rl")

robot = 'aliengo'  # 'aliengo', 'go1', 'go2', 'b2', 'hyqreal1', 'hyqreal2', 'mini_cheetah' 
scene = 'random_boxes'  # flat, random_boxes, random_pyramids, perlin

policy_folder_path = dir_path + "/../tested_policies/" + robot + "/8k_128_128_128_aliengo_stop_and_go_correct_offset"
#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se"


# ----------------------------------------------------------------------------------------------------------------
if(robot == "aliengo"):
    Kp_walking = 25.
    Kd_walking = 2.

    Kp_stand_up_and_down = 25.
    Kd_stand_up_and_down = 2.

elif(robot == "go2"):
    Kp_walking = 25.
    Kd_walking = 2.

    Kp_stand_up_and_down = 25.
    Kd_stand_up_and_down = 2.
elif(robot == "b2"):
    Kp_walking = 20.
    Kd_walking = 1.5

    Kp_stand_up_and_down = 25.
    Kd_stand_up_and_down = 2.
elif(robot == "hyqreal2"):
    Kp_walking = 175.
    Kd_walking = 20.

    Kp_stand_up_and_down = 25.
    Kd_stand_up_and_down = 2.
else:
    raise ValueError(f"Robot {robot} not supported")

# ----------------------------------------------------------------------------------------------------------------

# Load specific training parameters
import yaml 
with open(policy_folder_path + "/params/env.yaml", "r") as file:
    env = yaml.unsafe_load(file)


RL_FREQ = 1./(env["sim"]["dt"]*env["decimation"])  # Hz, frequency of the RL controller
action_scale = env["action_scale"]  # Scale of the RL actions, used to scale the actions from the RL policy


use_clip_actions = True  # If True, clip the actions to avoid too high torques
clip_actions = env["desired_clip_actions"]  # Clip the actions to avoid too high torques


observation_space = env["single_observation_space"]  # Number of observations in the RL policy
use_observation_history = env["use_observation_history"]  # If True, use the history of the actions to compute the RL policy
history_length = env["history_length"]  # Length of the history of the actions to be used in the RL policy


use_clock_signal = env["use_clock_signal"]  # If True, use the clock signal in the RL policy


use_vision = False  # If True, use the vision observations in the RL policy
if(use_vision):
    resolution_heightmap = env["height_scanner"]["pattern_cfg"]["resolution"]  # Resolution of the heightmap in meters
    size_x_heightmap = env["height_scanner"]["pattern_cfg"]["size"][0]  # Size of the heightmap in meters
    size_y_heightmap = env["height_scanner"]["pattern_cfg"]["size"][1]  # Size of the heightmap in meters


use_imu = env["use_imu"]
use_rma = env["use_rma"]
use_cuncurrent_state_est = env["use_cuncurrent_state_est"]
cuncurrent_state_est_network_path = policy_folder_path + "/exported/cuncurrent_state_estimator.pth"