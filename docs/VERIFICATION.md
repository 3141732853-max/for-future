# Verification / 验证

Chainwright validates its tools separately from claims about model effectiveness.

| Layer | Verification |
| --- | --- |
| State audit | Dependency order/cycles, premise evidence, final conditions, selected profiles, not-run handling, repair budgets and legacy v1 compatibility |
| Python checker | Narrow AST findings, adjacent non-failure cases, and no target-code execution |
| Diff checker | Scope, renamed files, Unicode paths, unsupported/malformed input and removed-check signals |
| Distribution | Skill metadata, source/adapter consistency, local reference links, source registry and ZIP contents/checksums |
| CI | Windows/Linux with Python 3.10/3.12 |
| Model effectiveness | Requires the paired study in [EVALUATION.md](EVALUATION.md); no improvement percentage is claimed |

Run `python -m unittest discover -s tests -v` and `python tools/validate_repo.py` for current results. Workflow results are available in the repository's Actions tab after CI completes. A successful structural check validates the reported fields, not the truth of the underlying evidence.

工具验证与模型效果评估分别进行。状态、AST、差异与打包都有自动检查；CI 覆盖 Windows/Linux、Python 3.10/3.12。实际通过状态以对应运行结果为准。模型效果需要独立对照评估，不能用脚本测试数量替代。
