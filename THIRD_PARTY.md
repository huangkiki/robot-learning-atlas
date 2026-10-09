# 来源与许可

原创课程正文、比较说明和检查脚本采用 [Apache-2.0](LICENSE)。课程组织参考 [Sim Atlas](https://github.com/huangkiki/sim-atlas) 的双路线与证据分级，具体课程围绕机器人学习框架重新编写。

| 上游 | 固定提交 | 使用方式 |
|---|---|---|
| mjlab | `033ae22a2c7a30a25a6fa77b16c113ed88dd1b55` | 原生符号、配置值与源码链接 |
| Isaac Lab | `07daf4426dfa8dcb6d0753768890b4f60dc54f9e` | 工作流和生命周期源码链接 |
| UniLab | `cbafb5071fb0ea2d7322e1b0b648f8819b2a7499` | 配置、后端与状态接口源码链接 |

上游代码、文档、模型与依赖保留原许可；本仓不打包它们，不使用官方 logo，也不宣称官方隶属。mjlab 与 UniLab 主仓许可为 Apache-2.0；Isaac Lab 仓内组件采用不同许可，应按所用文件核查。上游读取清单和文件摘要见 [sources.json](docs/sources.json)。

本仓短代码与命令用于解释原生接口；完整实现通过上游 permalink 阅读。未复制上游训练资产、checkpoint 或大段实现。

内容由 AI 辅助编写并由同一执行者依据固定源码自查；没有独立 reviewer 审批声明。执行证据与未验证项见 [验证记录](docs/validation.md)。
