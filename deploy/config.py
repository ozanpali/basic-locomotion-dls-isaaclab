from selectors import _PollLikeSelector
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
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_14-50-19_airtime0.7_mujoco_desiredfeetheight5cm_desiredbaseheight25cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-07_22-33-53_pullcheck_justclearance"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_11-07-20_airtime_mujoco_slide"
#sliding
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_11-25-09_airtime_mujoco_slide"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_11-42-32_airtime0.2_mujoco_slide"

policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_12-14-22_airtime0.2_mujoco_slide_desiredfeetheight25cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_12-32-32_airtime0.2_mujoco_slide_desiredfeetheight35cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_12-41-36_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_14-00-09_airtime0.2_mujoco_slide_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_14-35-34_airtime0.2_mujoco_desiredfeetheight35cmfromlocomotionintegrated3legrewardbutcommented"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_14-50-19_airtime0.7_mujoco_desiredfeetheight5cm_desiredbaseheight25cm"
#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/2025-09-07_19-13-16_go2_cuncurrent_se"
"""
"""
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_15-15-12_airtime0.5_mujoco_slide_desiredfeetheight15cm_desiredbaseheight35cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_15-27-37_locomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_15-49-19_locomotioneditedwithremote"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_16-18-38_robusteditedfromlocomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_16-31-03_robusteditedfromlocomotionAliengofromloco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_17-20-04_new_airtime_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_17-47-17_locomotion_airtime_mujoco"
"""
#good 4 leg with robust finally.
"""
"""
"""
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_18-11-31_Robust_airtime_mujoco_desiredfeetheight15cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-08_17-59-58_Robust_airtime_mujoco_500iteration"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_11-13-45_Robust_airtime_mujoco_desiredfeetheight25cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_11-46-17_Robust_airtime0.8_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_13-33-37_Robust_airtime0.5_mujoco_desiredfeetheight5cm"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_12-26-38_Robust_airtime0.5_mujoco_desiredfeetheight25cmfixed"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_14-25-59_newpull9oct_airtime0.5_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_15-22-42_Lortime0.7_mujoco_locomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_14-37-35_airtime0.7_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_15-38-13_airtime0.7_mujoco_locomotionfixed"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_16-44-07_airtime0.7_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_17-00-51_airtime0.7fixed_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_17-11-22_airtime1.0_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_17-25-38_airtime0.5_mujoco"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_17-48-47_airtime0.5_mujoco_asymmetricppoTrue"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_18-11-45_copypastedLocoAliengoRslrlppofromLocomotiontoRobust"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_00-10-17_soloLocomotionLetsSeeeee"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_01-05-18_locomotionClearancePeriodicSuggestion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_10-42-04_AirtimeClearanceSlide"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_11-03-31_AirtimeClearancemujocoClearanceSlide"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_14-53-17_ForkRobust_1000Iter_8192_clearance_slide_feettohipbase"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_15-40-34_ForkRobust_600Iter_8192_clearance_slide_feettohip"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_16-30-18_ForkRobust_600Iter_8192_clearanceOver0.05_slide_feettohip"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_15-40-34_ForkRobust_600Iter_8192_clearance_slide_feettohip"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_17-10-14_ForkRobust_600Iter_8192_clearanceOver0.001scale0.5_slide_feettohip"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-15_16-40-39_ForkRobust_600Iter_8192_clearanceOver0.05_slide_feettohip"
"""


"""



#sag pc
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-09_18-03-54_sagpc_locomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_11-36-10_sagpc_locomotion"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_11-48-26_sagpcAirtimeClearanceClearancemujocoSlide"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_12-10-10_RightpcAirtimeClearancemujocoSlide"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-10_13-26-36_RightpcOzansrepoRobustAirtimeMujocoSlideIteration1000"




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
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_23-03-50_LPC_1000Iter_8192Env_97f48f32_individual_airtime_flrr_0.5_frrl_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_23-31-38_LPC_1000Iter_8192Env_fd06cded_individual_airtime_flrr_0.5_frrl_0.3_fl_calf_target_2.5"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-17_23-59-30_LPC_1000Iter_8192Env_6a7a9b15_individual_airtime_flrr_0.5_frrl_0.3_fl_calf_target_2.5_maintenance_bend_swing"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-18_00-27-03_LPC_1000Iter_8192Env_9b8cb782_individual_airtime_rr_0.5_frrl_0.3_fl_calf_target_2.5_maintenance_bend_swing"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_15-34-36_LPC_1000Iter_8192Env_a6249f35_maintenance_bend_swing_no_airtime"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_16-24-09_LPC_1000Iter_8192Env_f9ae6c8b_airtime_fl_failure_reward_swing_punish_touch_maintenance_bend_swing_clearance_v2"
# cannot turn right
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_19-10-52_LPC_2000Iter_8192Env_42495d6e_airtime_fl_failure_maintenance_bend"
#bad
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_20-30-02_LPC_2000Iter_8192Env_ae69b405_airtime_fl_failure_maintenance_swing"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_23-08-19_LPC_2000Iter_8192Env_60d61d08_airtime_fl_failure_maintenance_bend_swing"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_21-49-40_LPC_2000Iter_8192Env_770c6bec_airtime_fl_failure_bend_swing"


#maintenance is not keeping the leg up enough
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_20-01-20_LPC_2000Iter_8192Env_0c19c2df_airtime_fl_failure_maintenance"
#turning is not good enough
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_20-56-35_LPC_2000Iter_8192Env_d65cb358_airtime_fl_failure_bend"
#slow forward commands are bad.
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_21-51-44_LPC_2000Iter_8192Env_2ff16233_airtime_fl_failure_swing"
#good
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-19_19-05-57_LPC_2000Iter_8192Env_2497913e_airtime_fl_failure"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_02-19-53_LPC_2000Iter_8192Env_a02ab819_test1_rl_feet_failure_airtime_active"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_03-13-20_LPC_2000Iter_8192Env_fe4f9671_test2_fr_feet_failure_airtime_active"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_04-07-12_LPC_2000Iter_8192Env_f31b5598_test3_rr_feet_failure_airtime_active"










policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_16-15-11_RPC_1000Iter_8192Env_82d62d21_rl_failure_salak_deneme"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_02-19-53_LPC_2000Iter_8192Env_a02ab819_test1_rl_feet_failure_airtime_active"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_15-21-23_LPC_1000Iter_8192Env_3ffb0380_test2_rl_individual_clearance_fixed_bug_and_airtime_failure"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_12-10-01_LPC_1000Iter_8192Env_01058928_test1_fl_feet_failure_airtime_std_clearance"

# Properly working ones for individual leg up with individual clearance and airtime failure

# front left leg up
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_18-03-19_LPC_2000Iter_8192Env_cbe3d007_test1_fl_up_individual_clearance_std_and_airtime"
# rear left leg up
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_18-58-27_LPC_2000Iter_8192Env_aa21364e_test2_rl_up_individual_clearance_std_and_airtime"
# front right leg up
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_17-04-51_RPC_2000Iter_8192Env_ad5eee62_test3_fr_up_individual_clearance_std_and_airtime"
# rear right leg up
#policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_18-23-43_RPC_2000Iter_8192Env_354b1134_test4_rr_up_individual_clearance_std_and_airtime"

# leg up and failure events
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_22-37-09_LPC_3000Iter_8192Env_2e77b415_test1_fl_always_up_hip_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_23-57-48_LPC_3000Iter_8192Env_6d14ae49_test2_fl_always_up_thigh_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-22_01-19-20_LPC_3000Iter_8192Env_1f98636e_test3_fl_always_up_calf_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-22_02-40-31_LPC_3000Iter_8192Env_2e286df1_test4_fl_always_up_hip_thigh_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-21_22-38-28_RPC_3000Iter_8192Env_f99d2fb0_test5_fl_always_up_hip_calf_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-22_00-37-27_RPC_3000Iter_8192Env_c0fd03dc_test6_fl_always_up_thigh_calf_failure_5_15_seconds_scale_0.3"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-22_02-36-20_RPC_3000Iter_8192Env_32e08b07_test7_fl_always_up_hip_thigh_calf_failure_5_15_seconds_scale_0.3"

# leg up and failure event with event-aware rewards attempt(failed) need to use asymmetric ppo
policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-22_15-19-36_LPC_1500Iter_8192Env_95f329a8_test1_fl_always_up_hip_failure_5_15_seconds_scale_0.3"




policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-26_17-30-35_LegFlagIsInBothActorCritic"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-26_17-44-55_LegFlagIsInBothActorCritic"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-04_18-06-44_commando4novembercombinations"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-10-29_14-58-29_2000Iter_8192Env_5failuretype_onefailureforeachleg"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-07_02-10-52_RPC_2000Iter_8192Env_a37434a4_2case_training_test1_fine_and_rear_legs_fail_scenarios_with_event_in_reset.rewar"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-07_03-33-12_RPC_2000Iter_8192Env_37d9b8a1_2case_training_test2_fine_scenario_with_event_in_reset.rewards_and_observations_"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-07_04-50-51_RPC_2000Iter_8192Env_0b0ed254_2case_training_test3_rear_legs_fail_scenario_with_event_in_reset.rewards_and_obs"

policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-07_04-50-51_RPC_2000Iter_8192Env_0b0ed254_2case_training_test3_rear_legs_fail_scenario_with_event_in_reset.rewards_and_obs/"



# 2case distinguishes but 2leg not well.
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-11_23-18-23_2casefailureorbackfailedrevertrewardtonormalscalestiffnessdampingtozeroObservationofbackfailonehot"





# serial test for multitask
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_03-21-04_RPC_1000Iter_8192Env_4a83767f_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_04-02-24_RPC_1000Iter_8192Env_131f97e2_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_04-42-29_RPC_1000Iter_8192Env_bf76e5bb_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_05-24-21_RPC_1000Iter_8192Env_e716f398_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_06-05-34_RPC_1000Iter_8192Env_a3ce2158_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_06-45-40_RPC_1000Iter_8192Env_bb3943a2_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_07-27-43_RPC_1000Iter_8192Env_bfaa73ad_2case_test1_just_back_legs_failure_scene"
"""
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_08-11-08_RPC_1000Iter_8192Env_0352b299_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_08-51-34_RPC_1000Iter_8192Env_521afcb5_2case_test3_both_no_failure_and_back_legs_failure_scenes"
"""



"""
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_12-39-18_newtrystiffnesafterrandomassignment"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_13-24-19_newtrystiffnesafterrandomassignmentselfcollusionfalse"

policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_15-09-53_origfeettohipslidedeactivatedmovedstiffnessanddampingremoveddisabledsinglelegfailureairtimeandclearanceobonehot2dimcollusionfallse"
"""



"""

#new serial for multitask
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_17-28-08_RPC_1000Iter_8192Env_3cc020ca_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_18-12-34_RPC_1000Iter_8192Env_8cbba472_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-12_18-53-16_RPC_1000Iter_8192Env_d8550787_2case_test3_both_no_failure_and_back_legs_failure_scenes"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-04_18-06-44_commando4novembercombinations"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_16-46-00_newcrewardcombinationwithpidscaling"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_17-09-54_newcrewardcombinationplusfrontheightwithpidscaling"



# working well
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_18-01-45_RPC_1000Iter_8192Env_831c2fd0_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_18-42-54_RPC_1000Iter_8192Env_035a94c1_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_19-22-33_RPC_1000Iter_8192Env_41dc966b_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_20-03-10_RPC_1000Iter_8192Env_388f299f_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_20-43-14_RPC_1000Iter_8192Env_bb09eb06_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_21-23-01_RPC_1000Iter_8192Env_7b693bde_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_22-02-53_RPC_1000Iter_8192Env_6b778c34_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_22-44-56_RPC_1000Iter_8192Env_ea08f6bf_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-17_23-25-17_RPC_1000Iter_8192Env_a8040b6c_2case_test3_both_no_failure_and_back_legs_failure_scenes"


policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_15-04-22_18novembernewcombinationsenvshalffinehalfcommando"
"""



"""
# 18 november serial tests
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_18-08-24_RPC_1000Iter_8192Env_c8bf88e9_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_18-51-35_RPC_1000Iter_8192Env_49197495_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_19-33-41_RPC_1000Iter_8192Env_0113d44c_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_20-17-38_RPC_1000Iter_8192Env_3044ad0e_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_21-00-34_RPC_1000Iter_8192Env_9f1669ca_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_21-42-21_RPC_1000Iter_8192Env_d53da1e3_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_22-26-19_RPC_1000Iter_8192Env_fde6121e_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_23-08-54_RPC_1000Iter_8192Env_fb297090_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-18_23-50-40_RPC_1000Iter_8192Env_f276c89d_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_00-34-29_RPC_1000Iter_8192Env_4753330e_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_01-16-59_RPC_1000Iter_8192Env_0def80be_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_01-58-54_RPC_1000Iter_8192Env_3d9c3701_2case_test3_both_no_failure_and_back_legs_failure_scenes"
#below is kinda working
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_02-43-08_RPC_1000Iter_8192Env_eee72a43_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_03-27-37_RPC_1000Iter_8192Env_3c6890f9_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_04-09-52_RPC_1000Iter_8192Env_45ac064b_2case_test3_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_04-55-14_RPC_1000Iter_8192Env_e6068cbc_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_05-39-55_RPC_1000Iter_8192Env_fece1334_2case_test2_no_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_06-22-01_RPC_1000Iter_8192Env_dcf7bd0e_2case_test3_both_no_failure_and_back_legs_failure_scenes"


policy_folder_path  = "logs/rsl_rl/flat_direct/2025-11-19_14-00-31_19novemberremovedtorquescalaingbutstilldifferentthan202511171922"

policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_14-54-42_19novemberremovedtorquescalaingbutstilldifferentthan202511171922noslide"



policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_15-44-38_19novemberremovedtorquescalaingbutstilldifferentthan202511171922noslidenocommandscaling"
"""



policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_18-12-57_RPC_2000Iter_8192Env_4ed52a94_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_19-32-36_RPC_2000Iter_8192Env_3ff8ea81_2case_test2_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_20-55-22_RPC_2000Iter_8192Env_3114852a_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_22-22-53_RPC_2000Iter_8192Env_48c2ff0d_2case_test2_both_no_failure_and_back_legs_failure_scenes"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-19_23-50-02_RPC_2000Iter_8192Env_d38faaf0_2case_test1_just_back_legs_failure_scene"
policy_folder_path = "logs/rsl_rl/flat_direct/2025-11-20_01-16-17_RPC_2000Iter_8192Env_14938ca9_2case_test2_both_no_failure_and_back_legs_failure_scenes"
"""
"""




#basic-locomotion-dls-isaaclab/source/basic_locomotion_dls_isaaclab/basic_locomotion_dls_isaaclab/assets/aliengo_asset.py


#policy_folder_path = dir_path + "/../tested_policies/" + rologs/rsl_rl/flat_direct/2025-1bot + "/aliengo_stop_and_go_correct_offset"

#policy_folder_path = dir_path + "/../tested_policies/" + robot + "/go2_5asymm"

#cuncurrent_state_est_network = policy_folder_path + "/exported/cuncurrent_state_estimator.pth"
#rma_network = policy_folder_path + "/exported/rma.pth"

# Load specific training parameters
import yaml 
with open(policy_folder_path + "/params/env.yaml", "r") as file:
    training_env = yaml.unsafe_load(file)

use_vision = False  # If True, use the vision observations in the RL policy #TODO add in yaml
