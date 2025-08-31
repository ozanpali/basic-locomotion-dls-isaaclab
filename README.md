# Overview


This repository is about basic RL quadruped locomotion tasks within the robots available at DLS. 

Features:
- [Cuncurrent State Estimator](https://arxiv.org/pdf/2202.05481)
- [Rapid Motor Adaptation](https://arxiv.org/pdf/2107.04034)
- [Morphologycal Symmetries](https://arxiv.org/pdf/2403.17320) 
- [Adversarial Motion Priors](https://arxiv.org/pdf/2104.02180)
- Sim-to-Sim in [Mujoco](https://github.com/google-deepmind/mujoco)
- Sim-to-Real in ROS1 and ROS2

| Robot Model         | Environment Name (ID)                                      | Screenshot |
|---------------------|------------------------------------------------------------|------------|
| [Aliengo](https://github.com/iit-DLSLab/gym-quadruped/tree/master/gym_quadruped/robot_model/aliengo) | Locomotion-Aliengo-Flat <br> Locomotion-Aliengo-Rough-Blind <br> Locomotion-Aliengo-Rough-Vision  | <img src="./imgs/deeprobotics_lite3.png" alt="Lite3" width="150">
| [Go2](https://github.com/iit-DLSLab/gym-quadruped/tree/master/gym_quadruped/robot_model/go2) | Locomotion-Go2-Flat <br> Locomotion-Go2-Rough-Blind <br> Locomotion-Go2-Rough-Vision | <img src="./imgs/deeprobotics_m20.png" alt="deeprobotics_m20" width="150">
| [B2](https://github.com/iit-DLSLab/gym-quadruped/tree/master/gym_quadruped/robot_model/b2) | Locomotion-B2-Flat <br> Locomotion-B2-Rough-Blind <br> Locomotion-B2-Rough-Vision | <img src="./imgs/deeprobotics_m20.png" alt="deeprobotics_m20" width="150">
| [HyQReal2](https://github.com/iit-DLSLab/gym-quadruped/tree/master/gym_quadruped/robot_model/hyqreal2) | Locomotion-HyQReal-Flat <br> Locomotion-HyQReal-Rough-Blind <br> Locomotion-HyQReal-Rough-Vision | <img src="./imgs/deeprobotics_m20.png" alt="deeprobotics_m20" width="150">


## Citing this work

If you find the work useful and you adopt [Morphologycal Symmetries](https://arxiv.org/pdf/2403.17320), please consider citing one of our works:

#### [Leveraging Symmetry in RL-based Legged Locomotion Control (IROS-2024)](https://arxiv.org/pdf/2403.17320)

```
@inproceedings{suhuang2024leveraging,
  author={Su, Zhi and Huang, Xiaoyu and Ordoñez-Apraez, Daniel and Li, Yunfei and Li, Zhongyu and Liao, Qiayuan and Turrisi, Giulio and Pontil, Massimiliano and Semini, Claudio and Wu, Yi and Sreenath, Koushil},
  booktitle={2024 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)}, 
  title={Leveraging Symmetry in RL-based Legged Locomotion Control}, 
  year={2024},
  pages={6899-6906},
  doi={10.1109/IROS58592.2024.10802439}
}
```

#### [Morphological symmetries in robotics (IJRR-2025)](https://arxiv.org/pdf/2402.15552):

```
@article{ordonez2025morphosymm,
  author = {Daniel Ordoñez-Apraez and Giulio Turrisi and Vladimir Kostic and Mario Martin and Antonio Agudo and Francesc Moreno-Noguer and Massimiliano Pontil and Claudio Semini and Carlos Mastalli},
  title ={Morphological symmetries in robotics},
  journal = {The International Journal of Robotics Research},
  year = {2025},
  doi = {10.1177/02783649241282422},
  URL = {https://doi.org/10.1177/02783649241282422},
  eprint = {https://doi.org/10.1177/02783649241282422}
}
```


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

5. If you want to play with [Morphologycal Symmetries](https://arxiv.org/pdf/2403.17320), install the repo [morphosymm-rl](https://github.com/iit-DLSLab/morphosymm-rl)


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
We use model from [gym-quadruped](https://github.com/iit-DLSLab/gym-quadruped).

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
conda env create -f mamba_environment.yml
conda activate basic_locomotion_dls_isaaclab_env
```

3. Then you can run play_mujoco.py or run play_ros2.py

```bash
## Sim-to-Sim
python3 deploy/play_mujoco.py

## Sim-to-Real
cd deploy/ros2_ws
colcon build
python3 deploy/play_ros2.py 
ros2 launch teleop_twist_joy teleop-launch.py joy_config:='xbox' (if want joystick)
```
