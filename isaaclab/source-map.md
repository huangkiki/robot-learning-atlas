# Isaac Lab 固定源码地图

[导读](README.md) · [全部版本](../docs/sources.json)

`develop@07daf4426dfa8dcb6d0753768890b4f60dc54f9e`。这些路径属于该开发快照，不能用于追认旧版课程或安装环境。

| 入口 | 固定源码 | 阅读问题 |
|---|---|---|
| 版本与环境 | [README.md](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/README.md#L5-L28) | 这是开发快照还是稳定发布，宿主版本是什么？ |
| Manager 基类 | [source/isaaclab/isaaclab/envs/manager_based_env.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_env.py#L270-L277) | 物理时间与环境时间如何对应？ |
| Manager RL step | [source/isaaclab/isaaclab/envs/manager_based_rl_env.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env.py#L177-L286) | decimation、奖励、重置与 final_obs 由谁负责？ |
| Manager RL 配置 | [source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/manager_based_rl_env_cfg.py#L15-L99) | 时域与最终观测配置在哪里？ |
| Direct step | [source/isaaclab/isaaclab/envs/direct_rl_env.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/envs/direct_rl_env.py#L360-L469) | 基类何时调用任务提供的方法？ |
| Reward manager | [source/isaaclab/isaaclab/managers/reward_manager.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab/isaaclab/managers/reward_manager.py#L125-L161) | 权重与时间如何组合？ |
| RSL-RL wrapper | [source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/rsl_rl/vecenv_wrapper.py#L155-L170) | done 与 time_outs 如何送往算法？ |
| 训练入口 | [source/isaaclab_rl/isaaclab_rl/entrypoints/backends/train_rsl_rl.py](https://github.com/isaac-sim/IsaacLab/blob/07daf4426dfa8dcb6d0753768890b4f60dc54f9e/source/isaaclab_rl/isaaclab_rl/entrypoints/backends/train_rsl_rl.py) | 启动宿主、读取任务配置与创建 runner 的边界在哪里？ |

证据限于源码定位与阅读；未启动宿主、仿真器或训练。
