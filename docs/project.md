# GitHub Project 与任务管理

[首页](../README.md) · [roadmap](roadmap.md)

看板：[Robot Learning Atlas · 机器人学习图谱](https://github.com/users/huangkiki/projects/3)。

仓库：[robot-learning-atlas](https://github.com/huangkiki/robot-learning-atlas)。

Project 管理队列与实际状态，Issue 保存范围、依赖和验收，提交及 CI 提供交付证据。开始、受阻和交付时回写并读回。

- [开发看板](https://github.com/users/huangkiki/projects/3/views/1)：首页视图，按 Status 分为 Todo、In Progress、Done；卡片显示 Framework、Track 和 Stage。
- [课程总表](https://github.com/users/huangkiki/projects/3/views/2)：集中查看标题、状态、框架、路线和 E0–E6 阶段，可按相应字段筛选。

Framework 使用蓝色 mjlab、绿色 Isaac Lab、橙色 UniLab、紫色 Cross-framework 和灰色 Shared。Track 区分共同基础、应用路线、原理与源码路线和双路线；阶段使用中性颜色，避免与进度混淆。每个阶段仍保留一个正式 Issue，路线字段描述该阶段的覆盖范围。

| 阶段 | Issue | 前置 |
|---|---|---|
| E0 | [#1 · E0 · 建立双路线、共同基础与三框架固定源码导读](https://github.com/huangkiki/robot-learning-atlas/issues/1) | 无 |
| E1 | [#2 · E1 · 讲解 mjlab G1 完整任务路径并提供静态核对示例](https://github.com/huangkiki/robot-learning-atlas/issues/2) | [E0 / #1](https://github.com/huangkiki/robot-learning-atlas/issues/1) |
| E2 | [#3 · E2 · 补齐 Isaac Lab 原生任务的纵向课程](https://github.com/huangkiki/robot-learning-atlas/issues/3) | [E0 / #1](https://github.com/huangkiki/robot-learning-atlas/issues/1)、[E1 / #2](https://github.com/huangkiki/robot-learning-atlas/issues/2) |
| E3 | [#4 · E3 · 补齐 UniLab 任务配置到后端和 learner 的纵向课程](https://github.com/huangkiki/robot-learning-atlas/issues/4) | [E0 / #1](https://github.com/huangkiki/robot-learning-atlas/issues/1)、[E1 / #2](https://github.com/huangkiki/robot-learning-atlas/issues/2) |
| E4 | [#5 · E4 · 深入动作观测、随机化课程与 PPO 数据路径](https://github.com/huangkiki/robot-learning-atlas/issues/5) | [E1 / #2](https://github.com/huangkiki/robot-learning-atlas/issues/2) |
| E5 | [#6 · E5 · 执行冻结配置下的原生运行与训练连通性验收](https://github.com/huangkiki/robot-learning-atlas/issues/6) | [E1 / #2](https://github.com/huangkiki/robot-learning-atlas/issues/2) |
| E6 | [#7 · E6 · 完成迁移、独立评估与全课程审校](https://github.com/huangkiki/robot-learning-atlas/issues/7) | [E2 / #3](https://github.com/huangkiki/robot-learning-atlas/issues/3)、[E3 / #4](https://github.com/huangkiki/robot-learning-atlas/issues/4)、[E4 / #5](https://github.com/huangkiki/robot-learning-atlas/issues/5)、[E5 / #6](https://github.com/huangkiki/robot-learning-atlas/issues/6) |

本轮课程范围为 E2/E3/E4，承接已有 E0/E1；用户明确将 E5 原生运行与短训练留到后续，E6 仍依赖 E5。任务只有在达到约定交付终点、核实远端提交和 CI 后才标 Done。当前状态以看板和 Issue 为准，本页不复制状态历史。

Project 与新课程仓初始可见性为私有。公开 Sim Atlas 继续作为物理引擎课程入口；本仓已链接到它。面向所有读者的反向入口需在本仓公开后接入，避免公开导航指向不可访问内容。

本次没有配置定时自动化，没有因创建 Project 自动启动原生训练。
