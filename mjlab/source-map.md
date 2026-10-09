# mjlab 固定源码地图

[导读](README.md) · [首课](01-g1-task.md) · [观测与动作](02-observations-actions.md) · [随机化与课程](03-randomization-curriculum.md) · [PPO](../learning/ppo-data-path.md) · [全部版本](../docs/sources.json)

快照：`033ae22a2c7a30a25a6fa77b16c113ed88dd1b55`，源码元数据 1.6.0。下列行号只对这个提交有效。

| 入口 | 固定源码 | 带着什么问题读 |
|---|---|---|
| 包入口 | [pyproject.toml](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/pyproject.toml#L60-L67) | train/play 命令绑定到哪个 Python 函数？ |
| 任务发现 | [src/mjlab/tasks/__init__.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/__init__.py) | 导入任务包怎样填充注册表？ |
| G1 注册 | [src/mjlab/tasks/velocity/config/g1/__init__.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/__init__.py#L19-L24) | 训练配置、play 配置、算法配置和 runner 如何绑定？ |
| 注册表 | [src/mjlab/tasks/registry.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/registry.py#L48-L64) | 配置为何复制，runner 类从哪里来？ |
| 基础任务 | [src/mjlab/tasks/velocity/velocity_env_cfg.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L39-L43) | 机器人专用配置之前有哪些共享 terms？ |
| G1 配置 | [src/mjlab/tasks/velocity/config/g1/env_cfgs.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/env_cfgs.py#L188-L220) | flat 相对 rough 修改了哪些内容？ |
| PPO 参数 | [src/mjlab/tasks/velocity/config/g1/rl_cfg.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/rl_cfg.py#L10-L46) | 采样长度、更新参数与训练迭代数在哪里？ |
| 训练装配 | [src/mjlab/scripts/train.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/train.py#L49-L63) | device、seed、环境、wrapper、runner 怎样连接？ |
| 命令解析 | [src/mjlab/scripts/train.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/train.py#L230-L258) | 任务 ID 和配置覆盖为何分两次解析？ |
| 环境生命周期 | [src/mjlab/envs/manager_based_rl_env.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L386-L510) | 物理、奖励、事件、reset、forward、sense、obs 的顺序是什么？ |
| 局部重置 | [src/mjlab/envs/manager_based_rl_env.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/manager_based_rl_env.py#L580-L618) | 环境与 manager 状态怎样一起清理？ |
| 动作 | [src/mjlab/envs/mdp/actions/actions.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L154-L164) | 缩放、偏置与裁剪怎样作用？ |
| 奖励 | [src/mjlab/managers/reward_manager.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/reward_manager.py#L116-L135) | dt、权重、NaN 清理和日志如何区分？ |
| 终止 | [src/mjlab/managers/termination_manager.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/termination_manager.py#L102-L125) | timeout 与 terminated 如何分开积累？ |
| RL wrapper | [src/mjlab/rl/vecenv_wrapper.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/vecenv_wrapper.py#L72-L94) | 五项环境返回怎样变成 learner 所需结构？ |
| 基础 runner | [src/mjlab/rl/runner.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/runner.py#L11-L37) | 外部算法库与本仓扩展的分界在哪里？ |
| 速度任务 runner | [src/mjlab/tasks/velocity/rl/runner.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/rl/runner.py#L12-L27) | 保存 checkpoint 时附加了什么？ |
| 回放 | [src/mjlab/scripts/play.py](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/scripts/play.py#L59-L75) | play 配置、dummy agent 与训练策略怎样选择？ |

核对使用 Git 提交对象，未导入上述模块。源码依赖、平台支持和安装步骤请同时核对该提交的 pyproject 与上游文档。
