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
    id="Locomotion-Aliengo-Flat-Old",
    entry_point=LocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoFlatEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoFlatPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Blind-Old",
    entry_point=LocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughBlindEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)

gym.register(
    id="Locomotion-Aliengo-Rough-Vision-Old",
    entry_point=LocomotionEnv,
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": AliengoRoughVisionEnvCfg,
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.aliengo_agent.rsl_rl_ppo_cfg:AliengoRoughPPORunnerCfg",
    },
)