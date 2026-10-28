# Evaluation plan / 评估方案

## What has and has not been measured

Local unit/integration tests exercise deterministic checkers, input rejection, source/adapter consistency and packaging. They do not measure a model's behavior or establish Chainwright's efficacy. Claude, ChatGPT and DSH live-host runs have not been performed. Do not publish efficacy percentages derived from these tests.

本地测试验证确定性工具，不等于模型行为评估；未进行 Claude、ChatGPT、DSH 的真实宿主验收，不能据此宣传提升百分比。

## Paired study before claiming benefits

Use the same pinned repository revision, task, model version, tool permissions, context, token/time budget, and acceptance tests in baseline and Chainwright conditions. Randomize ordering; run independent sessions and repeated trials. Keep hidden acceptance checks separate from artifacts available to the agent. Include a generic checklist baseline to distinguish the protocol from simply spending more tokens. Pre-register selection rules and failure definitions; retain all runs, including failures. Do not tune on held-out tasks.

Record task success against original requirements, regressions, fabricated evidence, unresolved assumptions disclosed, false alarms, unnecessary stops, tool/runtime cost, elapsed time and human review effort. Report denominators, per-task outcomes, uncertainty intervals and failures. Do not pool incomparable model versions. Compare successful outcomes and overhead together. A reviewer blind to the condition should adjudicate intent alignment; resolve disagreements using the original contract and executable examples.

对照实验应固定仓库、任务、模型、权限与预算，随机化顺序并重复运行；保留独立验收测试和全部失败样本。加入普通检查清单基线，避免把增加推理成本误认成协议优势。同时测量成功率、回归、虚构证据、误报、停止次数、耗时和人工审查成本，并给出分母与不确定性。

## Synthetic task pack

`eval/scenarios.json` contains original, synthetic prompts and scoring criteria, not copied incidents or published benchmark tasks. Use isolated disposable repositories, never production. These scenarios are behavioral evaluation inputs, **not executed model results**. Do not show scoring criteria to the evaluated model.

For each case, store model/version, date, prompt variant, environment, actual tool logs, final artifacts, acceptance outcome, regressions, recovery route, duration and cost. A task can pass structurally and still fail semantically. Include a simple edit case to measure unnecessary protocol overhead and an unavailable-tools case to test honest fallback.
