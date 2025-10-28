# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Script to train RL agent with RSL-RL.
#
# Launch Isaac Sim Simulator first.

import argparse
import sys

# Import here to avoid the pinocchio error if morphosymm import it after the import of AppLauncher.
import pinocchio as pin

from isaaclab.app import AppLauncher

# local imports
import morphosymm_rl.example.cli_args_utils as cli_args_utils  # isort: skip


# Misc arguments =============================================================
parser = argparse.ArgumentParser(description="Train an RL agent with RSL-RL.")
parser.add_argument("--video", action="store_true", default=False, help="Record videos during training.")
parser.add_argument("--video_length", type=int, default=400, help="Length of videos [steps]")
parser.add_argument("--video_interval", type=int, default=2000, help="Interval between videos [in steps]")
parser.add_argument("--num_envs", type=int, default=None, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument("--seed", type=int, default=None, help="Seed used for the environment")
parser.add_argument("--max_iterations", type=int, default=None, help="RL Policy training iterations.")
# RSL-RL arguments ============================================================
arg_group = parser.add_argument_group("rsl_rl", description="Arguments for RSL-RL agent.")
# Experiment arguments
arg_group.add_argument("--experiment_name", type=str, default=None, help="Dir where logs will be stored.")
arg_group.add_argument("--run_name", type=str, default=None, help="Run name suffix to the log directory.")
# Model loading and saving arguments
arg_group.add_argument("--resume", type=bool, default=None, help="Whether to resume from a checkpoint.")
arg_group.add_argument("--load_run", type=str, default=None, help="Name of the run folder to resume from.")
arg_group.add_argument("--checkpoint", type=str, default=None, help="Checkpoint file to resume from.")
# Logger arguments
arg_group.add_argument(
    "--logger", type=str, default="wandb", choices={"wandb", "tensorboard", "neptune"}, help="Logger module to use."
)
arg_group.add_argument("--log_project_name", type=str, default=None, help="Project name for wandb | neptune.")
# Customize the Agent configuration with cli commands ========================

# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

# Custom parsing logic ==========================================================================
# always enable cameras to record video
if args_cli.video:
    args_cli.enable_cameras = True
if args_cli.log_project_name is None:  # Default wandb/neptune proj name is the task name.
    args_cli.log_project_name = args_cli.task
# ===============================================================================================
# clear out sys.argv for Hydra
sys.argv = [sys.argv[0]] + hydra_args

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import os  # noqa: I001
import re
from datetime import datetime

import isaaclab_tasks  # noqa: F401

# Import DLS isaaclab tasks and envs.
import basic_locomotion_dls_isaaclab.tasks  # noqa: F401

import torch
import gymnasium as gym
from isaaclab.envs import (
    DirectMARLEnv,
    DirectMARLEnvCfg,
    DirectRLEnvCfg,
    ManagerBasedRLEnvCfg,
    multi_agent_to_single_agent,
)
from isaaclab.utils.dict import print_dict
from isaaclab.utils.io import dump_pickle, dump_yaml
from isaaclab_rl.rsl_rl import (
    RslRlOnPolicyRunnerCfg,
    RslRlVecEnvWrapper,
    export_policy_as_jit,
    export_policy_as_onnx,
)
from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

# from rsl_rl.runners import OnPolicyRunner
from morphosymm_rl.symm_on_policy_runner import SymmOnPolicyRunner
import escnn.nn

torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.backends.cudnn.deterministic = False
torch.backends.cudnn.benchmark = False


@hydra_task_config(args_cli.task, "rsl_rl_cfg_entry_point")
def main(
    env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg,
    agent_cfg: RslRlOnPolicyRunnerCfg,
):
    """Train with RSL-RL agent."""
    # override configurations with non-hydra CLI arguments
    agent_cfg = cli_args_utils.update_rsl_rl_cfg(agent_cfg, args_cli)
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    agent_cfg.max_iterations = (
        args_cli.max_iterations if args_cli.max_iterations is not None else agent_cfg.max_iterations
    )

    # set the environment seed
    # note: certain randomizations occur in the environment initialization so we set the seed here
    env_cfg.seed = agent_cfg.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device

    # specify directory for logging experiments
    log_root_path = os.path.join("logs", "rsl_rl", agent_cfg.experiment_name)
    log_root_path = os.path.abspath(log_root_path)
    print(f"[INFO] Logging experiment in directory: {log_root_path}")
    # specify directory for logging runs: {time-stamp}_{run_name}
    log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # This way, the Ray Tune workflow can extract experiment name.
    print(f"Exact experiment name requested from command line: {log_dir}")
    if agent_cfg.run_name:
        log_dir += f"_{agent_cfg.run_name}"
    log_dir = os.path.join(log_root_path, log_dir)

    # create isaac environment
    env = gym.make(args_cli.task, cfg=env_cfg, render_mode="rgb_array" if args_cli.video else None)

    # convert to single-agent instance if required by the RL algorithm
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)

    # save resume path before creating a new log_dir
    if agent_cfg.resume:
        # Normalize CLI/resume selectors:
        # - load_run: regex for run folder. Use ".*" for latest when unset or "-1".
        # - load_checkpoint: regex for checkpoint file. Accept plain iteration (e.g., "999") and map to model_999.pt.
        load_run_regex = agent_cfg.load_run
        if load_run_regex in (None, "", "-1"):
            load_run_regex = ".*"
        load_ckpt_regex = getattr(agent_cfg, "load_checkpoint", None)
        if load_ckpt_regex in (None, "", "-1"):
            load_ckpt_regex = r"model_.*\\.pt"
        else:
            # If a numeric iteration is provided (e.g., "999"), match exactly model_999.pt
            if isinstance(load_ckpt_regex, (int, float)) or (isinstance(load_ckpt_regex, str) and load_ckpt_regex.isdigit()):
                load_ckpt_regex = rf"model_{int(load_ckpt_regex)}\\.pt"

        # Fallback: if latest run has no checkpoints, scan previous runs until one matches
        def _find_latest_ckpt_with_fallback(root_path: str, run_regex: str, ckpt_regex: str) -> str:
            # collect candidate runs matching regex
            runs = [d.name for d in os.scandir(root_path) if d.is_dir() and re.match(run_regex, d.name)]
            if not runs:
                raise ValueError(f"No runs present in the directory: '{root_path}' match: '{run_regex}'.")
            runs.sort()
            # iterate from latest to oldest
            for run_name in reversed(runs):
                try:
                    # escape run_name to match exactly this folder
                    exact_run_regex = re.escape(run_name)
                    return get_checkpoint_path(root_path, exact_run_regex, ckpt_regex)
                except ValueError:
                    continue
            raise ValueError(
                f"No checkpoints found in any runs under '{root_path}' matching run='{run_regex}', checkpoint='{ckpt_regex}'."
            )

        resume_path = _find_latest_ckpt_with_fallback(log_root_path, load_run_regex, load_ckpt_regex)

    # wrap for video recording
    if args_cli.video:
        video_kwargs = {
            "video_folder": os.path.join(log_dir, "videos", "train"),
            "step_trigger": lambda step: step % args_cli.video_interval == 0,
            "video_length": args_cli.video_length,
            "disable_logger": True,
        }
        print("[INFO] Recording videos during training.")
        print_dict(video_kwargs, nesting=4)
        env = gym.wrappers.RecordVideo(env, **video_kwargs)

    # wrap around environment for rsl-rl
    env = RslRlVecEnvWrapper(env)

    # create runner from rsl-rl
    runner = SymmOnPolicyRunner(env=env, train_cfg=agent_cfg.to_dict(), log_dir=log_dir, device=agent_cfg.device)
    # write git state to logs
    runner.add_git_repo_to_log(__file__)
    # load the checkpoint
    if agent_cfg.resume:
        print(f"[INFO]: Loading model checkpoint from: {resume_path}")
        # load previously trained model
        runner.load(resume_path)

    # dump the configuration into log-directory
    dump_yaml(os.path.join(log_dir, "params", "env.yaml"), env_cfg)
    dump_yaml(os.path.join(log_dir, "params", "agent.yaml"), agent_cfg)
    dump_pickle(os.path.join(log_dir, "params", "env.pkl"), env_cfg)
    dump_pickle(os.path.join(log_dir, "params", "agent.pkl"), agent_cfg)

    # run training
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)

    # Export policy as jit/onnx
    # Resolve latest checkpoint for export stage as well
    load_run_regex = agent_cfg.load_run if agent_cfg.load_run not in (None, "", "-1") else ".*"
    load_ckpt_regex = getattr(agent_cfg, "load_checkpoint", None)
    if load_ckpt_regex in (None, "", "-1"):
        load_ckpt_regex = r"model_.*\\.pt"
    else:
        if isinstance(load_ckpt_regex, (int, float)) or (isinstance(load_ckpt_regex, str) and load_ckpt_regex.isdigit()):
            load_ckpt_regex = rf"model_{int(load_ckpt_regex)}\\.pt"
    # reuse the fallback resolution for export stage as well
    resume_path = _find_latest_ckpt_with_fallback(log_root_path, load_run_regex, load_ckpt_regex)
    runner.load(resume_path)
    # obtain the trained policy for inference
    policy = runner.get_inference_policy(device=env.unwrapped.device)
    # export policy to onnx/jit
    ckpt_path = os.path.join(os.path.dirname(resume_path), "exported")

    # Convert Equivariant modules into standard torch modules.
    policy = runner.alg.policy.export() if hasattr(runner.alg.policy, "export") else runner.alg.policy
    export_policy_as_jit(policy, runner.obs_normalizer, path=ckpt_path, filename="policy.pt")
    export_policy_as_onnx(policy, normalizer=runner.obs_normalizer, path=ckpt_path, filename="policy.onnx")

    # close the simulator
    env.close()


if __name__ == "__main__":
    # run the main function
    main()
    # close sim app
    simulation_app.close()
