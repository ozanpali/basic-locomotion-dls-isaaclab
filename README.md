# Overview


This repository is about basic locomotion tasks with DLS robots. Here you can play with standard PPO, Morphologycal Symmetries, and Adversarial Motion Priors. Scripts for sim-to-sim (mujoco) and sim-to-real are provided. 


## Installation

If you want only to deploy a trained policy on your robot, go directly [at the bottom of the readme](https://github.com/iit-DLSLab/basic-locomotion-dls-isaaclab/tree/main?tab=readme-ov-file#run-sim-to-sim-and-sim-to-real).

1. Install Isaac Lab by following the [installation guide](https://github.com/isaac-sim/IsaacLab). We recommend using the conda installation as it simplifies calling Python scripts from the terminal.

2. Install git for very large file
```bash
sudo apt install git-lfs
```

3. Clone the repository separately from the Isaac Lab installation (i.e. outside the `IsaacLab` directory)


4. Using a python interpreter that has Isaac Lab installed, install the library

```bash
python -m pip install -e source/basic_locomotion_dls_isaaclab
```


### Run a train/play in IsaacLab

- To train:

```bash
python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Flat --num_envs=4096 --headless
python scripts/rsl_rl/train.py --task=Locomotion-Aliengo-Rough-Blind --num_envs=4096 --headless
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
```


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


### Run Sim-to-Sim and Sim-to-Real

1. install [miniforge](https://github.com/conda-forge/miniforge/releases) (x86_64 or arm64 depending on your platform)

2. create an environment using the file in the folder [installation](https://github.com/iit-DLSLab/basic-locomotion-dls-isaaclab/tree/main/installation):


```bash
conda env create -f mamba_environment.yml`
conda activate basic_locomotion_dls_isaaclab_env
```

3. Then you can run play_mujoco.py or run play_ros2.py

```bash
## Sim-to-Sim
python3 play_mujoco.py

## Sim-to-Real
cd ros2/msg_wd
colcon build
python3 play_ros2.py 
ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox' (if want joystick)
```