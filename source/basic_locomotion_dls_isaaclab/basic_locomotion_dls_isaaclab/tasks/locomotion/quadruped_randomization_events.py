import basic_locomotion_dls_isaaclab.tasks.custom_events as custom_events  # noqa: I001
import isaaclab.envs.mdp as mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.utils import configclass
from isaaclab.managers import SceneEntityCfg


@configclass
class EventCfg:
    """Configuration for randomization."""

    physics_material = EventTerm(
        func=mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.2, 1.25),
            "dynamic_friction_range": (0.2, 1.25),
            "restitution_range": (0.0, 0.1),
            "num_buckets": 64,
        },
    )

    add_base_mass = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base"),
            "mass_distribution_params": (-5.0, 5.0),
            "operation": "add",
        },
    )

    scale_all_link_masses = EventTerm(
        func=mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "mass_distribution_params": (0.9, 1.1),
            "operation": "scale",
        },
    )

    base_external_force_torque = EventTerm(
        func=mdp.apply_external_force_torque,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="base"),
            "force_range": (-5.0, 5.0),
            "torque_range": (-5.0, 5.0),
        },
    )

    """add_all_joint_default_pos = EventTerm(
        func=mdp.randomize_joint_default_pos,
        mode="startup",
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*"]), "pos_distribution_params": (-0.05, 0.05),
                "operation": "add"},
    )"""

    """joint_parameters = EventTerm(
    func=mdp.randomize_joint_parameters,
    mode="reset",
    params={
        "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
        "armature_distribution_params": (0.0, 0.2),
        "operation": "add",
        "distribution": "uniform",
    },
    )"""

    scale_all_joint_friction_model = EventTerm(
        func=custom_events.randomize_joint_friction_model,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*"]),
            "friction_distribution_params": (0.2, 2.0),
            "operation": "scale",
        },
    )

    scale_all_joint_armature_model = EventTerm(
        func=custom_events.randomize_joint_friction_model,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=[".*"]),
            "armature_distribution_params": (0.0, 1.0),
            "operation": "scale",
        },
    )

    actuator_gains = EventTerm(
        func=mdp.randomize_actuator_gains,
        mode="reset",
        params={
            "asset_cfg": SceneEntityCfg("robot", joint_names=".*"),
            "stiffness_distribution_params": (-5.0, 5.0),
            "damping_distribution_params": (-1.0, 1.0),
            "operation": "add",
            "distribution": "uniform",
        },
    )

    # interval
    push_robot = EventTerm(
        func=mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(10.0, 15.0),
        params={
            "velocity_range": {
                "x": (-0.5, 0.5),
                "y": (-0.5, 0.5),
                "z": (-0.5, 0.5),
                "roll": (-0.5, 0.5),
                "pitch": (-0.5, 0.5),
                "yaw": (-0.5, 0.5),
            }
        },
    )
