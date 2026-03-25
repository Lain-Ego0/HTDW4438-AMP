# AMP Workflow and Dataset Import

[中文](./zh.md) | [English](./en.md)

This guide uses `aliengo_stairs_amp` as the default task.

```bash
python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless
```

Expected result after running:
- Training starts and prints `Learning iteration ...`
- A timestamped directory is created under `logs/stairs_aliengo/`
- The directory contains `config.json` and model weights `model_*.pt`

You can verify the log directory was created with:

```bash
ls -lt logs/stairs_aliengo | head
```

Expected result:
- The first row is usually the latest training run directory (newest timestamp first)

---

## 2. AMP Call Chain

### 2.1 Training Entry

```bash
sed -n '49,57p' legged_gym/legged_gym/scripts/train.py
```

Expected result:
- You can see the 3-step pipeline: `make_env -> make_alg_runner -> learn`

### 2.2 Task Registration

```bash
sed -n '49,56p' legged_gym/legged_gym/envs/__init__.py
```

Expected result:
- You can see `aliengo_stairs_amp` mapped to `LeggedRobot` and `AlienGoStairsAmpCfg`

### 2.3 Runner Selection

```bash
sed -n '150,160p' legged_gym/legged_gym/utils/task_registry.py
```

Expected result:
- You can see `runner_class = eval(train_cfg.runner_class_name)`
- So the final runner is selected by a config field

---

## 3. `aliengo_stairs_amp` Configuration

```bash
sed -n '35,55p;301,355p' legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py
```

Expected result:
- You will see `using_amp = True`
- You will see `runner_class_name = 'HybridPolicyRunner'`
- You will see `algorithm_class_name = 'HybridPPO'`
- You will see AMP-related parameters like `amp_motion_files`, `amp_reward_coef`

This is the main switchboard for the full AMP path.

---

## 4. What AMP Does During Rollout

```bash
sed -n '100,120p;146,205p' rsl_rl/rsl_rl/runners/hybrid_runner.py
```

Expected result:
- Initialization creates `AMPLoader` (expert data), `Normalizer`, and `AMPDiscriminator`
- At every env step, it reads `amp_obs` and `next_amp_obs`
- It calls `predict_amp_reward(...)` to replace (or blend) rewards with AMP rewards

In short: the policy runs in the environment, and the discriminator tells it whether motions look expert-like.

---

## 5. How the Update Stage Combines PPO + AMP

```bash
sed -n '170,185p;240,270p' rsl_rl/rsl_rl/algorithms/hybrid_ppo.py
```

Expected result:
- You can see `amp_policy_generator` (policy samples) and `amp_expert_generator` (expert samples)
- You can see discriminator loss added together with PPO loss

So this is not “PPO first, AMP later”; both are optimized in one backprop pass.

---

## 6. Dataset Import: Entry, Format, Loading

### 6.1 Motion File List Entry

```bash
sed -n '35,40p;348,350p' legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py
```

Expected result:
- You can see `MOTION_FILES` collecting `datasets/mocap_motions_aliengo/*.txt` via `glob`
- Then it is assigned to `amp_motion_files`

Changing this part switches the data source for training.

### 6.2 Inspect a Real Data File Format

```bash
head -n 30 datasets/mocap_motions_aliengo/trot0.txt
```

Expected result:
- You can see JSON structure (even though the extension is `.txt`)
- It contains at least `FrameDuration`, `MotionWeight`, and `Frames`

### 6.3 How Code Reads These Fields

```bash
sed -n '76,120p' rsl_rl/rsl_rl/datasets/motion_loader.py
```

Expected result:
- `json.load(f)` reads the file
- `motion_json["Frames"]` is loaded
- `MotionWeight` is used for weighted sampling
- `FrameDuration` is used to compute trajectory length

---

## 7. AMP Observation Dimension Alignment

### 7.1 What AMP Observations the Environment Outputs

```bash
sed -n '481,494p' legged_gym/legged_gym/envs/base/legged_robot.py
```

Expected result:
- You can see the returned vector is: `joint_pos + base_ang_vel + joint_vel + z_pos`
- Total dimension is `12 + 3 + 12 + 1 = 28`

### 7.2 Whether Dataset Fields Match It

```bash
sed -n '321,333p;347,354p' rsl_rl/rsl_rl/datasets/motion_loader.py
```

Expected result:
- You can see expert states also include joint positions, angular/joint velocity, and `root z`
- If this mismatches the env side, training becomes unstable quickly

---

## 8. Replace With Your Own Dataset

### Step 1: Put Files in Place

```bash
mkdir -p datasets/my_motions
ls datasets/my_motions
```

Expected result:
- New directory is created successfully and is initially empty

Put your own AMP JSON files there (you can keep `.txt` extensions).

### Step 2: Update Config

Change `MOTION_FILES` in `legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py` to:

```python
MOTION_FILES = glob.glob(str(MOTION_FILES_DIR / 'my_motions/*.txt'))
```

### Step 3: Verify `glob` Works

```bash
python - <<'PY'
import glob
print(glob.glob('datasets/my_motions/*.txt'))
PY
```

Expected result:
- It prints your file list

### Step 4: Start Training

```bash
python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless
```

Expected result:
- Training starts normally and keeps iterating
- If data format is wrong, you will see JSON/dimension errors during startup

---

## 9. Common Errors and Fast Debugging

1. JSON parse error
Run:
```bash
python -m json.tool datasets/my_motions/your_file.txt > /tmp/ok.json
```
Expected result:
- No error: file is valid JSON
- Error appears: fix JSON syntax first

2. Training runs but quality is poor
Check observation alignment in Section 7 first.

3. No motion files loaded
Run the `glob` check in Section 8.3 and confirm it is not an empty list.

---

## 10. Related Scripts

If you retarget motion from keypoint data, check:
- `datasets/retarget_kp_motions.py`
- `datasets/retarget_utils.py`

`output_motion()` in `retarget_utils.py` directly writes the AMP-required JSON structure.
