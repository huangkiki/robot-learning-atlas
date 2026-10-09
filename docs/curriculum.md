# 双路线课程目录

[首页](../README.md) · [当前任务](roadmap.md) · [共同基础](../foundations/README.md)

先沿 mjlab 的真实任务建立完整对象地图，再把同一问题带到 Isaac Lab 和 UniLab。已有链接表示本期有可读内容；“部分覆盖”表示仍有内容待写，不表示整个单元完成。

## A · 使用框架

| 单元 | 学习目标 | 本期内容 | 后续验收 |
|---|---|---|---|
| A0 对象与环境 | 分清安装包、任务、物理后端和算法 | 三框架导读，部分覆盖 | 各框架安装/版本检查与首个原生运行记录 |
| A1 定义任务 | 找到场景、机器人、配置与注册入口 | [mjlab 首课](../mjlab/01-g1-task.md)，部分覆盖 | 一个最小任务修改及配置前后对照 |
| A2 观测与动作 | 解释维度、单位、噪声、历史、缩放与控制目标 | 首课动作/观测与 [基础](../foundations/README.md)，部分覆盖 | 逐字段维度表及选定机器人映射 |
| A3 奖励与终止 | 区分每步奖励、时间缩放、失败、截断和重置 | 首课与 [生命周期对照](../comparisons/lifecycle.md)，部分覆盖 | 固定协议下的边界案例 |
| A4 训练与评估 | 连接 rollout、runner、checkpoint 和策略回放 | 首课源码路径，部分覆盖 | 原生运行、独立评估和可复核产物 |
| A5 随机化与课程 | 区分 startup/reset/interval 与难度调度 | 首课说明配置位置，专题待写 | 一项随机化与一项课程的触发/状态追踪 |
| A6 策略迁移 | 核对观测、控制、归一化、频率和后端差异 | 待写 | 迁移检查表与实际验证范围 |

## B · 理解实现

| 单元 | 源码问题 | 本期内容 | 后续验收 |
|---|---|---|---|
| B0 配置装配 | 配置何时解析、实例化、覆盖和复制？ | 三框架源码地图与 mjlab 首课 | 补齐另两框架配置展开实例 |
| B1 step/reset | 谁推进物理、刷新派生量、生成观测和重置？ | mjlab 首课与三框架对照 | 两个其他框架的完整纵向课程 |
| B2 Manager 依赖 | 观测、命令、事件之间为什么有执行顺序？ | mjlab 首课，部分覆盖 | 逐 manager 的状态与依赖图 |
| B3 数据与设备 | CPU/GPU、张量形状与所有权在哪里改变？ | UniLab 导读，部分覆盖 | 固定组合的数据边界与同步点追踪 |
| B4 Runner 与算法 | rollout 怎样进入 return/advantage/loss？ | 当前到 runner.learn 接口，算法内部待写 | 固定算法依赖版本后的 PPO 数据路径 |
| B5 性能与扩展 | 开销在采样、物理、传输还是更新？ | 待写 | 从源码提出可检验假设；实测另有授权与协议 |

## 首次阅读顺序

1. [共同基础](../foundations/README.md)：用时间、单位、状态与回合边界描述一个任务。
2. [mjlab 导读](../mjlab/README.md) → [源码地图](../mjlab/source-map.md) → [G1 首课](../mjlab/01-g1-task.md)。
3. [Isaac Lab 导读](../isaaclab/README.md)：把 manager 经验与 Direct 工作流对照。
4. [UniLab 导读](../unilab/README.md)：追踪任务配置与后端/学习运行时的接口。
5. [生命周期对照](../comparisons/lifecycle.md)：解释哪些语义可对应、哪些必须重新检查。

物理先修按需阅读 [Sim Atlas 共同基础](https://github.com/huangkiki/sim-atlas/blob/main/docs/foundations.md)。无需先学完六个引擎。
