# Copyright (c) 2022-2024, The Berkeley Humanoid Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import torch
from typing import TYPE_CHECKING, Literal

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.envs.mdp.events import _randomize_prop_by_op

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedEnv


def randomize_joint_default_pos(
        env: ManagerBasedEnv,
        env_ids: torch.Tensor | None,
        asset_cfg: SceneEntityCfg,
        pos_distribution_params: tuple[float, float] | None = None,
        operation: Literal["add", "scale", "abs"] = "abs",
        distribution: Literal["uniform", "log_uniform", "gaussian"] = "uniform",
):
    """
    Randomize the joint default positions which may be different from URDF due to calibration errors.
    """
    # extract the used quantities (to enable type-hinting)
    asset: Articulation = env.scene[asset_cfg.name]

    # resolve environment ids
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)

    # resolve joint indices
    if asset_cfg.joint_ids == slice(None):
        joint_ids = slice(None)  # for optimization purposes
    else:
        joint_ids = torch.tensor(asset_cfg.joint_ids, dtype=torch.int, device=asset.device)

    if pos_distribution_params is not None:
        pos = asset.data.default_joint_pos.to(asset.device).clone()
        pos = _randomize_prop_by_op(
            pos, pos_distribution_params, env_ids, joint_ids, operation=operation, distribution=distribution
        )[env_ids][:, joint_ids]

        if env_ids != slice(None) and joint_ids != slice(None):
            env_ids = env_ids[:, None]
        asset.data.default_joint_pos[env_ids, joint_ids] = pos



def randomize_joint_friction_model(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg,
    friction_distribution_params: tuple[float, float] | None = None,
    armature_distribution_params: tuple[float, float] | None = None,
    first_order_delay_filter_distribution_params: tuple[float, float] | None = None,
    second_order_delay_filter_distribution_params: tuple[float, float] | None = None,
    operation: Literal["add", "scale", "abs"] = "abs",
    distribution: Literal["uniform", "log_uniform", "gaussian"] = "uniform",
):
    """
    Randomize the friction parameters used in joint friction model. 
    """
    # extract the used quantities (to enable type-hinting)
    asset: Articulation = env.scene[asset_cfg.name]

    # resolve environment ids
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)

    # resolve joint indices
    if asset_cfg.joint_ids == slice(None):
        joint_ids = slice(None)  # for optimization purposes
    else:
        joint_ids = torch.tensor(asset_cfg.joint_ids, dtype=torch.int, device=asset.device)

    # sample joint properties from the given ranges and set into the physics simulation
    # -- friction
    if friction_distribution_params is not None:
        for actuator in asset.actuators.values():
            actuator_joint_ids = [joint_id in joint_ids for joint_id in actuator.joint_indices]
            if sum(actuator_joint_ids) > 0:
                friction = actuator.friction_static.to(asset.device).clone()
                friction = _randomize_prop_by_op(
                    friction, friction_distribution_params, env_ids, torch.arange(friction.shape[1]), operation=operation, distribution=distribution
                )[env_ids][:, actuator_joint_ids]
                actuator.friction_static[env_ids[:, None], actuator_joint_ids] = friction

                friction = actuator.friction_dynamic.to(asset.device).clone()
                friction = _randomize_prop_by_op(
                    friction, friction_distribution_params, env_ids, torch.arange(friction.shape[1]), operation=operation, distribution=distribution
                )[env_ids][:, actuator_joint_ids]
                actuator.friction_dynamic[env_ids[:, None], actuator_joint_ids] = friction

    if armature_distribution_params is not None:
        for actuator in asset.actuators.values():
            actuator_joint_ids = [joint_id in joint_ids for joint_id in actuator.joint_indices]
            if sum(actuator_joint_ids) > 0:
                armature = actuator.armature.to(asset.device).clone()
                armature = _randomize_prop_by_op(
                    armature, armature_distribution_params, env_ids, torch.arange(armature.shape[1]), operation=operation, distribution=distribution
                )[env_ids][:, actuator_joint_ids]
                actuator.armature[env_ids[:, None], actuator_joint_ids] = armature


def randomize_joint_delay_model(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg,
    friction_distribution_params: tuple[float, float] | None = None,
    armature_distribution_params: tuple[float, float] | None = None,
    first_order_delay_filter_distribution_params: tuple[float, float] | None = None,
    second_order_delay_filter_distribution_params: tuple[float, float] | None = None,
    operation: Literal["add", "scale", "abs"] = "abs",
    distribution: Literal["uniform", "log_uniform", "gaussian"] = "uniform",
):

    """
    Randomize the delay used in joint hydraulic model. 
    """
    # extract the used quantities (to enable type-hinting)
    asset: Articulation = env.scene[asset_cfg.name]

    # resolve environment ids
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)

    # resolve joint indices
    if asset_cfg.joint_ids == slice(None):
        joint_ids = slice(None)  # for optimization purposes
    else:
        joint_ids = torch.tensor(asset_cfg.joint_ids, dtype=torch.int, device=asset.device)

    if first_order_delay_filter_distribution_params is not None:
        for actuator in asset.actuators.values():
            actuator_joint_ids = [joint_id in joint_ids for joint_id in actuator.joint_indices]
            if sum(actuator_joint_ids) > 0:
                first_order_delay_filter = actuator.first_order_delay_filter.to(asset.device).clone()
                first_order_delay_filter = _randomize_prop_by_op(
                    first_order_delay_filter, first_order_delay_filter_distribution_params, env_ids, torch.arange(first_order_delay_filter.shape[1]), operation=operation, distribution=distribution
                )[env_ids][:, actuator_joint_ids]
                actuator.first_order_delay_filter[env_ids[:, None], actuator_joint_ids] = first_order_delay_filter

    if second_order_delay_filter_distribution_params is not None:
        for actuator in asset.actuators.values():
            actuator_joint_ids = [joint_id in joint_ids for joint_id in actuator.joint_indices]
            if sum(actuator_joint_ids) > 0:
                second_order_delay_filter = actuator.second_order_delay_filter.to(asset.device).clone()
                second_order_delay_filter = _randomize_prop_by_op(
                    second_order_delay_filter, second_order_delay_filter_distribution_params, env_ids, torch.arange(second_order_delay_filter.shape[1]), operation=operation, distribution=distribution
                )[env_ids][:, actuator_joint_ids]
                actuator.second_order_delay_filter[env_ids[:, None], actuator_joint_ids] = second_order_delay_filter


def zero_command_velocity(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor,
):
   
    env._commands[env_ids, 0] = 0.0
    env._commands[env_ids, 1] = 0.0
    env._commands[env_ids, 2] = 0.0


def resample_command_velocity(
    env: ManagerBasedEnv,
    env_ids: torch.Tensor,
):
   
    # Sample new commands
    env._commands[env_ids] = torch.zeros_like(env._commands[env_ids]).uniform_(-1.0, 1.0)
    env._commands[env_ids, 0] *= 0.5 
    env._commands[env_ids, 1] *= 0.25 
    env._commands[env_ids, 2] *= 0.3 


def scale_joint_torque(
    env: "ManagerBasedEnv",
    env_ids: torch.Tensor | None,
    asset_cfg: SceneEntityCfg,
    scale: float = 1.0,
):
    """
    Scale joint efforts for selected joints and update a per-leg, per-joint activation mask.

    Behavior
    - Multiplies computed joint efforts by `scale` for targeted joints.
    - Safe to call repeatedly. Patches actuator.compute only once per actuator.
    - Interval-friendly: when called with a subset `env_ids`, sets those envs to `scale`
      and resets the complement envs to 1.0 for the targeted joints (acts like a gate).
    - Updates env._torque_scaled_mask_per_leg_joint[env, leg(FL/FR/RL/RR), joint(hip/thigh/calf)].
    """
    # locate articulation
    asset: Articulation = env.scene[asset_cfg.name]

    # normalize env_ids
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)
    else:
        env_ids = env_ids.to(asset.device)

    # resolve target joint ids (global indices on the robot)
    if asset_cfg.joint_ids == slice(None):
        selected_joint_ids = None  # means: all joints in each actuator
    else:
        selected_joint_ids = set(int(x) for x in torch.as_tensor(asset_cfg.joint_ids).view(-1).tolist())

    # ensure each actuator has a per-env, per-joint scale tensor and a patched compute()
    for actuator in asset.actuators.values():
        # which of this actuator's joints are selected
        if selected_joint_ids is None:
            joint_mask = [True for _ in actuator.joint_indices]
        else:
            joint_mask = [int(jid) in selected_joint_ids for jid in actuator.joint_indices]
        if not any(joint_mask):
            continue

        # init torque_scale tensor
        if not hasattr(actuator, "torque_scale"):
            actuator.torque_scale = torch.ones(
                (env.scene.num_envs, len(actuator.joint_indices)), dtype=torch.float, device=asset.device
            )

        # patch compute once
        if not getattr(actuator, "_torque_scale_patched", False):
            actuator._orig_compute_for_torque_scale = actuator.compute

            def _compute_with_scale(*args, _self=actuator, **kwargs):
                ca = _self._orig_compute_for_torque_scale(*args, **kwargs)
                if getattr(ca, "joint_efforts", None) is not None:
                    ca.joint_efforts = ca.joint_efforts * _self.torque_scale
                return ca

            actuator.compute = _compute_with_scale
            actuator._torque_scale_patched = True

        # write scales: set active envs; do NOT reset complement here to avoid flicker
        joint_idx = torch.tensor([i for i, m in enumerate(joint_mask) if m], dtype=torch.long, device=asset.device)
        actuator.torque_scale[env_ids.unsqueeze(1), joint_idx] = float(scale)

    # update per-leg, per-joint mask used by rewards/observations
    # lazily initialize the mask on the env
    if not hasattr(env, "_torque_scaled_mask_per_leg_joint"):
        env._torque_scaled_mask_per_leg_joint = torch.zeros(
            (env.scene.num_envs, 4, 3), dtype=torch.float, device=asset.device
        )

    # turn joint names (if provided) into leg/joint indices
    target_names = getattr(asset_cfg, "joint_names", None)
    if target_names is None:
        names: list[str] = []
    elif isinstance(target_names, str):
        names = [target_names]
    else:
        names = list(target_names)

    def _leg_idx(n: str) -> int | None:
        if n.startswith("FL_"):
            return 0
        if n.startswith("FR_"):
            return 1
        if n.startswith("RL_"):
            return 2
        if n.startswith("RR_"):
            return 3
        return None

    def _joint_idx(n: str) -> int | None:
        if "hip" in n:
            return 0
        if "thigh" in n:
            return 1
        if "calf" in n:
            return 2
        return None

    active_val = 1.0 if abs(float(scale) - 1.0) > 1e-6 else 0.0
    for jn in names:
        li = _leg_idx(jn)
        ji = _joint_idx(jn)
        if li is None or ji is None:
            continue
        # set active envs to active_val; do NOT reset complement here to avoid flicker
        env._torque_scaled_mask_per_leg_joint[env_ids, li, ji] = active_val
