# Robot Learning Atlas · 机器人学习图谱

从一个训练任务出发，读懂机器人学习框架怎样组织仿真、观测、动作、奖励和策略。

[English](README.en.md) · [学习路线](docs/curriculum.md) · [共同基础](foundations/README.md) · [当前进度](docs/roadmap.md) · [GitHub Project](https://github.com/users/huangkiki/projects/3)

本系列面向已经接触 Python 和机器人仿真的读者，以 **mjlab → Isaac Lab → UniLab** 为建议阅读顺序。先沿一个真实任务走通配置、环境、训练和回放的源码，再对照其他框架的实现。课程按原生接口展开，保留每个框架的命名和约束。

## 从哪里开始

| 你想解决的问题 | 阅读入口 | 本期已有内容 |
|---|---|---|
| 模型、任务、算法各自负责什么？ | [共同基础](foundations/README.md) | 分层地图、时间与批量、终止与重置 |
| 一条 mjlab 训练命令究竟调用了什么？ | [mjlab](mjlab/README.md) | G1 任务、逐字段观测/动作、随机化与课程 |
| Isaac Lab 的 manager 和 direct 怎么选？ | [Isaac Lab](isaaclab/README.md) | Cartpole 注册、配置、step/reset、训练 API 与两种工作流对照 |
| 换后端时，哪些任务语义必须保持？ | [UniLab](unilab/README.md) | Go2 配置覆盖、后端构造、Torch 状态与 PPO adapter |
| rollout 怎样变成 PPO loss？ | [PPO 数据路径](learning/ppo-data-path.md) | 固定 RSL-RL 5.5.1、storage、timeout、GAE 与更新 |
| 三个框架的 step/reset 能否直接对换？ | [生命周期对照](comparisons/lifecycle.md) | 时间、返回结构、自动重置与终止观测 |

**现在开始：** 阅读 [mjlab 首课](mjlab/01-g1-task.md)，再用附带的 [源码核对脚本](mjlab/examples/inspect_g1.py) 验算 50 Hz、1000 步和每轮采样数。脚本仅需 Python 3.10+ 与固定提交的 Git 源码，不导入框架、不启动 GPU。

## 两条学习路线

- **A · 使用框架**：对象与安装 → 原生任务 → 观测与动作 → 奖励与终止 → 训练评估 → 随机化与课程 → 策略迁移。
- **B · 理解实现**：配置装配 → step/reset → manager 依赖 → 数据与设备 → runner/算法接口 → 性能与扩展。

[课程目录](docs/curriculum.md) 对每个单元标明已有章节与剩余内容；目录完整不代表课程已经写完。已有 E0–E4：导航与基础、三框架原生任务，以及 mjlab 观测/动作、随机化/课程和固定算法版本的 PPO 专题。E5 原生运行与短训练按本轮约定留到后续；E6 迁移、独立评估和最终审校仍待推进。

## 与 Sim Atlas 的衔接

[Sim Atlas](https://github.com/huangkiki/sim-atlas) 讲物理引擎的模型、状态、控制、接触与求解。本仓从这些接口向上讲任务和学习流程：

```text
物理引擎与原生接口         → 任务、观测、奖励与重置 → rollout、算法更新与评估
Sim Atlas                  Robot Learning Atlas
```

阅读中遇到质量、惯量、接触力或积分器问题，回到对应引擎课程；遇到观测时刻、动作缩放、采样和重置问题，沿本仓课程继续。首期三个框架共用一个课程仓，各自保留独立章节和固定版本。

## 来源与验证

源码固定于 2026-10-09 的阅读快照，完整提交和文件摘要见 [sources.json](docs/sources.json)。[验证记录](docs/validation.md) 区分源码核对、课程脚本执行、原生仿真、训练、评估和实机验证。当前完成前两类；原生训练命令是待执行的操作说明，未报告训练效果或速度。

维护检查：

```bash
python3 scripts/check_docs.py
python3 learning/examples/rollout_math.py
python3 -m compileall -q scripts mjlab/examples learning/examples
git diff --check
```

独立社区课程，与所述项目无隶属关系。原创正文和脚本采用 [Apache-2.0](LICENSE)，上游代码及资产遵循各自许可，见 [来源说明](THIRD_PARTY.md)。
