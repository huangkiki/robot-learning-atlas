# 双路线课程目录

[首页](../README.md) · [当前任务](roadmap.md) · [共同基础](../foundations/README.md)

先沿 mjlab 的真实任务建立完整对象地图，再把同一问题带到 Isaac Lab 和 UniLab。已有链接表示本期有可读内容；“部分覆盖”表示仍有内容待写，不表示整个单元完成。

## A · 使用框架

| 单元 | 学习目标 | 本期内容 | 后续验收 |
|---|---|---|---|
| A0 对象与环境 | 分清安装包、任务、物理后端和算法 | 三框架导读，部分覆盖 | 各框架安装/版本检查与首个原生运行记录 |
| A1 定义任务 | 找到场景、机器人、配置与注册入口 | [G1](../mjlab/01-g1-task.md)、[Cartpole](../isaaclab/01-native-task.md)、[Go2](../unilab/01-native-task.md) 源码课程 | 原生配置解析与最小修改的运行对照 |
| A2 观测与动作 | 解释维度、单位、噪声、历史、缩放与控制目标 | [G1 逐字段表与位置目标](../mjlab/02-observations-actions.md)，另两框架首课对照 | 运行时读回实际 shape、名字和索引 |
| A3 奖励与终止 | 区分每步奖励、时间缩放、失败、截断和重置 | 三框架首课、[生命周期](../comparisons/lifecycle.md) 与 [GAE 边界](../learning/ppo-data-path.md) | 原生终止/截断轨迹 |
| A4 训练与评估 | 连接 rollout、runner、checkpoint 和策略回放 | 三框架训练入口与 [PPO](../learning/ppo-data-path.md)，源码部分完成 | 原生运行、独立评估和可复核产物 |
| A5 随机化与课程 | 区分 startup/reset/interval 与难度调度 | [G1 触发点、状态与命令课程](../mjlab/03-randomization-curriculum.md) | 运行时触发追踪与效果验证 |
| A6 策略迁移 | 核对观测、控制、归一化、频率和后端差异 | 待写 | 迁移检查表与实际验证范围 |

## B · 理解实现

| 单元 | 源码问题 | 本期内容 | 后续验收 |
|---|---|---|---|
| B0 配置装配 | 配置何时解析、实例化、覆盖和复制？ | 三框架首课；Go2 展开 Hydra owner 覆盖 | 原生解析配置与静态推导逐项核对 |
| B1 step/reset | 谁推进物理、刷新派生量、生成观测和重置？ | 三框架纵向课程与生命周期对照 | 原生时序追踪 |
| B2 Manager 依赖 | 观测、命令、事件之间为什么有执行顺序？ | G1 事件/课程与三框架 step/reset | 运行时刷新、历史与局部 reset 案例 |
| B3 数据与设备 | CPU/GPU、张量形状与所有权在哪里改变？ | Go2 状态与 adapter、PPO storage 拷贝 | 实际设备驻留、传输与同步开销测量 |
| B4 Runner 与算法 | rollout 怎样进入 return/advantage/loss？ | [固定 RSL-RL 5.5.1 的 PPO 路径](../learning/ppo-data-path.md) 与标量 GAE 示例 | Torch 原生更新与 checkpoint 读回 |
| B5 性能与扩展 | 开销在采样、物理、传输还是更新？ | 待写 | 从源码提出可检验假设；实测另有授权与协议 |

## 首次阅读顺序

1. [共同基础](../foundations/README.md)：用时间、单位、状态与回合边界描述一个任务。
2. [mjlab 导读](../mjlab/README.md) → [源码地图](../mjlab/source-map.md) → [G1 首课](../mjlab/01-g1-task.md)。
3. [G1 观测与动作](../mjlab/02-observations-actions.md) → [随机化与课程](../mjlab/03-randomization-curriculum.md) → [PPO](../learning/ppo-data-path.md)。
4. [Isaac Lab 导读](../isaaclab/README.md) → [Cartpole 首课](../isaaclab/01-native-task.md)：对照 Manager 与 Direct 工作流。
5. [UniLab 导读](../unilab/README.md) → [Go2 首课](../unilab/01-native-task.md)：追踪配置、后端和 learner。
6. [生命周期对照](../comparisons/lifecycle.md)：解释哪些语义可对应、哪些必须重新检查。

物理先修按需阅读 [Sim Atlas 共同基础](https://github.com/huangkiki/sim-atlas/blob/main/docs/foundations.md)。无需先学完六个引擎。
