# mjlab：从 MuJoCo 接到机器人学习

[首页](../README.md) · [源码地图](source-map.md) · [首课：G1 速度任务](01-g1-task.md)

**先修：** [共同基础](../foundations/README.md)，MuJoCo 模型/数据/控制输入的基本区分。

**读完应能：** 指出任务配置、环境、物理后端、runner 和策略回放的职责。

固定源码：`033ae22a2c7a30a25a6fa77b16c113ed88dd1b55`；源码包元数据版本 `1.6.0`。这是阅读快照，不表示本机已安装该版本。[包与依赖](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/pyproject.toml#L5-L64)

mjlab 采用 Isaac Lab 风格的 manager 组织方式，以 MuJoCo-Warp 作为批量仿真基础。学习入口是一个具体任务 ID，而不是先记住所有类。

## 沿一个任务读

1. `tasks/velocity/config/g1/__init__.py` 注册 `Mjlab-Velocity-Flat-Unitree-G1`。
2. `unitree_g1_flat_env_cfg` 从粗糙地形配置派生场景、观测和终止条件。
3. `ManagerBasedRlEnv` 把场景、仿真和 managers 装配起来。
4. `RslRlVecEnvWrapper` 把环境结果交给 RSL-RL 所需的接口。
5. `VelocityOnPolicyRunner` 继承 `MjlabOnPolicyRunner`，再接到外部 `OnPolicyRunner`。
6. `play` 重新构建 play 配置、加载策略并交给 viewer。

每个入口都在 [源码地图](source-map.md) 中固定到行号。首课解释从命令到这些入口的完整连接；PPO loss 的具体实现留到 B4，并需固定 `rsl-rl-lib` 的实际依赖版本。

## 先看语义，再运行

阅读首课无需 GPU。后续运行先建立隔离环境、核对源码提交和依赖，遵循固定版本 README/锁文件。当前项目 README 将训练限定于 NVIDIA GPU，并把 macOS 定位于评估；本课程未独立验证各平台。[上游运行说明](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/README.md#L19-L34)

首课的零动作命令用于检查环境响应；策略播放用于观察 checkpoint；独立评估还需要冻结命令分布、随机化、种子和指标。三者回答的问题不同。

## 两个阅读练习

- 为什么修改从注册表取出的配置不应污染之后的任务创建？

  **答案：** `load_env_cfg/load_rl_cfg` 使用 `deepcopy`；同时还要检查用户代码是否共享了其他可变对象。
- 为什么 play 配置不能直接充当训练评估配置？

  **答案：** G1 play 路径会关闭 actor 观测噪声、移除推扰事件、修改回合长度和命令范围等条件。详见首课。

**本期状态：** 导读、源码地图和首课可读；源码核对脚本已执行。没有训练结果、性能结论或 sim-to-real 成功声明。
