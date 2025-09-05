## HimLoco

- forked from: https://github.com/InternRobotics/HIMLoco
- him paper: https://arxiv.org/abs/2404.14405
- hinf paper: https://arxiv.org/abs/2304.08485 (code to be released)
- amp integrated from: https://github.com/Alescontrela/AMP_for_hardware.git
- rewards integrated from:

### Installation
1. Create an environment and install PyTorch:

2. Install Isaac Gym:
  - Download and install Isaac Gym Preview 4 from https://developer.nvidia.com/isaac-gym
  - `cd isaacgym/python && pip install -e .`

3. Clone this repository.
  - `cd HIMLoco`

4. Install HIMLoco.
  - `cd rsl_rl && pip install -e .`
  - `cd ../legged_gym && pip install -e .`

5. Install LidarSensor

- `cd LidarSensor && pip install -e .`

### Usage
1. Train a policy:
* flat terrain
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo --headless`
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_recover --headless`
  - for lidar:
      - if consider robot sel-occlusion, should combine the robots' meshes first: `python legged_gym/resources/robots/aliengo/process_body_mesh.py`,
        then change the `consider_self_occlusion=True` in env configs (暂时自遮挡后的光线追踪有点问题)
      - `python legged_gym/legged_gym/scripts/train.py --task aliengo_lidar --headless`
* stairs terrain
  - change the resume flat terrain log path in `legged_gym/legged_gym/envs/aliengo/aliengo_stairs_config.py` lines 192 `load_run = ...` and change `resume = True`
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs --headless`
  
    or 
  - `python legged_gym/legged_gym/scripts/train --task aliengo_stairs --resume --load_run Jul29_14-35-18_ --headless`

* use amp
  - recommand direct 1-stage training (see [aliengo_stairs_amp_config.py](legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py)):
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless`


2. Play and export the latest policy:
   - `python legged_gym/legged_gym/scripts/play.py --task aliengo --load_run <run_name> --load_cfg`
   - `python legged_gym/legged_gym/scripts/play.py --task aliengo_stairs --load_run <run_name> --load_cfg`
   - train aliengo_stairs_amp and play with random vel_x from -2.0 to 2.0, yaw from -1.0 to 1.0:
   - ![amp_2stage.gif](projects/assets/amp_2stage.gif)
   - some pretrained weights [link](https://drive.google.com/drive/folders/1BSknmyXVngnZQTRyra1fTVmoVvp5cZWq?usp=sharing)
