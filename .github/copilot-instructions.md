# Copilot instructions for basic-locomotion-dls-isaaclab

These instructions help AI coding agents be productive quickly in this repo. Keep edits concise, follow existing patterns, and verify with a short play/run when changing behavior.

## Big picture
- This repo builds IsaacLab DirectRLEnv tasks for quadruped locomotion and trains policies with RSL-RL. Core package: `source/basic_locomotion_dls_isaaclab/basic_locomotion_dls_isaaclab`.
- Envs are registered as Gym tasks (IDs like `Locomotion-Go2-Flat`) and configured via dataclass-style cfgs. Policies are trained via `scripts/rsl_rl/*` wrappers (Hydra + RSL-RL), with artifacts exported to `logs/rsl_rl/.../exported/` (JIT and ONNX).
- Optional integrations: Morphological Symmetries (`morphosymm-rl`), Adversarial Motion Priors (`amp-rsl-rl`), sim-to-sim (MuJoCo) and sim-to-real (ROS1/ROS2) under `deploy/`.

## Code architecture (where to look)
- Env runtime: `tasks/locomotion/locomotion_env.py` defines `LocomotionEnv` (DirectRLEnv). It constructs sensors (RayCaster, IMU), builds observations, rewards, and dones, and manages resets.
- Task registry: `tasks/locomotion/__init__.py` registers Gym env IDs and maps them to env cfgs and PPO cfgs in `agents/rsl_rl_ppo_cfg.py`.
- Robot-specific cfgs: `tasks/locomotion/*_env_cfg.py` provide `DirectRLEnvCfg` subclasses with simulation, terrain, sensors, noise, events (domain randomization), and reward scales.
- Domain randomization and events: `tasks/custom_events.py` contains event functions (startup/reset/interval) used via `EventTerm` in cfgs. See e.g. `randomize_joint_friction_model`, `randomize_joint_default_pos`, and the interval-ready `scale_joint_torque` (monkey-patches actuator.compute to apply per-joint scaling).
- Rewards and logging: reward terms are assembled in `LocomotionEnv._get_rewards`; corresponding per-episode aggregates are tracked in `_episode_sums` and flushed on reset for logging.
- Training interface: `scripts/rsl_rl/train.py` launches the simulator (`isaaclab.app.AppLauncher`), wraps env for RSL-RL, and exports JIT/ONNX. CLI defaults and logger wiring live in `scripts/rsl_rl/cli_args.py`.

## Developer workflows (commands and gotchas)
- Install (after IsaacLab): `python -m pip install -e source/basic_locomotion_dls_isaaclab` (see README for full prerequisites).
- Train (headless examples):
  - `python scripts/rsl_rl/train.py --task=Locomotion-Go2-Flat --num_envs=4096 --headless`
  - To enable Symmetries or AMP, change `class_name` in `agents/rsl_rl_ppo_cfg.py` (e.g., `PPOSymmDataAugmented` or `AMP_PPO`) as noted in README.
- Play/test: `python scripts/rsl_rl/play.py --task=Locomotion-Go2-Flat --num_envs=16` (records video if `--video`).
- Artifacts and resume:
  - Logs: `logs/rsl_rl/<experiment>/<timestamp>_{run_name}`; exports in `<...>/exported/{policy.pt, policy.onnx}`.
  - Resume flags: `--resume --load_run=<folder> --checkpoint=<file>` (see `cli_args.py`).
- Deployment: `deploy/` contains `play_mujoco.py`, `play_ros1.py`, `play_ros2.py` and `config.py` that points to a trained policy folder (uses `<policy_folder_path>/params/env.yaml`).

## Project-specific conventions and patterns
- Observation assembly: configurable history (`cfg.use_observation_history`) and optional clock signal for periodic gaits. RMA and concurrent state estimator are supervised heads learned online; see `LocomotionEnv._get_rma` and `_get_cuncurrent_state_estimation`.
- Events API: event funcs have signature `(env, env_ids, asset_cfg, **params)`. Use `SceneEntityCfg` to select bodies/joints. Respect per-env shape `[num_envs, *]`; when indexing across actuators, map global joint ids to actuator-local indices. Use `_randomize_prop_by_op` for additive/scale/abs ops with uniform/log-uniform/gaussian.
- Interval events: use `EventTerm(..., mode="interval", interval_range_s=(low, high))`. For runtime scaling/gating (e.g., joint torque failures), prefer patterns like `scale_joint_torque` that:
  - lazily initialize per-env/per-joint tensors on device,
  - patch once per actuator and multiply after base `compute()`,
  - maintain an env-level mask (`env._torque_scaled_mask_per_leg_joint`) for reward/critic awareness.
- Gym registration: new envs must be registered in `tasks/locomotion/__init__.py` with both `env_cfg_entry_point` and `rsl_rl_cfg_entry_point` (string path to `agents` cfg class).
- Naming/order: joints and legs follow names like `FL_hip_joint`, `FR_thigh_joint`, etc. The symmetry cfg encodes expected order in `agents/rsl_rl_ppo_cfg.py`.

## Extending the project (common edits)
- Add a robot: create `<robot>_env_cfg.py` (copy pattern from `go2_env_cfg.py`), add an asset cfg under `assets/`, register in `tasks/locomotion/__init__.py`, and reference an agent cfg in `agents/rsl_rl_ppo_cfg.py`.
- Add a reward: implement in `LocomotionEnv._get_rewards` and add a matching `_episode_sums` entry; scale via cfg fields in the corresponding env cfg.
- Add an event: implement in `tasks/custom_events.py` and wire in a cfg under `EventCfg` using `EventTerm` with proper `mode` and `params`.

## Quick sanity checks and common pitfalls
- Smoke test play: `python scripts/rsl_rl/play.py --task=Locomotion-Go2-Flat --num_envs=4 --video --video_length=200` to verify observations, contacts, and rewards don’t error.
- Dry-run train: `python scripts/rsl_rl/train.py --task=Locomotion-Go2-Flat --num_envs=64 --max_iterations=1 --headless` then check `logs/rsl_rl/.../exported/` exists.
- Event shapes: when writing events, handle `env_ids` and joint masks carefully. If not using `slice(None)`, broadcast with `env_ids[:, None]` and ensure masks map global joint ids to each actuator’s local indices.
- Device placement: use `asset.device` and move `env_ids`/tensors accordingly; keep shapes `[num_envs, num_joints]` for per-env/per-joint maps.
- Height scanner inputs: ensure `mesh_prim_paths` include the active terrain prim; NaNs are handled but a wrong path yields flat zeros.
- Observation history: append with `self._obs_hist = torch.cat((hist[:,1:,:], obs.unsqueeze(1)), dim=1)` and flatten with `start_dim=1` to match agent cfg sizes.
- Exports: policy export already moves to CPU and sets `.eval()`. If you customize, keep this to make ONNX portable.
- Performance tip: on slow trainings with cylinder collisions, add `--kit_args="--/physics/collisionApproximateCylinders=true"`.

## External dependencies/assumptions
- Requires IsaacLab (see project README). Training uses `rsl_rl` via `isaaclab_rl`. Optional: `morphosymm-rl` and `amp-rsl-rl` repos for symmetry and AMP features.
- Simulator app is launched by scripts; you typically don’t run Isaac Sim manually.

Questions or gaps? If instructions around events, new robot registration, or deployment specifics are unclear for your task, mention the exact area so we can refine these notes.
