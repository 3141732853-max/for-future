# Choosing checks from observed failure modes

Read the user's acceptance criteria first. For each changed behavior identify at least one positive example and a relevant counterexample; use existing tests when they already cover this. Keep an unchanged behavior as a regression anchor. Don't replace a specified implementation just to fit this checklist.

Apply this proportionately. A small reversible change can use one existing check with no persistent record. In Explore mode, test the immediate hypothesis first; formalize acceptance only when retaining the result. Reuse stable specs and toolchains. For deep defects, performance, concurrency, visual/interaction or content checks, consult only the applicable section of [review-profiles.md](review-profiles.md).

| Failure | Check to choose | What automation cannot establish |
| --- | --- | --- |
| Nonexistent package / invented API | Installed manifest, actual definition, official versioned documentation; registry verification only when needed | An existing name can still be malicious or incompatible |
| Cross-file mismatch | Read callers and data schema; integration/type check | A local AST walk cannot see all runtime dependencies |
| Happy-path-only implementation | Empty, absent, invalid, maximum-size and failure cases relevant to the contract | No guard syntax does not prove a missing boundary check |
| Swallowed failure / unreachable operation | Error-path tests and cleanup behavior | Dynamic dispatch, exception and async control flow need deeper tools |
| Race / duplicate side effect | Concurrent request, retry and idempotency tests where relevant | A sequential passing test says nothing about races |
| Test overfitting | Fresh inputs, original assertions/protections preserved, tests separate from implementation | Changing a test can be legitimate; investigate rather than condemn |
| Scope drift | Declared file scope plus semantic diff review | File allowlists do not detect all unintended behavior |
| Confident unsupported claim | Open the cited source / run the named check | A well-formed ledger may contain fabricated evidence |
| Repeated ineffective patch | Record failure signature and new evidence; redesign after budget | More self-critique is not inherently better |

`check_python.py` reports direct unreachable statements after terminal statements, unused local bindings in simple functions, literal zero division, literal out-of-range list/tuple indexing, and a candidate-risk notice for variable indexing at 0/-1. It intentionally skips unused-variable analysis for nested functions/classes, comprehensions, lambdas, dynamic locals access, and global/nonlocal scopes. It does not build a complete control-flow graph, infer types, verify branch coverage, perform taint analysis, detect all unused imports, or inspect JS/TS. Candidate risks are not definite bugs; a guard or contract may justify them.

`review_diff.py` highlights out-of-scope paths, removed assertion/check/raise lines, added skip/xfail markers, test changes, and dependency/configuration changes. These are review prompts, not conclusions about intention. To collect a tracked diff you may use `git diff --no-ext-diff --no-textconv --binary BASE --` and save it with a UTF-8-capable mechanism. Include untracked files separately or stage only authorized changes before collecting; an empty tracked diff does not mean an empty working tree. Binary patches are deliberately rejected for manual review.

Run repository tests only if their execution is authorized. Preserve command, relevant environment/version, exit status, and concise result in the ledger. For unavailable tools record not run, then use a conditional/blocked conclusion instead of fabricated evidence.
