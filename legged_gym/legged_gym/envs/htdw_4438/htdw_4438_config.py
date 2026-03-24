import math

from legged_gym.envs.aliengo.aliengo_config import AlienGoRoughCfg, AlienGoRoughCfgPPO


class HTDW4438RoughCfg(AlienGoRoughCfg):
    class init_state(AlienGoRoughCfg.init_state):
        pos = [0.0, 0.0, 0.50]
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
        penalize_contacts_on = ["thigh", "calf"]
        terminate_after_contacts_on = ["base"]
        privileged_contacts_on = ["base", "thigh", "calf"]
        self_collisions = 1


class HTDW4438RoughCfgPPO(AlienGoRoughCfgPPO):
    class runner(AlienGoRoughCfgPPO.runner):
        experiment_name = "rough_htdw_4438"
        run_name = ""
