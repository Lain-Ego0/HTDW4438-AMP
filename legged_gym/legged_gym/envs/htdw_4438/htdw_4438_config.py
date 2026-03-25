import math

from legged_gym.envs.aliengo.aliengo_config import AlienGoRoughCfg, AlienGoRoughCfgPPO


class HTDW4438RoughCfg(AlienGoRoughCfg):
    class init_state(AlienGoRoughCfg.init_state):
        pos = [0.0, 0.0, 0.185]
        rot = [0.0, 0.0, 0.0, 1.0]
        lin_vel = [0.0, 0.0, 0.0]
        ang_vel = [0.0, 0.0, 0.0]
        # Match joint names in htdw_4438.urdf (lowercase).
        default_joint_angles = {
            "fl_hip_joint": 0.0,
            "rl_hip_joint": 0.0,
            "fr_hip_joint": 0.0,
            "rr_hip_joint": 0.0,
            "fl_thigh_joint": 0.9,
            "rl_thigh_joint": 0.9,
            "fr_thigh_joint": 0.9,
            "rr_thigh_joint": 0.9,
            "fl_calf_joint": -1.8,
            "rl_calf_joint": -1.8,
            "fr_calf_joint": -1.8,
            "rr_calf_joint": -1.8,
        }

    class commands(AlienGoRoughCfg.commands):
        class ranges(AlienGoRoughCfg.commands.ranges):
            lin_vel_x = [-0.5, 1.0]
            lin_vel_y = [-0.5, 0.5]
            ang_vel_yaw = [-1.0, 1.0]
            heading = [-math.pi, math.pi]

    class asset(AlienGoRoughCfg.asset):
        file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/htdw_4438/urdf/htdw_4438.urdf"
        name = "htdw_4438"
        foot_name = "foot"
        penalize_contacts_on = ["hip", "thigh", "calf", "base"]
        terminate_after_contacts_on = ["base"]
        privileged_contacts_on = ["base", "thigh", "calf"]
        self_collisions = 1

    class rewards(AlienGoRoughCfg.rewards):
        soft_dof_pos_limit = 0.9
        base_height_target = 0.185
        clearance_height_target = -0.135

        class scales(AlienGoRoughCfg.rewards.scales):
            termination = -0.0
            tracking_lin_vel = 1.0
            tracking_ang_vel = 0.5
            lin_vel_z = -2.0
            ang_vel_xy = -0.05
            orientation = -1.3
            dof_acc = -2.5e-7
            joint_power = -2e-5

            base_height = -1.0
            default_pos_linear = -0.02
            diagonal_sync = -0.1
            hip_mirror_symmetry = -0.1

            foot_clearance = -0.0
            action_rate = -0.01
            smoothness = -0.01
            feet_air_time = 0.05
            feet_stumble = -0.0
            stand_still = -1.0
            torques = -0.0
            dof_vel = -0.0
            dof_pos_limits = -0.0
            dof_vel_limits = -0.0
            torque_limits = -0.0
            collision = -1.0


class HTDW4438RoughCfgPPO(AlienGoRoughCfgPPO):
    class runner(AlienGoRoughCfgPPO.runner):
        experiment_name = "rough_htdw_4438"
        run_name = ""
