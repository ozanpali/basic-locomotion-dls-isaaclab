import sys
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../")
sys.path.append(dir_path+"/../scripts/rsl_rl")

robot = 'aliengo'  # 'aliengo', 'go1', 'go2', 'b2', 'hyqreal1', 'hyqreal2', 'mini_cheetah' 
scene = 'flat'  # flat, random_boxes, random_pyramids, perlin
"""
policy_path = dir_path + "/../tested_policies/" + robot + "/8k_128_128_128_aliengo_stop_and_go_correct_offset" + "/exported/policy.onnx"
#policy_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se" + "/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-22_19-10-57_FLAir/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_13-51-00_FLAir/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-13-00_FLAir_alsostdairtime/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-29-10_FLAir/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-44-06_FLAir/exported/policy.onnx"
#policy_path = "/home/iit.local/gturrisi/isaaclab_ws_home/basic-locomotion-dls-isaaclab/tested_policies/hyqreal/2025-07-23_09-19-46_8k_128_128_128_hyq/exported/policy.onnx"
#policy_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se" + "/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_15-03-42_Originalfromgiulio??/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_15-40-49_newtripodtryfromgiulio/exported/policy.onnx"
#freq 1 is bad
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_16-28-30_Originalfromgiulio_freq1/exported/policy.onnx"
#freq 2 is bad
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_17-30-38_Originalfromgiulio_freq2/exported/policy.onnx"
#policy_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se" + "/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-22_19-10-57_FLAir/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_13-51-00_FLAir/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-13-00_FLAir_alsostdairtime/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-29-10_FLAir/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_14-44-06_FLAir/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_15-05-04_FLAir/exported/policy.onnx"
# crawl not walking...
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_15-19-25_FLAir/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_15-52-59_FLAir_Slide/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_16-38-11_FLAir10/exported/policy.onnx"

policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_17-06-43_FLAir10trot/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-23_17-26-37_FLAir1trot/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_12-21-14_FLAirSt10Stepfreq1/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_13-17-14_FLAirSt10Stepfreq1.5/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_14-17-14_FLAir10_alsoStdAirtime_slide_Stepfreq1.4/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-24_14-42-46_Standart_freq1.4/exported/policy.onnx"

policy_path = dir_path + "/../tested_policies/" + robot + "/8k_128_128_128_aliengo_stop_and_go_correct_offset" + "/exported/policy.onnx"
#policy_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se" + "/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_12-08-55_deneme26sept/exported/policy.onnx"
#accidentally removed FL swing so useless
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_12-46-58_deneme26sept_duty0.65/exported/policy.onnx"
# fixed it
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_13-21-06_deneme26sept_duty0.65fixed/exported/policy.onnx"
# height clearance tanh x3
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_13-53-43_foot_velocity_tanh_x3/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_14-19-59_fvtx1_airtime0.75/exported/policy.onnx"
#policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_14-41-05_fvtx1airtime750ms/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_16-32-00_4Leg_0.2FLRR_0.5FRRL/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_16-48-34_4Leg_0.1FLRR_0.7FRRL/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_17-46-51_4Leg_0.5FLRR_0.2FRRL_addedmujoco/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_18-58-22_4Leg_0.2FLRR_0.2FRRL_addedmujoco/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_17-03-39_4Leg_0.5FLRR_0.5FRRL/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-26_17-29-56_4Leg_0.5FLRR_0.5FRRL_addedmujoco/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-28_14-18-09_4Leg_0.5FLRR_0.5FRRL_addedmujoco_heighclearancedefault/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-09-28_14-58-54_4Leg_stdairtime_addedmujoco_heighclearancedefault/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-07_22-33-53_pullcheck_justclearance/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-07-20_airtime_mujoco_slide/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-25-09_airtime_mujoco_slide/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-42-32_airtime0.2_mujoco_slide/exported/policy.onnx"

policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-14-22_airtime0.2_mujoco_slide_desiredfeetheight25cm/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-32-32_airtime0.2_mujoco_slide_desiredfeetheight35cm/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-41-36_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotion/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-00-09_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-35-34_airtime0.2_mujoco_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented/exported/policy.onnx"
policy_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-50-19_airtime0.7_mujoco_desiredfeetheight5cm_desiredbaseheight25cm/exported/policy.onnx"
"""

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

    Kp_stand_up_and_down = 175.
    Kd_stand_up_and_down = 20.
else:
    raise ValueError(f"Robot {robot} not supported")

# ----------------------------------------------------------------------------------------------------------------

"""
policy_folder_path = dir_path + "/../tested_policies/" + robot + "/8k_128_128_128_aliengo_stop_and_go_correct_offset"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-50-19_airtime0.7_mujoco_desiredfeetheight5cm_desiredbaseheight25cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-07_22-33-53_pullcheck_justclearance"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-07-20_airtime_mujoco_slide"
#sliding
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-25-09_airtime_mujoco_slide"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_11-42-32_airtime0.2_mujoco_slide"

policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-14-22_airtime0.2_mujoco_slide_desiredfeetheight25cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-32-32_airtime0.2_mujoco_slide_desiredfeetheight35cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_12-41-36_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-00-09_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-35-34_airtime0.2_mujoco_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_14-50-19_airtime0.7_mujoco_desiredfeetheight5cm_desiredbaseheight25cm"
#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se"
"""
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-15-12_airtime0.5_mujoco_slide_desiredfeetheight15cm_desiredbaseheight35cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-27-37_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-49-19_locomotioneditedwithremote"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_16-18-38_robusteditedfromlocomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_16-31-03_robusteditedfromlocomotionAliengofromloco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-20-04_new_airtime_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-47-17_locomotion_airtime_mujoco"
#good 4 leg with robust finally.
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_18-11-31_Robust_airtime_mujoco_desiredfeetheight15cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-59-58_Robust_airtime_mujoco_500iteration"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_11-13-45_Robust_airtime_mujoco_desiredfeetheight25cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_11-46-17_Robust_airtime0.8_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_12-26-38_Robust_airtime0.5_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_13-33-37_Robust_airtime0.5_mujoco_desiredfeetheight5cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_14-25-59_newpull9oct_airtime0.5_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_15-22-42_Lortime0.7_mujoco_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_14-37-35_airtime0.7_mujoco"




cuncurrent_state_est_network = policy_folder_path + "/exported/cuncurrent_state_estimator.pth"
rma_network = policy_folder_path + "/exported/rma.pth"

# Load specific training parameters
import yaml 
with open(policy_folder_path + "/params/env.yaml", "r") as file:
    training_env = yaml.unsafe_load(file)

use_vision = False  # If True, use the vision observations in the RL policy #TODO add in yaml
