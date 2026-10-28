# Chainwright

[简体中文](README.zh-CN.md) · [Skill](skills/chainwright/SKILL.md) · [Research](docs/RESEARCH.md)

**Help creators reduce mistakes without slowing every task down.**

Chainwright is an Agent Skill that adds proportionate verification to AI-assisted work: code, interfaces, documents and multi-step projects. It checks assumptions, compares results with intent, and changes course when evidence fails.

**0.2.0** · MIT · Optional scripts: Python 3.10+ · No third-party runtime dependencies

## Use the lightest useful workflow

| Mode | Best for | What happens |
| --- | --- | --- |
| Quick | Small reversible edits, controlled one-off scripts | Do the work and verify its result; no formal ledger |
| Explore | Prototypes, uncertain direction, creative experiments | Try a bounded experiment, inspect the result, then keep/change/discard |
| Standard | Dependent changes and delivery work | Use concise acceptance checks and verify consequential assumptions |
| Deep | Costly failure, recurring defects, explicit audits | Reproduce failures, compare baselines and retain evidence |

Existing requirements, tests and design systems are reused by reference. Chainwright records gaps and changes instead of copying a stable specification.

## Check the risks that matter

- **Code:** control flow, data dependencies, boundaries and intent alignment.
- **Deep bugs:** reproduction, violated invariants, causal evidence and regression checks.
- **Performance:** representative workloads, baseline comparisons, capacity, tail latency, resource and error budgets.
- **Concurrency:** shared state, interleavings, retries, idempotency, cancellation and cleanup.
- **Visual and interaction quality:** actual rendered output, layout states, main flows, keyboard/focus and accessibility.
- **Content:** factual sources, dates, calculations, units and consistency.

These profiles guide real checks with available tools. The bundled Python AST checker remains deliberately narrow; it does not automatically diagnose deep bugs, optimize performance or judge visual quality. Subjective design decisions stay with the creator.

## Install

Copy the complete `skills/chainwright` folder into one supported location:

| Host | Project location | Personal location |
| --- | --- | --- |
| DeepSeek Harness (DSH) | `.dsh/skills/chainwright` | `~/.dsh/skills/chainwright` |
| Codex | `.agents/skills/chainwright` | `~/.agents/skills/chainwright` |
| Claude Code | `.claude/skills/chainwright` | `~/.claude/skills/chainwright` |

The final path must end in `chainwright/SKILL.md`; keep its scripts and references alongside it. Install inside the environment where the assistant runs. ChatGPT with native skills can load the bundle where supported. For a prompt-only host, use `adapters/minimal.txt` and supply the full instructions on demand.

[Installation and host requirements](docs/ADAPTERS.md) · [中文协议](skills/chainwright/references/protocol.zh-CN.md)

Example requests:

> Use Chainwright to check this change. Keep verification proportionate and preserve existing behavior.

> Use Chainwright in Explore mode. Try a small prototype first, then check the result before choosing a design.

> Review this interface with Chainwright. Inspect its rendered states and main interactions; distinguish defects from stylistic suggestions.

## Optional local checkers

Use existing project tooling first. A formal ledger and these scripts are optional.

```sh
python skills/chainwright/scripts/audit_state.py skills/chainwright/assets/state.example.json
python skills/chainwright/scripts/check_python.py path/to/changed.py
python skills/chainwright/scripts/review_diff.py change.diff --scope scope.json
```

| Checker | Coverage |
| --- | --- |
| State audit | Dependencies/cycles, evidence presence, premise conditions, selected review profiles and recovery budgets |
| Python AST | Direct unreachable statements, simple unused bindings, literal zero/index errors and boundary review candidates |
| Diff review | File scope, removed checks, skipped tests and dependency/configuration changes |

The scripts read inputs without executing target code. Exit **0**: no findings within coverage; **1**: findings to review; **2**: invalid input/tool failure. A zero result does not prove correctness. State v2 supports profile-specific checks and explicit `not_run` conditions; v1 remains readable. [State format](skills/chainwright/references/state-format.md).

## Evidence and limits

[23 primary sources](docs/RESEARCH.md) motivate the failure modes and verification practices. Sources retain dates, scope, numerical denominators and limitations. No measured error-reduction or productivity claim is made for Chainwright. It records observable evidence, not private chain-of-thought.

Checks that cannot be performed are reported as not run. The protocol cannot verify fabricated evidence, guarantee semantic correctness, prove race freedom or replace a creator's judgment.

## Development

```sh
python -m unittest discover -s tests -v
python tools/validate_repo.py
python tools/package_release.py
```

Packaging produces skill/source ZIPs and SHA-256 checksums in `dist/`. [Evaluation](docs/EVALUATION.md) · [Verification](docs/VERIFICATION.md) · [Releasing](docs/PUBLISHING.md) · [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

Copyright © 2026 [3141732853-max](https://github.com/3141732853-max). [MIT License](LICENSE).
