# UniLab 固定源码地图

[导读](README.md) · [全部版本](../docs/sources.json)

`cbafb5071fb0ea2d7322e1b0b648f8819b2a7499`，源码元数据 1.3.3。物理后端实现与部分学习组件位于外部包，本图只承诺已列明的 UniLab 文件。

| 入口 | 固定源码 | 阅读问题 |
|---|---|---|
| 包与命令 | [pyproject.toml](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/pyproject.toml#L66-L71) | train/eval 命令实际进入哪里？ |
| CLI | [src/unilab/cli.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/cli.py#L577-L592) | 算法和任务选择如何进入训练入口？ |
| PPO 入口 | [src/unilab/scripts/train_rsl_rl.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/scripts/train_rsl_rl.py) | 配置、环境与外部 OnPolicyRunner 如何连接？ |
| 任务配方 | [src/unilab/conf/ppo/task/go2_joystick_flat/mujoco.yaml](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/task/go2_joystick_flat/mujoco.yaml) | task_name、sim_backend 与 algo 分属哪层？ |
| 配置适配 | [src/unilab/base/config_adapter.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/config_adapter.py#L152-L168) | 最终配置怎样传入 registry？ |
| 注册表 | [src/unilab/base/registry.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/registry.py#L266-L330) | 哪个任务工厂和环境实现被选择？ |
| 后端装配 | [src/unilab/base/backend_factory.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/backend_factory.py) | 哪些逻辑在 UniLab，哪些来自 unisim？ |
| 公共生命周期 | [src/unilab/base/torch_env.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L256-L349) | 后端推进、任务更新与自动重置怎样配合？ |
| Manager 环境 | [src/unilab/envs/manager_based_rl_env.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1169-L1198) | 子类怎样调用父类及更新 manager 状态？ |
| 任务更新 | [src/unilab/envs/manager_based_rl_env.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L1215-L1307) | 终止、奖励、事件和命令以什么顺序执行？ |
| Collector 构造 | [src/unilab/base/env_factory.py](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/env_factory.py#L26-L43) | 为什么用顶层函数和可序列化 partial？ |

静态源码定位不表示任何后端/任务/硬件组合已完成运行验证。
