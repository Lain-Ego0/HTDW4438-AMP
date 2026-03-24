<p align="right">
  <a href="./README.md"><img alt="Language: English" src="https://img.shields.io/badge/Language-English-1677FF"></a>
  <a href="./README.zh-CN.md"><img alt="语言: 简体中文" src="https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-00A870"></a>
</p>

## HimLoco

- 分叉自：https://github.com/InternRobotics/HIMLoco
- HIM 论文：https://arxiv.org/abs/2404.14405
- H-inf 论文：https://arxiv.org/abs/2304.08485（代码待发布）
- AMP 集成自：https://github.com/Alescontrela/AMP_for_hardware.git
- 奖励函数集成自：

### 安装
1. 创建环境并安装 PyTorch。

2. 安装 Isaac Gym：
  - 从 https://developer.nvidia.com/isaac-gym 下载并安装 Isaac Gym Preview 4
  - `cd isaacgym/python && pip install -e .`

3. 克隆本仓库。
  - `cd HIMLoco`

4. 安装 HIMLoco。
  - `cd rsl_rl && pip install -e .`
  - `cd ../legged_gym && pip install -e .`

5. 安装 LidarSensor。

- `cd LidarSensor && pip install -e .`

### 使用
1. 训练策略：
* 平地地形
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo --headless`
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_recover --headless`
  - 使用 lidar：
      - 如果考虑机器人自遮挡，需要先合并机器人网格：`python legged_gym/resources/robots/aliengo/process_body_mesh.py`，
        然后在环境配置中设置 `consider_self_occlusion=True`（当前自遮挡后的光线追踪仍有一些问题）
      - `python legged_gym/legged_gym/scripts/train.py --task aliengo_lidar --headless`
* 楼梯地形
  - 在 `legged_gym/legged_gym/envs/aliengo/aliengo_stairs_config.py` 第 192 行修改平地训练日志路径 `load_run = ...`，并将 `resume = True`
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs --headless`
  
    或者
  - `python legged_gym/legged_gym/scripts/train --task aliengo_stairs --resume --load_run Jul29_14-35-18_ --headless`

* 使用 AMP
  - 推荐直接进行 1-stage 训练（见 [aliengo_stairs_amp_config.py](legged_gym/legged_gym/envs/aliengo/aliengo_stairs_amp_config.py)）：
  - `python legged_gym/legged_gym/scripts/train.py --task aliengo_stairs_amp --headless`


2. 回放并导出最新策略：
   - `python legged_gym/legged_gym/scripts/play.py --task aliengo --load_run <run_name> --load_cfg`
   - `python legged_gym/legged_gym/scripts/play.py --task aliengo_stairs --load_run <run_name> --load_cfg`
   - 训练 aliengo_stairs_amp，并以随机 `vel_x`（-2.0 到 2.0）、`yaw`（-1.0 到 1.0）回放：
   - ![amp_2stage.gif](projects/assets/amp_2stage.gif)
   - 一些预训练权重 [链接](https://drive.google.com/drive/folders/1BSknmyXVngnZQTRyra1fTVmoVvp5cZWq?usp=sharing)
