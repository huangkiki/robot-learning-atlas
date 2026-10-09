# 共同基础：先把一次交互说清楚

[首页](../README.md) · [课程目录](../docs/curriculum.md) · [下一课：mjlab G1](../mjlab/01-g1-task.md)

**先修：** Python 函数/类、数组形状、位置与速度的基本概念。

**目标：** 区分物理、任务与学习器；计算控制时间和采样量；正确描述结束回合的那一步。

## 1. 一条数据链，三类责任

```text
策略 π(o) → action → 动作处理/控制目标 → 物理推进 → 状态与传感器
    ↑                                                 ↓
学习器 ← rollout 与回合标记 ← reward / terminated / truncated / observation
```

- **物理引擎**根据模型、输入和数值方法推进物理状态。求解约束与计算奖励是不同工作。
- **任务/环境**定义机器人要做什么、策略看什么、控制什么、怎样计分和结束。
- **学习器**利用环境产生的转移更新策略。环境可以被零动作或随机动作驱动，环境构造成功不表示策略已经学会任务。

观测 `o` 通常只是状态的一部分，可能含噪声、历史和命令。策略 actor 与价值网络 critic 可以获得不同信息；critic 的额外状态不能顺带进入部署 actor。mjlab 的 G1 基础任务分别声明两个观测组：[actor / critic 配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L76-L171)。

## 2. 三种“步”必须分别计数

设物理步长为 `h` 秒，每次策略动作推进 `d` 次物理步：

```text
环境步长 Δt = d × h
策略频率 f = 1 / Δt
长度 T 秒的回合上限 = ceil(T / Δt)     （采用此规则的环境）
N 个环境 × H 次采样 = N × H 条转移
每个环境在一轮 rollout 中推进的模拟时间 = H × Δt
```

mjlab 的这份 G1 任务配置为 `h=0.005 s`、`d=4`、`T=20 s`，所以 `Δt=0.02 s`、`f=50 Hz`、最多 `1000` 个环境步。每轮 `H=24`，假设 `N=4096`，则收集 `98,304` 条转移，每个环境推进 `0.48 s`。4096 是示例 CLI 覆盖值；源码基础场景的 `num_envs` 是 1。来源：[时间和场景配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/velocity_env_cfg.py#L418-L456)、[rollout 配置](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/tasks/velocity/config/g1/rl_cfg.py#L42-L46)。

这些是配置推导，不能换算成训练墙钟时间、FPS 或收敛速度。并行环境数增加通常不等于单个机器人的模拟时间增加。

## 3. 动作要带着语义和单位读

神经网络输出的 action 可以是位置偏移、速度目标或力矩目标。对位置动作，简化关系为：

```text
处理后目标 = scale × 原始 action + offset
```

但这还不是执行器最终收到的全部逻辑。mjlab 的 `BaseAction.process_actions` 可能继续裁剪；`JointPositionAction` 可使用默认关节姿态作为 offset，并在应用时扣除 encoder bias，再写入关节位置目标。来源：[缩放与裁剪](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L154-L164)、[关节位置目标](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/envs/mdp/actions/actions.py#L212-L224)。

因此零动作不意味着零力矩，也不意味着把关节位置写成零。实际驱动力还取决于执行器与当前状态。

## 4. 奖励、结束和重置描述不同事实

- **reward**：这次转移的任务反馈。权重、是否乘 Δt、是否裁剪、日志如何归一化，都属于定义的一部分。
- **terminated**：任务定义的终止，例如失败或成功。
- **truncated**：外部限制截断；常见例子是持续任务的时间上限。有限时域任务的时间边界需按该任务和算法的定义处理。
- **reset**：为下一回合重新建立状态、历史和命令。它是一个操作，不是成功判据。

训练接口可能把两种结束合并成 `done`，同时在其他字段保留超时信息。mjlab 的 RSL-RL wrapper 正是这样做的：[dones 与 time_outs](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/rl/vecenv_wrapper.py#L77-L90)。是否、怎样 bootstrap 还需要继续读固定版本的算法消费者，本期尚未验证算法内部。

自动重置尤其容易误读：返回的奖励和结束标记属于刚结束的回合，而部分返回观测已经属于下一回合。终止观测必须按框架自己的接口读取，见 [三框架对照](../comparisons/lifecycle.md)。

## 5. 时间缩放只能解决一部分问题

mjlab 默认允许用 `r_step = Δt × Σ(w_i × term_i)` 近似持续时间上的奖励积分，见 [RewardManager.compute](https://github.com/mujocolab/mjlab/blob/033ae22a2c7a30a25a6fa77b16c113ed88dd1b55/src/mjlab/managers/reward_manager.py#L116-L135)。假设单位奖励率恒为 1、权重为 1、持续 20 秒且无其他处理，理论总和约为 20。

改变控制频率仍会改变动作保持时间、采样轨迹、观测时刻和折扣的物理含义。只乘 Δt 不保证两个任务等价。对于每步折扣 `γ`，经过物理时长 `t` 的折扣大约为 `γ^(t/Δt)`；比较时需要同时说明时间步。

## 练习与答案

1. 物理步长保持 5 ms，把 decimation 从 4 改成 8，策略频率、20 秒回合步数和 24 步 rollout 时长是多少？

   **答案：** 25 Hz、500 步、0.96 秒；这些都不是墙钟耗时。
2. 同一步返回 `terminated=True` 和看起来正常的站立观测，是否说明失败判定错误？

   **答案：** 不能这样判断。先检查是否同一步自动重置，以及终止观测与重置后观测的接口。
3. 把训练环境的 actor 输入替换为 critic 输入，是否只是增加信息？

   **答案：** 同时改变了策略任务与部署输入要求；若 critic 含实机不可获得的信息，部署链会失配。
4. 零 action 下机器人有力矩，是否违背接口？

   **答案：** 对位置目标动作不违背。零 action 仍可能要求保持默认姿态。

**验证范围：** 时间与采样数由附带脚本从固定源码读取并计算；动作、奖励与边界语义经过源码阅读。未执行三框架原生仿真或训练。
