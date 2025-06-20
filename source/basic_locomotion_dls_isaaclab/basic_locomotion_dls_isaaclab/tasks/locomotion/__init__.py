# Copyright (c) 2022-2024, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
import gymnasium as gym

from . import agents

# Aliengo environments
from .quadruped_env_cfg import (
    AliengoEnvCfg,
    AliengoRoughBlindEnvCfg,
    AliengoRoughVisionEnvCfg,
    Go2EnvCfg,
    Go2RoughBlindEnvCfg,
    Go2RoughVisionEnvCfg,
    HyQRealEnvCfg,
    HyQRealRoughBlindEnvCfg,
    HyQRealRoughVisionEnvCfg,
)

##
# Register Gym environments.
##
from .quadruped_locomotion_env import QuadrupedLocomotionEnv

gym.register(
    id="Locomotion-Aliengo-Flat",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoFlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Blind",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Vision",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)

# Go2 environments ===================================================================================================
gym.register(
    id="Locomotion-Go2-Flat",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2EnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2FlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Go2-Rough-Blind",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2RoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2RoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Go2-Rough-Vision",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": Go2RoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.go2_agent.rsl_rl_ppo_cfg:Go2RoughPPORunnerCfg",
    },
)

# HyQReal environments =================================================================================================
gym.register(
    id="Locomotion-HyQReal-Flat",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealFlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-HyQReal-Rough-Blind",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealRoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealRoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-HyQReal-Rough-Vision",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": HyQRealRoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.hyqreal_agent.rsl_rl_ppo_cfg:HyQRealRoughPPORunnerCfg",
    },
)


# Aliengo AMP environments
from .aliengo_amp_env_cfg import AliengoAMPFlatEnvCfg, AliengoAMPRoughVisionEnvCfg, AliengoAMPRoughBlindEnvCfg  # noqa: I001

gym.register(
    id="Locomotion-Aliengo-AMP-Flat",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoAMPFlatEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_amp_agent.rsl_rl_ppo_cfg:AliengoFlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-AMP-Rough-Blind",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoAMPRoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_amp_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-AMP-Rough-Vision",
    entry_point=QuadrupedLocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoAMPRoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_amp_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)
