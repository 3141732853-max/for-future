---
name: chainwright
description: "Help creators reduce mistakes in code, interfaces, documents, and multi-step work. Use for uncertain assumptions, cross-file changes, repeated failed fixes, performance/concurrency claims, visual reviews, or an explicit Chainwright check. Scale verification to the task: lightweight for small edits, experiment-first for exploration, evidence checkpoints for consequential work."
license: MIT
metadata:
  author: "3141732853-max"
  version: "0.2.0"
  runtime: "Optional checkers need Python 3.10+; standard library only; no network."
---

# Chainwright

Help creators catch mistakes before they become rework. Preserve the creator's intent and momentum; choose the smallest useful check, then deepen it when evidence or risk calls for more. Reply in the user's language. Record observable commitments, evidence and uncertainty, never private chain-of-thought or a claimed transcript of internal reasoning.

<!-- minimal:start -->
Use Chainwright to help creators reduce mistakes with proportionate checks. For a small reversible edit, do the work and verify its result without a ledger. For exploration, state one hypothesis and a bounded experiment; capture what happened before committing to a design. Reuse existing requirements and tests instead of rewriting them. For consequential work, declare checkable steps and dependencies, audit premises, review relevant code/performance/concurrency/visual/content risks, and choose bounded recovery when evidence fails. Report actual results and remaining conditions; never claim unrun checks passed, expose private chain-of-thought, or expand authorization. Use structured state and scripts only when they add value.
<!-- minimal:end -->

## Choose the working mode

| Situation | Mode | Minimum useful record |
| --- | --- | --- |
| Small reversible edit; known inputs and narrow effects | **Quick** | Result plus one relevant verification; no JSON, mandatory plan, or new test framework |
| Uncertain direction, prototype, creative variants | **Explore** | One hypothesis, a small reversible experiment, an observation, then keep/change/discard |
| Multiple dependent changes, unresolved assumptions, delivery to others | **Standard** | Short checkable steps, relevant premise checks, evidence for acceptance |
| Expensive failure, production behavior, repeated defects, explicit audit | **Deep** | Persistent evidence, reproducible counterexamples, baseline/regression checks and applicable review profiles |

Select a mode without asking a routine permission question. Existing authorization still governs execution and publication. A short script that deletes data can need Deep mode; line count alone is not risk. Do not create scaffolding whose cost outweighs the change. Escalate Quick/Explore when an experiment crosses a consequential boundary, changes an interface, or exposes repeated failures. Exploration does not relax permission or data boundaries. Before delivery, convert a retained experiment into acceptance checks.

## 1. Establish checkable anchors

In Standard/Deep mode, declare steps with inputs/premises, earlier dependencies, expected output and an observable check. Reuse requirement IDs, design specs, acceptance tests and project conventions **by reference**; add only gaps, conflicts and changed assumptions. Never duplicate a stable specification into a second contract.

Keep only the state needed for the task. A short table or existing issue checklist usually suffices. For machine-checked work, read [state-format.md](references/state-format.md) and adapt [state.example.json](assets/state.example.json). A script validates structure, not whether the output actually matches its expected meaning. If an output misses its acceptance check, mark it failed and reopen dependent work before consuming it.

## 2. Audit consequential premises

Label provenance `given`, `inferred`, or `assumed`; record `verified`, `unverified`, or `refuted` separately. Given does not mean independently true. Check assumptions that change implementation, facts, compatibility, safety or the conclusion. Inspect actual installed APIs and versions before adding dependencies; a package name existing does not establish trust.

When a premise changes, reopen affected results. Verify a material unknown using available evidence, or retain it as an explicit condition in the conclusion. If missing information or approval blocks a consequential action, stop that dependent action and continue independent work. Do not invent confidence percentages or evidence.

## 3. Select review profiles

Activate only relevant profiles. Read [review-profiles.md](references/review-profiles.md) for evidence and recovery guidance. Profiles are review workflows; they do not install or execute specialist tools automatically.

| Profile | Select when | Evidence focus |
| --- | --- | --- |
| `code` | Code behavior changes | `control_flow`, `data_dependencies`, `boundaries`, `intent_alignment` |
| `debug` | A defect is deep, intermittent or survives local fixes | `semantic_validity`: reproducible failure, invariant, causal explanation and regression check |
| `performance` | Speed, capacity, memory or responsiveness is a requirement/claim | `performance`: representative workload, baseline, units, tail behavior, resource/error budget |
| `concurrency` | Shared state, retries, cancellation or parallel work affect correctness | `concurrency`: interleavings, invariants, duplicate effects, ordering and cleanup |
| `visual` | Visual layout or interactive experience changes | `visual_quality`, `interaction_accessibility`: rendered artifacts, states/viewports, actual interactions |
| `content` | Factual copy, documents, calculations or published claims | `factual_integrity`: primary sources, dates, units, consistency and intended audience |

For changed code, mentally cover the four base dimensions even in Quick mode; a formal four-row record is unnecessary for a small edit. `control_flow` covers branch/error/cleanup paths; `data_dependencies` covers types, units, ownership and real callers; `boundaries` covers relevant empty/invalid/limit cases; `intent_alignment` compares original requirements and preserved behavior against the actual diff. Preserve protections and tests; a green check alone does not establish a generalized fix.

For deep bugs, prefer reproductions, traces, property/invariant tests or differential checks over repeated rereading. For performance, measure before optimizing. For UI, inspect the rendered result and exercise the main flow; source inspection cannot substitute for seeing it. Separate observable visual defects from subjective taste. If tools are unavailable, mark the corresponding check `not_run`; give a provisional result with explicit conditions rather than claiming it passed.

Use existing project tools first. Add only meaningful tests for risks not already covered; do not mirror the implementation or build a test framework for a harmless one-off. The optional read-only scripts need Python 3.10+:

```text
python <skill-dir>/scripts/audit_state.py state.json
python <skill-dir>/scripts/check_python.py changed.py
python <skill-dir>/scripts/review_diff.py change.diff --scope scope.json
```

They never execute target code. Exit 0 means no findings within limited coverage; 1 means findings; 2 means input/tool failure. [review-guide.md](references/review-guide.md) documents limits. The AST checker is narrow Python triage, not a deep semantic, race, performance or UI analyzer. The diff checker identifies review candidates, not proven unintended behavior. Use native tools and creator judgment where needed.

## 4. Recover using new evidence

| Failure | Action | Resume condition |
| --- | --- | --- |
| Contract too broad or output mismatch | `decompose` | Smaller checkable outputs |
| Missing or contradicted premise | `verify_premise` | New evidence; dependent results reopened |
| Premise or required check cannot be verified | `conditionalize` | Explicit limitation retained in affected results and conclusion |
| Reproduced local defect | `repair` | Targeted check demonstrates the fix |
| Multiple dimensions repeatedly fail, or an experiment rejects the design | `redesign` | Revised design/hypothesis and acceptance checks |
| Permission/data/tool blocker or exhausted budget | `stop` | Report the blocker and required input |

Default to at most two local repairs of the same failure before one redesign or a stop. This is an adjustable cost limit, not a researched optimum. Compare failure signatures and evidence; don't rename the same failed step just to reset a budget. Rerun checks affected by the change. Never weaken a test or protection solely to turn a failure into success.

## Deliver a useful result

Lead with the outcome, then actual verification and material remaining conditions. Keep Quick results short. For Standard/Deep work, include evidence references and only recovery decisions that affect confidence or scope. Store real ledgers outside public artifacts. Research motivates these practices; no measured accuracy gain is claimed for this skill. [evidence.md](references/evidence.md) links primary sources; [protocol.zh-CN.md](references/protocol.zh-CN.md) is the Chinese reading companion. This SKILL.md is the canonical behavioral source for generated adapters.
