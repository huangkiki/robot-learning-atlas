# 首期验证记录

[首页](../README.md) · [源码清单](sources.json) · [任务管理](project.md)

日期：2026-10-09。范围：E0 导读与共同基础、E1 mjlab G1 首课。检查由同一执行者完成，没有独立 reviewer 审批声明。

## 已执行

| 检查 | 结果 | 能证明什么 |
|---|---|---|
| 本地 Markdown 链接与固定源码行号检查 | 通过 | 目标存在，引用的 commit/path/行号纳入 manifest |
| 三个源码仓 Git blob SHA-256 与行数核对 | 38 个文件通过 | 对应固定提交的已读文件与记录一致 |
| Python 语法检查 | 通过 | 本仓三个 Python 脚本可解析 |
| G1 静态核对，4096 环境假设 | 50 Hz、1000 步、98,304 转移 | 所选固定源码的时间与采样配置推导 |
| G1 静态核对，64 环境假设 | 1,536 转移 | 环境数参数影响批量计算 |
| 非正环境数 | 正确拒绝，exit 2 | 输入检查有效 |
| 源码 HEAD 与 pin 不同 | 正确拒绝，exit 1 | 不把不同版本当作本课快照 |
| Markdown 缺失目标检查 | 检测出尚未生成的 evidence 文件；生成后通过 | 本轮实际观察到检查器能发现缺失文件 |

记录：[G1 静态输出](evidence/mjlab-g1-static.json)、[示例检查](evidence/example-checks.json)、[脚本身份](evidence/script-identities.json)。语法与源码检查分别执行，不把 Git blob 核对当作原生模块 import 通过。

复核命令，在本仓根目录执行；三个上游源码目录按实际位置替换：

```bash
python3 scripts/check_docs.py
python3 scripts/verify_sources.py --mjlab ../../work/mjlab --isaaclab ../../work/IsaacLab --unilab ../../work/UniLab
python3 mjlab/examples/inspect_g1.py --source ../../work/mjlab --num-envs 4096
python3 -m compileall -q scripts mjlab/examples
git diff --cached --check
```

Git 工作树中的未提交上游修改不会参与源码核对，因为工具读取提交对象。本课运行结果绑定 sources.json 中的固定提交与本仓保存的脚本摘要。

## 人工复核与修正

- G1 默认场景只有 1 个环境；4096 是示例命令覆盖值。
- G1 时间配置来自基础工厂，机器人/flat 覆盖没有修改该组时间参数。
- mjlab 默认返回重置后观测，reward/termination 与额外 forward 的时刻分别解释。
- mjlab 启用 FlagConversionOff，布尔覆盖使用值参数，不使用 no-flag 风格。
- Isaac Lab 当前训练入口已迁移到 isaaclab_rl/entrypoints/backends/train_rsl_rl.py；没有沿用旧 scripts 路径。
- UniLab 当前公共生命周期返回 TorchEnvState，不能套用旧 NumPy 介绍或直接假定五元组。
- play 配置与训练任务的评估条件分开标注，短训练不作为策略质量证明。

## 发布验证

远端当前提交的自动检查见 [Course checks](https://github.com/huangkiki/robot-learning-atlas/actions/workflows/docs.yml)。GitHub CI 只执行本仓链接、语法和 diff 检查，不下载三个上游仓，也不跑仿真。Issue 的交付记录保留实际 head 与该次 CI 结果。

## 未执行范围

没有安装或启动三框架的原生仿真环境，没有进行 GPU 训练、性能测量、独立策略评估或实机部署。首课原生命令已经按固定源码核对字段，实际 CLI 解析、依赖安装与运行留到 E5。纯 Python 配置脚本不能替代这些验证。
