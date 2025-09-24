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
    Scale the applied effort (torque) for selected joints by a multiplicative factor.

    Notes
    - This does NOT modify stiffness or damping; it multiplies the final joint efforts.
    - Implemented via runtime monkey-patching of actuator compute() to apply a per-joint scale tensor.
    - Safe to call repeatedly; patching occurs only once per actuator instance.
    - Use with mode="interval" to enable this scaling at scheduled times. Call again with scale=1.0 to reset.
    """
    # extract the used quantities (to enable type-hinting)
    asset: Articulation = env.scene[asset_cfg.name]

    # resolve environment ids
    if env_ids is None:
        env_ids = torch.arange(env.scene.num_envs, device=asset.device)

    # resolve joint indices (list or slice)
    if asset_cfg.joint_ids == slice(None):
        joint_ids = slice(None)
    else:
        joint_ids = torch.tensor(asset_cfg.joint_ids, dtype=torch.int, device=asset.device)

    # helper: ensure actuator has torque_scale tensor and patch compute once
    def _ensure_patch_and_scale(actuator):
        # Create per-joint, per-env torque scale map if missing
        if not hasattr(actuator, "torque_scale"):
            num_envs = env.scene.num_envs
            num_joints = len(actuator.joint_indices)
            actuator.torque_scale = torch.ones(
                (num_envs, num_joints), dtype=torch.float, device=asset.device
            )

        # Monkey-patch compute once to apply scaling after base compute
        if not hasattr(actuator, "_torque_scale_patched") or actuator._torque_scale_patched is False:
            actuator._orig_compute_for_torque_scale = actuator.compute

            def _compute_with_scale(*args, _self=actuator, **kwargs):
                ca = _self._orig_compute_for_torque_scale(*args, **kwargs)
                # Ensure torque_scale shape matches
                if hasattr(_self, "torque_scale") and getattr(ca, "joint_efforts", None) is not None:
                    # Multiply per-env and per-joint
                    ca.joint_efforts = ca.joint_efforts * _self.torque_scale
                return ca

            actuator.compute = _compute_with_scale
            actuator._torque_scale_patched = True

    # Apply scale for the selected joints within each actuator group
    for actuator in asset.actuators.values():
        # map the selected joint_ids into this actuator's local joint set
        if isinstance(joint_ids, slice):
            actuator_joint_mask = [True] * len(actuator.joint_indices)
        else:
            selected_ids = set(int(x) for x in joint_ids.view(-1).tolist())
            actuator_joint_mask = [int(jid) in selected_ids for jid in actuator.joint_indices]
        if sum(actuator_joint_mask) == 0:
            continue

        _ensure_patch_and_scale(actuator)

        # prepare indexing shapes
        if env_ids != slice(None):
            env_index = env_ids[:, None]
        else:
            env_index = slice(None)

        # update the scale for the targeted joints and environments
        actuator.torque_scale[env_index, actuator_joint_mask] = float(scale)