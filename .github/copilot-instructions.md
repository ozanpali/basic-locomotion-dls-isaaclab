## Copilot instructions for this repo

Be concise, follow existing patterns, and prefer small, verifiable changes. When behavior changes, validate with a short play/run.

## Big picture (what this repo is)
- IsaacLab quadruped locomotion tasks + RSL-RL training. Core package lives in `source/basic_locomotion_dls_isaaclab/basic_locomotion_dls_isaaclab`.
- Envs are registered as Gym tasks (e.g., `Locomotion-Aliengo-Flat`, `Locomotion-Go2-Rough-Vision`). Training/playing scripts are under `scripts/rsl_rl/` and export artifacts to `logs/rsl_rl/<experiment>/<timestamp>/exported/`.
- Optional integrations: Morphological Symmetries (`morphosymm-rl`), Adversarial Motion Priors (`amp-rsl-rl`), sim-to-sim (MuJoCo) and sim-to-real (ROS1/ROS2) via `deploy/`.

## Where things are (read these first)
- Env runtime: `tasks/locomotion/locomotion_env.py` defines `LocomotionEnv` (DirectRLEnv) with sensors (RayCaster, IMU), observation assembly, rewards (`_get_rewards`), and resets.
- Registry: `tasks/locomotion/__init__.py` registers Gym IDs and links `env_cfg_entry_point` + `rsl_rl_cfg_entry_point` to agent cfgs in `tasks/locomotion/agents/rsl_rl_ppo_cfg.py`.
- Robot cfgs: `tasks/locomotion/*_env_cfg.py` contain `DirectRLEnvCfg` subclasses (sim params, terrain, sensors, events, reward scales).
- Events: `tasks/custom_events.py` has startup/reset/interval terms (e.g., `randomize_joint_default_pos`, `randomize_joint_friction_model`, `scale_joint_torque`). The last one patches actuator.compute once and multiplies efforts per-env/per-joint, updating `env._torque_scaled_mask_per_leg_joint`.
- Deploy: `deploy/config.py` points `policy_folder_path` to a trained run (expects `<folder>/params/env.yaml`); launch via `deploy/play_mujoco.py`, `play_ros1.py`, `play_ros2.py`.

## Workflows (commands that matter)
- Install (after IsaacLab): `python -m pip install -e source/basic_locomotion_dls_isaaclab`.
- Train (headless): `python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Flat --num_envs=4096 --headless`.
- Play/test: `python scripts/rsl_rl/play.py --task=Locomotion-Aliengo-Flat --num_envs=16 --video`.
- Resume/organize: set `--resume --load_run=<run_folder> --checkpoint=<file>`; logs under `logs/rsl_rl/<experiment>/<time[_run]>` and exports under `exported/{policy.pt,policy.onnx}`.
- Symmetries/AMP: switch `algorithm.class_name` in `agents/rsl_rl_ppo_cfg.py` (e.g., `PPOSymmDataAugmented`, `AMP_PPO`) or use `train_symm.py` / `train_amp.py` scripts.

## Conventions and patterns (use these)
- Observations: choose IMU or model-based state; optional clock signal and history via `cfg.use_clock_signal`/`cfg.use_observation_history` (history is appended then flattened; newest at index -1).
- Events signature: `(env, env_ids, asset_cfg, **params)`; select joints via `SceneEntityCfg`. Keep per-env shapes; when touching actuators, map global joint ids to actuator-local indices; `_randomize_prop_by_op` handles add/scale/abs with uniform/log-uniform/gaussian.
- Registration: new tasks must be added in `tasks/locomotion/__init__.py` with both env and agent cfg entry points.
- Naming/order: legs and joints follow `FL/FR/RL/RR` with `hip/thigh/calf`. Symmetry cfg uses this order in `rsl_rl_ppo_cfg.py`.

## Sanity checks and tips
- Smoke test: `python scripts/rsl_rl/play.py --task=Locomotion-Aliengo-Flat --num_envs=4 --video --video_length=200`.
- One-iter train: `python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Flat --num_envs=64 --max_iterations=1 --headless` then confirm `exported/` artifacts.
- Performance: if cylinder collisions slow sim, pass `--kit_args="--/physics/collisionApproximateCylinders=true"`.

## External deps
- Requires IsaacLab and `isaaclab_rl` (RSL-RL). Optional repos: `morphosymm-rl` (symmetries), `amp-rsl-rl` (AMP). Simulator is launched by scripts via `AppLauncher`.

Questions or gaps? If events, new robot registration, or deployment specifics are unclear for your task, call out the exact area to refine these notes.
