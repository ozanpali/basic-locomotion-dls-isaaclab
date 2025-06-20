# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Ant locomotion environment.
"""

import gymnasium as gym

from . import agents

##
# Register Gym environments.
##
from .locomotion_env import LocomotionEnv


# Aliengo environments
from .locomotion_env import AliengoFlatEnvCfg, AliengoRoughVisionEnvCfg, AliengoRoughBlindEnvCfg

gym.register(
    id="Locomotion-Aliengo-Flat",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoFlatEnvCfg,
        "rl_games_cfg_entry_point": f"{agents.__name__}.aliengo_agent:rl_games_flat_ppo_cfg.yaml",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoFlatPPORunnerCfg",
        "skrl_cfg_entry_point": f"{agents.__name__}.aliengo_agent:skrl_flat_ppo_cfg.yaml",
        "sb3_cfg_entry_point": f"{agents.__name__}.aliengo_agent:sb3_ppo_cfg.yaml",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Blind",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughBlindEnvCfg,
        "rl_games_cfg_entry_point": f"{agents.__name__}.aliengo_agent:rl_games_rough_ppo_cfg.yaml",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
        "skrl_cfg_entry_point": f"{agents.__name__}.aliengo_agent:skrl_rough_ppo_cfg.yaml",
        "sb3_cfg_entry_point": f"{agents.__name__}.aliengo_agent:sb3_ppo_cfg.yaml",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Vision",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughVisionEnvCfg,
        "rl_games_cfg_entry_point": f"{agents.__name__}.aliengo_agent:rl_games_rough_ppo_cfg.yaml",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
        "skrl_cfg_entry_point": f"{agents.__name__}.aliengo_agent:skrl_rough_ppo_cfg.yaml",
    },
)

# Go2 environments
from .locomotion_env import Go2FlatEnvCfg, Go2RoughVisionEnvCfg, Go2RoughBlindEnvCfg

gym.register(
    id="Locomotion-Go2-Flat",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2FlatEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2FlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Go2-Rough-Blind",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2RoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2RoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Go2-Rough-Vision",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2RoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2RoughPPORunnerCfg",
    },
)

# HyQReal environments
from .locomotion_env import HyQRealFlatEnvCfg, HyQRealRoughVisionEnvCfg, HyQRealRoughBlindEnvCfg

gym.register(
    id="Locomotion-HyQReal-Flat",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealFlatEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealFlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-HyQReal-Rough-Blind",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealRoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealRoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-HyQReal-Rough-Vision",
    entry_point="basic_locomotion_dls_isaaclab.tasks.locomotion:LocomotionEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealRoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealRoughPPORunnerCfg",
    },
)