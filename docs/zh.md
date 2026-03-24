以你这个仓库默认的 `--task aliengo_stairs_amp` 来看，AMP 是“融合在 HybridPPO 里”实现的，不是独立一套流程。

1. 任务配置开启 AMP，并指定 runner/算法为 `HybridPolicyRunner + HybridPPO`，同时给出 AMP 超参（`amp_reward_coef=0.02`、`amp_task_reward_lerp=0.5`、判别器层数等）。  
[aliengo_stairs_amp_config.py#L303](/home/lxy/文档/GitHub/HTDW4438-AMP/legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py#L303)  
[aliengo_stairs_amp_config.py#L348](/home/lxy/文档/GitHub/HTDW4438-AMP/legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py#L348)

2. 训练时先构建 `AMPLoader`（专家动作数据）、`Normalizer`、`AMPDiscriminator`。  
[hybrid_runner.py#L105](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/runners/hybrid_runner.py#L105)

3. 每步 rollout 用 `env.get_amp_observations()` 得到当前/下一时刻 AMP 状态，并用判别器把环境任务奖励改成“AMP奖励与任务奖励的混合”。  
[hybrid_runner.py#L148](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/runners/hybrid_runner.py#L148)  
[hybrid_runner.py#L194](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/runners/hybrid_runner.py#L194)  
[amp_discriminator.py#L64](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/algorithms/amp_discriminator.py#L64)

4. 更新时同时做 PPO 和 AMP 判别器训练：  
- policy transition 来自 replay buffer；expert transition 来自 `AMPLoader`。  
- 判别器目标是 expert->`+1`、policy->`-1`，再加 gradient penalty。  
[hybrid_ppo.py#L175](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/algorithms/hybrid_ppo.py#L175)  
[hybrid_ppo.py#L252](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/algorithms/hybrid_ppo.py#L252)  
[hybrid_ppo.py#L263](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/algorithms/hybrid_ppo.py#L263)

5. AMP 观测当前是 28 维：`joint_pos(12) + base_ang_vel(3) + joint_vel(12) + z(1)`，环境侧与数据侧是对应的。  
[legged_robot.py#L481](/home/lxy/文档/GitHub/HTDW4438-AMP/legged_gym/legged_gym/envs/base/legged_robot.py#L481)  
[motion_loader.py#L321](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/datasets/motion_loader.py#L321)  
[motion_loader.py#L353](/home/lxy/文档/GitHub/HTDW4438-AMP/rsl_rl/rsl_rl/datasets/motion_loader.py#L353)

用的数据集（当前 AMP 任务）是：

1. `datasets/mocap_motions_aliengo` 下的 7 个 retarget gait 文件（由 `left* + right* + trot*` 组成）：  
`left_turn0/1`, `right_turn0/1`, `trot0/1/2`。  
[aliengo_stairs_amp_config.py#L35](/home/lxy/文档/GitHub/HTDW4438-AMP/legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py#L35)

2. 单个数据文件是 JSON 文本，包含 `FrameDuration`、`MotionWeight`、`Frames`。  
[trot0.txt#L1](/home/lxy/文档/GitHub/HTDW4438-AMP/datasets/mocap_motions_aliengo/trot0.txt#L1)

3. 仓库里也保留了 `datasets/official`（AMP_for_hardware 官方格式）作为可选来源，但当前 `aliengo_stairs_amp` 配置默认不是用它。  
[legged_robot_config.py#L37](/home/lxy/文档/GitHub/HTDW4438-AMP/legged_gym/legged_gym/envs/base/legged_robot_config.py#L37)