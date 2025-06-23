import isaaclab.sim as sim_utils
import isaaclab.terrains as terrain_gen
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, ImuCfg, RayCasterCfg, patterns
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG  # For completeness
from isaaclab.terrains.terrain_generator_cfg import TerrainGeneratorCfg
from isaaclab.utils import configclass
from isaaclab.utils.noise import GaussianNoiseCfg, NoiseModelWithAdditiveBiasCfg

# Import robot-specific assets from respective modules.
from basic_locomotion_dls_isaaclab.tasks.custom_curriculums import terrain_levels_vel
from basic_locomotion_dls_isaaclab.tasks.custom_events import randomize_joint_friction_model
from basic_locomotion_dls_isaaclab.tasks.locomotion.quadruped_randomization_events import EventCfg


@configclass
class BaseQuadrupedEnvCfg(DirectRLEnvCfg):
    """Base configuration for all quadruped robots in all terrain types."""

    # Common environment parameters
    episode_length_s = 20.0  # [seconds ?]
    decimation = 4
    action_scale = 0.5
    action_space = 12
    observation_space = None  # Base value; may be modified by clock signal and history
    state_space = 0

    # Flags for observation modification
    use_clock_signal: bool = True
    history_length: int = 1
    use_observation_history: bool = False
    use_filter_actions: bool = True
    use_asymmetric_ppo: bool = False
    use_amp: bool = False

    # Simulation configuration (common to all)
    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=4,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )

    # Terrain configuration: default flat terrain
    terrain: TerrainImporterCfg = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    # SENSORS ==================================================================================
    # Height scanner and IMU sensor configuration
    height_scanner: RayCasterCfg = RayCasterCfg(
        prim_path="/World/envs/env_.*/Robot/base",
        offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 0.0)),
        attach_yaw_only=True,
        pattern_cfg=patterns.GridPatternCfg(resolution=0.2, size=[1.6, 1.0]),
        debug_vis=False,
        mesh_prim_paths=["/World/ground"],
    )
    imu: ImuCfg = ImuCfg(prim_path="/World/envs/env_.*/Robot/base", debug_vis=False)

    # SCENE = ==============================================================================
    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=4096, env_spacing=4.0, replicate_physics=True)

    # RANDOMIZATION ========================================================================
    # Common events, noise models and contact sensor configuration
    events: EventCfg = EventCfg()

    action_noise_model: NoiseModelWithAdditiveBiasCfg = NoiseModelWithAdditiveBiasCfg(
        noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.05, operation="add"),
        bias_noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.015, operation="abs"),
    )
    observation_noise_model: NoiseModelWithAdditiveBiasCfg = NoiseModelWithAdditiveBiasCfg(
        noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.002, operation="add"),
        bias_noise_cfg=GaussianNoiseCfg(mean=0.0, std=0.0001, operation="abs"),
    )
    contact_sensor: ContactSensorCfg = ContactSensorCfg(
        prim_path="/World/envs/env_.*/Robot/.*",
        history_length=3,
        update_period=0.005,
        track_air_time=True,
    )

    # REWARD CONFIGURATION ========================================================================
    # Base state rewards --------------------------------------------------------
    lin_vel_reward_scale = 2.0
    yaw_rate_reward_scale = 0.5
    z_vel_reward_scale = -2.0
    ang_vel_reward_scale = -0.25
    orientation_reward_scale = -5.0
    height_reward_scale = 1.0

    # Joint space rewards -------------------------------------------------------
    joints_torque_reward_scale = -2.5e-6
    joints_accel_reward_scale = -2.5e-7
    joints_energy_reward_scale = -1e-4
    joints_hip_position_reward_scale = -0.1
    joints_thigh_position_reward_scale = -0.1
    joints_calf_position_reward_scale = -0.001

    # Undesired contacts reward scale -------------------------------------------
    undersired_contact_reward_scale = -1.0
    action_rate_reward_scale = -0.01
    action_smoothness_reward_scale = -0.001

    # Feet reward scale ---------------------------------------------------------
    feet_air_time_reward_scale = 0.5 * 0.0
    feet_height_clearance_reward_scale = 0.25
    feet_height_clearance_mujoco_reward_scale = 0.25 * 0.0
    feet_slide_reward_scale = -0.25 * 0.0
    feet_contact_suggestion_reward_scale = 0.25
    feet_to_base_distance_reward_scale = 0.25 * 0.0
    feet_to_hip_distance_reward_scale = 1.5
    feet_vertical_surface_contacts_reward_scale = -0.25 * 0.0

    # TARGET VARIABLES ============================================================================
    # Desired tracking variables (default; to be overridden where needed)
    desired_base_height = None  # Specific to robot
    desired_feet_height = None  # Specific to robot
    desired_clip_actions = 3.0

    # Placeholder for robot asset configuration; must be overridden in derived classes.
    robot: ArticulationCfg = None

    def __post_init__(self):  # noqa: D105
        print(f"Initializing {self.__class__.__name__} with:___________")
        if self.use_clock_signal:
            # Add clock signal to observation space.
            self.observation_space += 4
        if self.use_observation_history:
            # Extend observation space for history length.
            self.observation_space = int(self.observation_space * self.history_length)
        if self.use_asymmetric_ppo:
            self.state_space = self.observation_space
            self.state_space += 12  # P gain
            self.state_space += 12  # D gain
            # self.state_space += 1*17 # mass*num_bodies
            # self.state_space += 1*17 # inertia*num_bodies
            # self.state_space += 1 # wrench
            self.state_space += 12  # friction static
            self.state_space += 12  # friction dynamic
            self.state_space += 12  # armature
            # self.state_space += 1 # restitution

        cname = self.__class__.__name__
        assert self.desired_base_height is not None, f"desired_base_height must be set in {cname}."
        assert self.desired_feet_height is not None, f"desired_feet_height must be set in {cname}."
        print(f"{self.observation_space}")


@configclass
class BaseQuadrupedRoughEnvCfg(BaseQuadrupedEnvCfg):
    """Base configuration for quadruped robots in rough terrain environments."""

    # Common rough environment settings
    rough_terrain_generator = TerrainGeneratorCfg(
        curriculum=False,
        size=(8.0, 8.0),
        border_width=20.0,
        num_rows=10,
        num_cols=20,
        horizontal_scale=0.1,
        vertical_scale=0.005,
        slope_threshold=0.75,
        use_cache=False,
        sub_terrains={
            "flat": terrain_gen.MeshPlaneTerrainCfg(
                proportion=0.2
            ),
            "boxes": terrain_gen.MeshRandomGridTerrainCfg(
                proportion=0.2, grid_width=0.45, grid_height_range=(0.05, 0.10), platform_width=2.0,
            ),
            "random_rough": terrain_gen.HfRandomUniformTerrainCfg(
                proportion=0.1, noise_range=(0.02, 0.06), noise_step=0.02, border_width=0.25
            ),
            "hf_pyramid_slope": terrain_gen.HfPyramidSlopedTerrainCfg(
                proportion=0.1, slope_range=(0.2, 0.4), platform_width=2.0, border_width=0.25
            ),
            "hf_pyramid_slope_inv": terrain_gen.HfInvertedPyramidSlopedTerrainCfg(
                proportion=0.1, slope_range=(0.2, 0.4), platform_width=2.0, border_width=0.25
            ),
            "pyramid_stairs": terrain_gen.MeshPyramidStairsTerrainCfg(
                proportion=0.2, step_height_range=(0.05, 0.15), step_width=0.3,
                platform_width=3.0, border_width=1.0, holes=False,
            ),
            "pyramid_stairs_inv": terrain_gen.MeshInvertedPyramidStairsTerrainCfg(
                proportion=0.1, step_height_range=(0.05, 0.15), step_width=0.3,
                platform_width=3.0, border_width=1.0, holes=False,
            ),
        },
    )
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="generator",
        terrain_generator=ROUGH_TERRAINS_CFG,
        max_init_terrain_level=10,
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        visual_material=sim_utils.MdlFileCfg(
            mdl_path="{NVIDIA_NUCLEUS_DIR}/Materials/Base/Architecture/Shingles_01.mdl",
            project_uvw=True,
        ),
        debug_vis=False,
    )


@configclass
class BaseQuadrupedRoughBlindEnvCfg(BaseQuadrupedRoughEnvCfg):
    """Base configuration for quadruped robots in rough terrain environments without vision sensors."""

    pass


@configclass
class BaseQuadrupedRoughVisionEnvCfg(BaseQuadrupedRoughEnvCfg):
    """Base configuration for quadruped robots in rough terrain environments with vision sensors."""

    # Increase observation space for vision processing.
    observation_space: int = None
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="generator",
        terrain_generator=None,  # Use the rough terrain generator defined in the class
        max_init_terrain_level=10,
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        visual_material=sim_utils.MdlFileCfg(
            mdl_path="{NVIDIA_NUCLEUS_DIR}/Materials/Base/Architecture/Shingles_01.mdl",
            project_uvw=True,
        ),
        debug_vis=False,
    )

    def __post_init__(self):  # noqa: D105
        super().__post_init__()
        self.terrain.terrain_generator = self.rough_terrain_generator


# ============================================================================
# Robot-specific environment configurations
# ============================================================================


# ------------------------------------------------------------------------------
# ALIENGO configurations
# ------------------------------------------------------------------------------
@configclass
class AliengoEnvCfg(BaseQuadrupedEnvCfg):
    """Configuration for Aliengo in flat terrain environments."""

    from basic_locomotion_dls_isaaclab.assets.aliengo_asset import ALIENGO_CFG

    # Override observation processing: add clock signal and history
    use_clock_signal: bool = True
    history_length: int = 5
    use_observation_history: bool = True
    observation_space: int = 48

    # Robot asset for Aliengo
    robot: ArticulationCfg = ALIENGO_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    # Desired tracking variables specific to Aliengo
    desired_base_height: float = 0.35
    desired_feet_height: float = 0.04
    desired_clip_actions: float = 3.0


@configclass
class AliengoRoughBlindEnvCfg(BaseQuadrupedRoughBlindEnvCfg, AliengoEnvCfg):
    """Aliengo configuration for rough terrain environments without vision sensors."""

    pass


@configclass
class AliengoRoughVisionEnvCfg(BaseQuadrupedRoughVisionEnvCfg, AliengoEnvCfg):
    """Aliengo configuration for rough terrain environments with vision sensors."""

    observation_space: int = 235


# ------------------------------------------------------------------------------
# HYQREAL configurations
# ------------------------------------------------------------------------------
@configclass
class HyQRealEnvCfg(BaseQuadrupedEnvCfg):
    """Configuration for HyQReal in flat terrain environments."""

    from basic_locomotion_dls_isaaclab.assets.hyqreal_asset import HYQREAL_CFG

    # You can adjust clock signal and history if needed.
    use_clock_signal: bool = True
    history_length: int = 3
    use_observation_history: bool = True
    observation_space: int = 48

    robot: ArticulationCfg = HYQREAL_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    desired_base_height: float = 0.5
    desired_feet_height: float = 0.04
    desired_clip_actions: float = 3.0


@configclass
class HyQRealRoughBlindEnvCfg(BaseQuadrupedRoughBlindEnvCfg, HyQRealEnvCfg):
    """HyQReal configuration for rough environments without vision sensors."""

    pass


@configclass
class HyQRealRoughVisionEnvCfg(BaseQuadrupedRoughVisionEnvCfg, HyQRealEnvCfg):
    """HyQReal configuration for rough environments with vision sensors."""

    observation_space: int = 235


# ------------------------------------------------------------------------------
# GO2 configurations
# ------------------------------------------------------------------------------
@configclass
class Go2EnvCfg(BaseQuadrupedEnvCfg):
    """Configuration for Go2 in flat terrain environments."""

    from basic_locomotion_dls_isaaclab.assets.go2_asset import GO2_CFG

    # Use default flat parameters from BaseQuadrupedEnvCfg as needed.
    observation_space: int = 48

    robot: ArticulationCfg = GO2_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    desired_base_height: float = 0.29
    desired_feet_height: float = 0.15
    desired_clip_actions: float = 10.0


@configclass
class Go2RoughBlindEnvCfg(BaseQuadrupedRoughBlindEnvCfg, Go2EnvCfg):
    """Go2 configuration for rough terrain environments without vision sensors."""

    pass


@configclass
class Go2RoughVisionEnvCfg(BaseQuadrupedRoughVisionEnvCfg, Go2EnvCfg):
    """Go2 configuration for rough terrain environments with vision sensors."""

    observation_space: int = 235
