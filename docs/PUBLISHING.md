# Releasing Chainwright / 发布流程

## Validation

```sh
python tools/build_research.py
python skills/chainwright/scripts/export_adapters.py --out adapters
python -m unittest discover -s tests -v
python tools/validate_repo.py
python tools/package_release.py
```

Keep VERSION and skill metadata synchronized. Review the English and Chinese introductions, protocol companion and source registry. Generated adapters must match the canonical SKILL.md.

## Artifacts

The package builder creates `chainwright-<version>-skill.zip`, `chainwright-<version>-source.zip`, and `SHA256SUMS.txt` in `dist/`. It uses an allowlist and rejects symlinks. Inspect both contents and checksums; exclude credentials, personal paths, real task ledgers and private project data.

Publish source files at the repository root and attach distribution archives to a release when the release channel is available. CI should validate tests, generated artifacts and package creation. Record verification claims only after the associated checks finish.

## Repository description

English: **Help creators reduce mistakes with adaptive checks for code, interfaces, content, and complex AI-assisted work.**

中文：**通过适量的代码、界面、内容与复杂任务检查，帮助创作者减少错误。**

Suggested topics: `agent-skills`, `ai-assisted-creation`, `code-review`, `verification`, `developer-tools`.

## 中文发布要点

同步版本、中英文说明与生成文件，运行测试后核对源码包、技能包和校验和。公开材料只描述产品能力、使用方式和验证证据；不包含私人任务记录或工作环境信息。代码检查通过不等于模型效果提升。
