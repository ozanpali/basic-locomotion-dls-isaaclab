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
    Kp_walking = 21.5
    Kd_walking = 3.5

    Kp_stand_up_and_down = 25.
    Kd_stand_up_and_down = 2.

elif(robot == "go2"):
    Kp_walking = 21.5
    Kd_walking = 3.5

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
policy_folder_path = dir_path + "/../tested_policies/" + robot + "/aliengo_symmetricactor"
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
"""
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-15-12_airtime0.5_mujoco_slide_desiredfeetheight15cm_desiredbaseheight35cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-27-37_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_15-49-19_locomotioneditedwithremote"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_16-18-38_robusteditedfromlocomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_16-31-03_robusteditedfromlocomotionAliengofromloco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-20-04_new_airtime_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-47-17_locomotion_airtime_mujoco"
"""
#good 4 leg with robust finally.
"""
"""
"""
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_18-11-31_Robust_airtime_mujoco_desiredfeetheight15cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-08_17-59-58_Robust_airtime_mujoco_500iteration"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_11-13-45_Robust_airtime_mujoco_desiredfeetheight25cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_11-46-17_Robust_airtime0.8_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_13-33-37_Robust_airtime0.5_mujoco_desiredfeetheight5cm"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_12-26-38_Robust_airtime0.5_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_14-25-59_newpull9oct_airtime0.5_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_15-22-42_Lortime0.7_mujoco_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_14-37-35_airtime0.7_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_15-38-13_airtime0.7_mujoco_locomotionfixed"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_16-44-07_airtime0.7_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_17-00-51_airtime0.7fixed_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_17-11-22_airtime1.0_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_17-25-38_airtime0.5_mujoco"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_17-48-47_airtime0.5_mujoco_asymmetricppoTrue"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_18-11-45_copypastedLocoAliengoRslrlppofromLocomotiontoRobust"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_00-10-17_soloLocomotionLetsSeeeee"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_01-05-18_locomotionClearancePeriodicSuggestion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_10-42-04_AirtimeClearanceSlide"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_11-03-31_AirtimeClearancemujocoClearanceSlide"


policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_14-53-17_ForkRobust_1000Iter_8192_clearance_slide_feettohipbase"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_15-40-34_ForkRobust_600Iter_8192_clearance_slide_feettohip"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_16-30-18_ForkRobust_600Iter_8192_clearanceOver0.05_slide_feettohip"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_15-40-34_ForkRobust_600Iter_8192_clearance_slide_feettohip"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_17-10-14_ForkRobust_600Iter_8192_clearanceOver0.001scale0.5_slide_feettohip"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-15_16-40-39_ForkRobust_600Iter_8192_clearanceOver0.05_slide_feettohip"
"""


"""



#sag pc
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-09_18-03-54_sagpc_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_11-36-10_sagpc_locomotion"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_11-48-26_sagpcAirtimeClearanceClearancemujocoSlide"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_12-10-10_RightpcAirtimeClearancemujocoSlide"
policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-10_13-26-36_RightpcOzansrepoRobustAirtimeMujocoSlideIteration1000"




# after meeting with giulio 16th oct
"""

#policy_folder_path = "/home/dlsuser/isaaclab_ws_home/basic-locomotion-dls-isaaclab/logs/rsl_rl/flat_direct/2025-10-17_13-45-35_LPC_1000Iter_8192Env_3a72c548_fl_calf_bend_airtime_0.5"
#policy_folder_path = parent_dir + "/"
#policy_folder_path += "logs/rsl_rl/flat_direct/2025-10-17_11-17-32_LPC_1000Iter_8192_clearance"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_16-23-09_LPC_1000Iter_8192Env_clearance_slide"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_17-42-48_LPC_2Iter_2Env_97e0efba_tripod_test2_bend"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_17-43-03_LPC_2Iter_2Env_18ad6995_tripod_test3_swing"
#kinda lifs
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_19-03-07_LPC_1000Iter_8192Env_18ad6995_tripod_test3_swing"
#better then before
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_19-58-46_LPC_1000Iter_8192Env_a4a33723_tripod_test5_maintenance_swing"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_20-26-22_LPC_1000Iter_8192Env_8c6cfa6a_tripod_test6_bend_swing"
#properly lifts but touches.
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_20-53-57_LPC_1000Iter_8192Env_8ba738cc_tripod_test7_maintenance_bend_swing"
#lets remove airtime for FL




#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/aliengo_stop_and_go_correct_offset"

#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/go2_5asymm"

#cuncurrent_state_est_network = policy_folder_path + "/exported/cuncurrent_state_estimator.pth"
#rma_network = policy_folder_path + "/exported/rma.pth"

# Load specific training parameters
import yaml 
with open(policy_folder_path + "/params/env.yaml", "r") as file:
    training_env = yaml.unsafe_load(file)

use_vision = False  # If True, use the vision observations in the RL policy #TODO add in yaml
