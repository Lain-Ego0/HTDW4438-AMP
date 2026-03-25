# AMP流程和数据集导入

[中文](./zh.md) | [English](./en.md)

默认任务按 `aliengo_stairs_amp` 讲。

```bash
python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless
```

运行后效果：
- 训练开始滚动打印 `Learning iteration ...`
- 会在 `logs/stairs_aliengo/` 下新建一个时间戳目录
- 目录里有 `config.json` 和模型权重 `model_*.pt`

可以用下面命令确认日志目录是否创建成功：

```bash
ls -lt logs/stairs_aliengo | head
```

运行后效果：
- 第一行一般是最新一次训练生成的目录（时间在最前）

---

## 2. AMP 调用链

### 2.1 训练入口

```bash
sed -n '49,57p' legged_gym/legged_gym/scripts/train.py
```

运行后效果：
- 能看到 `make_env -> make_alg_runner -> learn` 三步

### 2.2 任务注册

```bash
sed -n '49,56p' legged_gym/legged_gym/envs/__init__.py
```

运行后效果：
- 能看到 `aliengo_stairs_amp` 对应 `LeggedRobot` 和 `AlienGoStairsAmpCfg`

### 2.3 runner选择

```bash
sed -n '150,160p' legged_gym/legged_gym/utils/task_registry.py
```

运行后效果：
- 能看到 `runner_class = eval(train_cfg.runner_class_name)`
- 也就是最终 runner 由配置字段决定

---

## 3. `aliengo_stairs_amp` 配置

```bash
sed -n '35,55p;301,355p' legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py
```

运行后效果：
- 会看到 `using_amp = True`
- 会看到 `runner_class_name = 'HybridPolicyRunner'`
- 会看到 `algorithm_class_name = 'HybridPPO'`
- 会看到 `amp_motion_files`、`amp_reward_coef` 等 AMP 参数

这里就是整条 AMP 路径的“总开关”。

---

## 4. rollout 阶段 AMP 在做什么

```bash
sed -n '100,120p;146,205p' rsl_rl/rsl_rl/runners/hybrid_runner.py
```

运行后效果：
- 初始化里创建 `AMPLoader`（专家数据）、`Normalizer`、`AMPDiscriminator`
- 每个 env step 都会拿 `amp_obs`、`next_amp_obs`
- 调 `predict_amp_reward(...)` 把奖励换成（或混合成）AMP奖励

简单说：策略在环境里跑，判别器负责告诉它“像不像专家动作”。

---

## 5. 更新阶段（PPO + AMP）是怎么拼在一起的

```bash
sed -n '170,185p;240,270p' rsl_rl/rsl_rl/algorithms/hybrid_ppo.py
```

运行后效果：
- 能看到 `amp_policy_generator`（策略样本）和 `amp_expert_generator`（专家样本）
- 能看到判别器损失和 PPO 损失一起加总

也就是说这里不是“先PPO后AMP”，而是一次反向传播里一起优化。

---

## 6. 数据集导入：入口、格式、读取

### 6.1 数据文件列表入口

```bash
sed -n '35,40p;348,350p' legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py
```

运行后效果：
- 能看到 `MOTION_FILES` 用 `glob` 收集 `datasets/mocap_motions_aliengo/*.txt`
- 然后赋给 `amp_motion_files`

只要改这里，训练就会换数据源。

### 6.2 看一个真实数据文件格式

```bash
head -n 30 datasets/mocap_motions_aliengo/trot0.txt
```

运行后效果：
- 会看到 JSON 结构（虽然扩展名是 `.txt`）
- 至少有 `FrameDuration`、`MotionWeight`、`Frames`

### 6.3 代码里如何读取这些字段

```bash
sed -n '76,120p' rsl_rl/rsl_rl/datasets/motion_loader.py
```

运行后效果：
- `json.load(f)` 读取文件
- 读取 `motion_json["Frames"]`
- 读取 `MotionWeight` 做加权采样
- 读取 `FrameDuration` 算轨迹时长

---

## 7. AMP 观测维度对齐

### 7.1 环境侧输出什么 AMP 观测

```bash
sed -n '481,494p' legged_gym/legged_gym/envs/base/legged_robot.py
```

运行后效果：
- 会看到返回的是：`joint_pos + base_ang_vel + joint_vel + z_pos`
- 维度是 `12 + 3 + 12 + 1 = 28`

### 7.2 数据侧取的字段是否一致

```bash
sed -n '321,333p;347,354p' rsl_rl/rsl_rl/datasets/motion_loader.py
```

运行后效果：
- 能看到专家状态也取了关节位置、角速度/关节速度和 `root z`
- 这里如果和环境侧不一致，训练会明显不稳定

---

## 8. 替换成你自己的数据集

### 步骤1：放文件

```bash
mkdir -p datasets/my_motions
ls datasets/my_motions
```

运行后效果：
- 新目录创建成功，先为空

把你自己的 JSON 格式 AMP 文件放进去（后缀可以继续用 `.txt`）。

### 步骤2：改配置

把 `legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py` 里的 `MOTION_FILES` 改成：

```python
MOTION_FILES = glob.glob(str(MOTION_FILES_DIR / 'my_motions/*.txt'))
```

### 步骤3：确认 glob 生效

```bash
python - <<'PY'
import glob
print(glob.glob('datasets/my_motions/*.txt'))
PY
```

运行后效果：
- 打印出文件列表

### 步骤4：开训

```bash
python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless
```

运行后效果：
- 训练正常启动并持续迭代
- 如果数据格式有问题，会在启动阶段就报 JSON/维度相关错误

---

## 9. 常见报错快速定位

1. JSON解析报错  
先跑：
```bash
python -m json.tool datasets/my_motions/你的文件.txt > /tmp/ok.json
```
运行后效果：
- 不报错：文件是合法 JSON
- 报错：先修 JSON 语法

2. 训练能跑但效果很差  
优先检查第 7 节的观测对齐。

1. 没有加载到任何 motion 文件  
先跑第 8.3 的 glob 检查，确认不是空列表。

---

## 10. 相关脚本

如果你从关键点数据重定向动作，可以看：
- `datasets/retarget_kp_motions.py`
- `datasets/retarget_utils.py`

`retarget_utils.py` 里的 `output_motion()` 会直接写出 AMP 需要的 JSON 结构。
