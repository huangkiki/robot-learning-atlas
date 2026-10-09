# 参与课程维护

先看 [roadmap](docs/roadmap.md)，选择依赖已满足的一项；已有章节的修正在原章节完成。一个切片应能独立审阅和验收，不以空目录或标题数量计进度。

章节应包含：先修、学习目标、真实任务或问题、原生字段与调用链、固定源码链接、公式的单位与适用条件、易错点、练习和答案、验证范围。解释应能让读者沿链接复核。源码注释与行为不一致时，以调用和实现为依据，并保留差异。

三框架的配置、返回类型和重置方式不要求统一。共同基础可以复用概念；具体数值和默认行为回到固定源码。严禁把支持矩阵里的注册项写成已经验证的训练组合。

## 检查

```bash
python3 scripts/check_docs.py
python3 -m compileall -q scripts mjlab/examples
git diff --check
```

更新源码时，在提供三个固定提交源码仓的前提下运行：

```bash
python3 scripts/verify_sources.py --mjlab ../mjlab --isaaclab ../IsaacLab --unilab ../UniLab
python3 mjlab/examples/inspect_g1.py --source ../mjlab --num-envs 4096
```

`--source` 可以指向有未提交修改的阅读仓；核对工具读取指定提交的 Git blob，不读取未提交文件。输出只证明固定源码的内容，不能描述工作区安装包的行为。

添加检查脚本时优先标准库；对脚本进行正常路径和相关失败路径验证。人工复核源码含义、练习答案、中英文入口与实际内容。远程链接的 commit/path/行号能被源码对象核对，不代表运行或网页视觉验证。

原创内容采用 Apache-2.0。新增上游摘录、资产和图片必须说明来源与许可；优先链接源码，不打包上游代码与资产。只提交本次课程内容。
