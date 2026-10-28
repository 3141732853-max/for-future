# Contributing / 贡献指南

Keep behavioral rules in `skills/chainwright/SKILL.md`, and synchronize the Chinese reading companion when behavior changes. Keep the skill concise; put conditional detail in references. Changes must preserve user intent, scope and authorization. Never require private chain-of-thought or claim a passing structural check proves correctness.

For checker changes, add a real failure case and a nearby non-failure case. Keep scripts standard-library-only, bounded and read-only with respect to targets. Record unsupported syntax rather than silently reporting success. Source additions need a primary URL, inspected section, date/version, denominator for numbers, and explicit limitations; do not paste copyrighted papers or secret code.

```sh
python tools/build_research.py
python skills/chainwright/scripts/export_adapters.py --out adapters
python -m unittest discover -s tests -v
python tools/validate_repo.py
```

行为规则只维护在 SKILL.md，修改时同步中文说明与生成的适配文件。检查器修改要有错误样例和相邻的正常样例；资料必须有一手链接、位置、分母和局限。未经对照测量，不要声称提升准确率。不要提交个人任务状态、密钥、私有仓库内容或评估对话日志。
