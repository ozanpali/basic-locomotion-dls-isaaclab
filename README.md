# Overview


This repository is about basic locomotion tasks with DLS robots. Here you can play with standard PPO, Morphologycal Symmetries, and Adversarial Motion Priors. Scripts for sim-to-sim (mujoco) and sim-to-real are provided. 


## Installation

- Install Isaac Lab by following the [installation guide](https://github.com/isaac-sim/IsaacLab). We recommend using the conda installation as it simplifies calling Python scripts from the terminal.

- Clone the repository separately from the Isaac Lab installation (i.e. outside the `IsaacLab` directory)


- Using a python interpreter that has Isaac Lab installed, install the library

```bash
python -m pip install -e source/basic_locomotion_dls_isaaclab
```

- Verify that the extension is correctly installed by running the following command:

```bash
python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Flat --num_envs=4096 --headless
python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Rough-Blind --num_envs=4096 --headless

python scripts/rsl_rl/train.py --task=Locomotion-Go2-Flat --num_envs=4096 --headless
python scripts/rsl_rl/train.py --task=Locomotion-Go2-Rough-Blind --num_envs=4096 --headless
```

- To train with Symmetries, modify the related rsl_rl_ppo_cfg.py
```bash
python scripts/rsl_rl/train_symm.py --task=Locomotion-Aliengo-Flat --num_envs=4096 --headless
python scripts/rsl_rl/train_symm.py --task=Locomotion-Aliengo-Rough-Blind --num_envs=4096 --headless
```

- To test the policy, you can press:
```bash
python scripts/rsl_rl/play.py --task=Locomotion-Aliengo-Flat --num_envs=16
python scripts/rsl_rl/play.py --task=Locomotion-Aliengo-Rough-Blind --num_envs=16

python scripts/rsl_rl/play.py --task=Locomotion-Go2-Flat --num_envs=16
python scripts/rsl_rl/play.py --task=Locomotion-Go2-Rough-Blind --num_envs=16
```

- If you want to use symmetrues, launch the file play_symm or train_symm instead

### Run Hyperparameter Search

```bash
echo "import ray; ray.init(); import time; [time.sleep(10) for _ in iter(int, 1)]" | python3 (TERMINAL 1)
```

```bash
python3 ../basic_locomotion_dls_isaaclab/exts/basic_locomotion_dls_isaaclab/basic_locomotion_dls_isaaclab/hyperparameter_tuning/tuner.py --run_mode local --cfg_file ../basic_locomotion_dls_isaaclab/exts/basic_locomotion_dls_isaaclab/basic_locomotion_dls_isaaclab/hyperparameter_tuning/locomotion_aliengo_cfg.py --cfg_class LocomotionAliengoFlatTuner (TERMINAL 2)
```


### Convert XML to USD

```bash
./isaaclab.sh -p scripts/tools/convert_mjcf.py   ../basic_locomotion_dls_isaaclab/scripts/sim_to_sim_mujoco/gym-quadruped/gym_quadruped/robot_model/aliengo/aliengo.xml   ../aliengo.usd   --import-sites   --make-instanceable
```

Remember to set in the application above, "set as default prim" to the root of the robot. Furthermore, for now, add the following lines in the xml of your robots to make the feet seen as body

```bash
<body name="FL_foot" pos="0 0 -0.25">
    <!-- FL_foot only collision -->
    <geom name="FL" class="collision" size="0.0265" pos="0 0 0" />
</body>
```


### Run Sim to Sim 
Go in the folder scripts/sim_to_others, and install gym_quadruped with 

```bash
pip install -e .
```

Then you can run play_mujoco.py
