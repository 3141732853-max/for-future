# Chainwright

[English](README.md) · [Skill 入口](skills/chainwright/SKILL.md) · [研究资料](docs/RESEARCH.zh-CN.md)

**帮助创作者减少错误，同时保留创作节奏。**

Chainwright 是一个 Agent Skill，为 AI 辅助的代码、界面、文档和多步骤创作加入适量检查：核实关键前提，比较产出与目标，在证据不成立时调整方向。

**0.2.0** · MIT · 可选脚本需要 Python 3.10+ · 无第三方运行依赖

## 按任务选择检查强度

| 模式 | 适用场景 | 工作方式 |
| --- | --- | --- |
| Quick 轻量 | 可逆的小改动、输入可控的一次性工具 | 直接完成并核对结果，无需正式记录表 |
| Explore 探索 | 原型、方向未定、创意试验 | 先做小实验，观察结果，再保留、调整或放弃 |
| Standard 常规 | 有依赖的修改与交付任务 | 简短验收步骤，核实关键前提 |
| Deep 深入 | 失败成本高、反复缺陷、明确审计 | 复现问题，比较基线，保留证据 |

已有需求、测试与设计规范直接引用，只记录缺口和变化，不重新抄写一份契约。

## 只检查相关风险

- **代码**：控制流、数据依赖、边界条件与意图对齐。
- **深层缺陷**：最小复现、不变量、因果证据与回归检查。
- **性能**：真实负载、基线、容量、尾延迟、资源与错误预算。
- **并发**：共享状态、交错执行、重试、幂等、取消与清理。
- **视觉交互**：真实渲染、布局状态、主流程、键盘焦点与可访问性。
- **内容**：事实来源、日期、计算、单位与前后一致性。

这些专项指导助手使用实际工具完成检查。附带的 Python AST 脚本仍是有限静态提示，不会自动诊断所有深层 bug、调优性能或评价视觉品质。审美取舍由创作者决定。

## 安装

把完整的 `skills/chainwright` 文件夹复制到以下任一对应位置：

| 宿主 | 项目级位置 | 个人位置 |
| --- | --- | --- |
| DeepSeek Harness（DSH） | `.dsh/skills/chainwright` | `~/.dsh/skills/chainwright` |
| Codex | `.agents/skills/chainwright` | `~/.agents/skills/chainwright` |
| Claude Code | `.claude/skills/chainwright` | `~/.claude/skills/chainwright` |

最终路径应以 `chainwright/SKILL.md` 结束，保留旁边的脚本和参考资料。安装到助手实际运行的环境中。支持原生技能的 ChatGPT 可使用原生入口；纯提示词宿主使用 `adapters/minimal.txt`，按需提供完整协议。

[安装与环境要求](docs/ADAPTERS.md) · [完整中文协议](skills/chainwright/references/protocol.zh-CN.md)

使用示例：

> 使用 Chainwright 检查这个修改，按风险决定检查强度，并保留原有行为。

> 使用 Chainwright 的探索模式，先做一个小原型，再根据运行结果决定设计。

> 使用 Chainwright 审查这个界面，查看真实渲染和主要交互，区分实际缺陷与风格建议。

## 可选本地检查器

优先使用项目已有工具；正式状态记录与以下脚本均按需使用：

```sh
python skills/chainwright/scripts/audit_state.py skills/chainwright/assets/state.example.json
python skills/chainwright/scripts/check_python.py path/to/changed.py
python skills/chainwright/scripts/review_diff.py change.diff --scope scope.json
```

| 检查器 | 覆盖范围 |
| --- | --- |
| 状态校验 | 依赖与闭环、证据是否填写、前提条件、选中的专项检查、恢复预算 |
| Python AST | 直接不可达语句、简单未读绑定、字面零除/越界与边界提示 |
| 差异审查 | 文件范围、删除检查、跳过测试、依赖与配置变动 |

脚本只读，不执行目标代码。退出码 **0**：有限范围内无发现；**1**：需审查的发现；**2**：输入或工具错误。无发现不等于正确性证明。状态 v2 支持专项检查与 `not_run` 条件，仍可读取 v1。[状态格式](skills/chainwright/references/state-format.md)。

## 研究依据与边界

[23 项一手来源](docs/RESEARCH.zh-CN.md) 支持失误类型与检查方法的选择，保留年份、范围、数据分母和局限。项目不宣称经过测量的准确率或效率提升；记录的是可观察证据，不是模型内部思维链。

无法执行的检查必须标注未运行。协议不能识别所有虚构证据、保证语义正确、证明没有竞态，也不能替代创作者判断。

## 开发与验证

```sh
python -m unittest discover -s tests -v
python tools/validate_repo.py
python tools/package_release.py
```

打包生成 skill、源码 ZIP 以及 SHA-256 清单，位于 `dist/`。[评估方案](docs/EVALUATION.md) · [验证记录](docs/VERIFICATION.md) · [发布流程](docs/PUBLISHING.md) · [贡献](CONTRIBUTING.md) · [安全](SECURITY.md)

Copyright © 2026 [3141732853-max](https://github.com/3141732853-max)。[MIT 许可证](LICENSE)。
