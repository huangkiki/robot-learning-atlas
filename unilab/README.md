# UniLab：任务、后端与学习运行时的边界

[首页](../README.md) · [源码地图](source-map.md) · [生命周期对照](../comparisons/lifecycle.md)

**先修：** 共同基础和一种 manager-based 环境；了解 CPU/GPU 是不同执行与存储位置。

**目标：** 找到配置、任务构造、后端与 learner 的责任；识别公共返回结构。

**快照：** `cbafb5071fb0ea2d7322e1b0b648f8819b2a7499`，源码元数据 `1.3.3`。这里指当前 [Motphys/UniLab](https://github.com/Motphys/UniLab)，原 unilabsim/UniLab 地址会重定向到该仓。

## 沿着配置进入运行时

该版本通过 Hydra 组织任务和算法配置。一个具体例子是 `ppo/task/go2_joystick_flat/mujoco.yaml`：它继承基础任务配置，设置 `training.task_name=Go2JoystickFlat`、`training.sim_backend=mujoco`，并配置算法和环境规模。[Go2 + MuJoCo 配置](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/conf/ppo/task/go2_joystick_flat/mujoco.yaml)

由配置到执行的阅读顺序为：

```text
CLI → 训练入口/配置组合 → config_adapter → registry.make
    → 任务环境 + backend_factory → TorchEnv.step
    → 后端 step_tensor → 任务 update_state → learner 所需状态
```

`backend_factory` 把 UniLab 的配置和资产需求交给外部 `unisim` 工厂。任务配置与后端实现因此有明确接缝；具体能力需要查注册项、配置、接口协商和验证记录。来源：[后端装配职责](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/backend_factory.py#L1-L10)。

## 不要把旧版 NumPy 介绍当成当前公共接口

当前 `ManagerBasedRlEnv` 继承 `TorchEnv`。公共 actions、observations、reward、terminated、truncated 和 final observation 都围绕 Torch 张量组织。部分 manager/entity 内部仍涉及 host 边界，应继续读其实现，不能从公共张量类型推出“整个链路零拷贝”。来源：[当前环境类](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L353-L363)。

`TorchEnv.step` 返回一个 `TorchEnvState`，并不是可以直接按 Gym 五元组解包的对象。该结构包含 `obs/reward/terminated/truncated/info/final_observation`。[状态结构](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L45-L65)

## 仿真设备与学习设备是两个问题

CPU 仿真可以向加速器上的学习器提供样本，设备驻留后端也可能提供张量接口。具体路径要追踪后端执行类型、张量 device、状态读取、collector 进程和数据传输，而不只是看 `torch.cuda.is_available()`。

`env_factory` 提供可序列化的顶层构造入口，供 spawn collector 子进程重新建立 registry 与环境；它的职责是创建环境，不负责替代学习算法。[collector 环境工厂](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/env_factory.py#L26-L43)

## 时间与重置

环境的 `physics_dt` 来自 `sim_dt`，`step_dt` 来自 `ctrl_dt`；`sim_substeps` 在基础配置中由比例四舍五入得到。本期仅对照字段与实现，不假设所有后端都接受任意不整除的时钟组合。来源：[子步数计算](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/base.py#L147-L156)、[时间属性](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/envs/manager_based_rl_env.py#L952-L958)。

父类 `TorchEnv.step` 负责调用 `step_tensor(ctrl, sim_substeps)`、更新任务状态和处理自动重置。重置前把结束行观测写入 `final_observation`；读取时使用 `terminated | truncated` 选择有效行，不能把 scratch 缓冲中的所有行都当成本步终止观测。[自动重置与终止观测](https://github.com/Motphys/UniLab/blob/cbafb5071fb0ea2d7322e1b0b648f8819b2a7499/src/unilab/base/torch_env.py#L482-L529)

## 练习与答案

1. 后端出现在配置文件中，是否说明其所有机器人任务都训练成功？

   **答案：** 否。注册、配置、接口支持、执行和训练验证是不同证据。
2. 公共接口使用 Torch 张量，是否说明仿真全部运行在 GPU？

   **答案：** 否。还需读取 backend 的执行模式、数据边界与具体 device。
3. 迁移 mjlab 五元组调用代码时，第一处需要核对什么？

   **答案：** 返回的 `TorchEnvState` 结构和 adapter，随后核对自动重置与终止观测语义。

**本期状态：** 导读、配置样例和源码地图完成；完整跨后端任务课程、性能比较与原生运行未完成。
