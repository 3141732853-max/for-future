# Review profiles / 按需专项检查

Read only the relevant section. Existing specs, tests, design systems and budgets are the starting point; reuse their references rather than rewriting them. A selected profile needs evidence or an explicit `not_run` limitation. It grants no execution permissions.

## Debug: semantic validity

Reproduce the behavior through the real affected path with the smallest meaningful input. Capture expected/actual behavior, relevant version and state; for intermittent defects, record frequency and triggers. Trace actual data and calls, then identify the violated invariant. Separate a hypothesis from a demonstrated cause.

Choose a discriminating check: regression input, property/invariant, metamorphic relation, differential reference, debugger observation or integration suite. Verify assumptions about any reference implementation. Confirm the original reproduction and adjacent preserved behavior after the fix. Without reproduction, label the diagnosis provisional; passing lint does not resolve a deep bug.

中文：最小复现后追踪真正的调用与数据路径，以不变量和反例检验原因。无法复现时给出暂定诊断，不宣称深层 bug 已修复。

## Performance: budgets and measurement

State the workload (size, mix, concurrency, duration), environment/version and objective from an existing budget or a labeled proposed target. Establish a baseline before optimizing. Choose relevant metrics: throughput, median/tail latency, memory/CPU, frame time, startup delay, error rate or saturation. Do not require server metrics for a small offline script.

Compare before/after under equivalent conditions; note warm-up, repeated trials, variance and tradeoffs. Check correctness and error rate alongside speed. For capacity claims, bound the load, stop thresholds and cost; never load-test production or third-party systems without authorization. No benchmark access means a proposed optimization, not a measured speedup.

Google's [monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/) provides latency/traffic/error/saturation signals, not universal acceptance targets.

中文：先记录负载、环境和目标，再测基线与改后表现。看适用的尾延迟、容量、资源和错误率；没有测量就明确待测。

## Concurrency: invariants and interleavings

Identify shared mutable state, ownership, ordering, retries, cancellation and resource lifetime. State the invariant: no duplicate side effect, no lost update, bounded queue, consistent version or eventual cleanup. Check success and failure paths.

Use controlled interleavings/barriers, duplicate requests, cancellation/error injection or native race/thread sanitizers when available. Repeating sequential tests or one successful stress run is weak evidence. Review deadlock ordering, timeouts, backpressure and idempotency where relevant. Retain reproducing schedules/inputs; repeated invariant failures call for design review.

中文：找共享状态与必须保持的不变量，再测试交错执行、重试、取消和重复副作用。顺序测试通过不等于无竞态。

## Visual: rendered quality and interaction

Inspect actual rendered artifacts at relevant sizes and content lengths. Compare with the brief/design system: hierarchy, spacing, clipping, legibility, consistency and empty/loading/error/success states. Report observable defects separately from subjective alternatives; creator preferences govern taste.

Exercise the main flow: discoverability, affordances, feedback, error recovery, keyboard navigation, focus visibility/order and accessible names. Include relevant zoom/reflow and contrast checks. Screenshots and interaction observations are evidence; source review alone is not visual inspection. Automated accessibility checks supplement manual interaction. [WCAG quick reference](https://www.w3.org/WAI/WCAG22/quickref/) provides accessibility criteria, not an aesthetic score.

Without a renderer/screenshot or UI access, deliver a source-level review and mark visual/interaction checks `not_run`. For a static illustration, inspect visual quality and explain that interaction is not applicable.

中文：看真实渲染和关键状态，实际走主流程，检查焦点、键盘、可读性与布局。无界面访问则标注未检查；静态插画无需强加交互检查。

## Content: factual integrity

Match the audience and brief. Verify consequential claims against primary sources with date, scope and units. Recompute important totals and compare labels, captions, tables and prose. Distinguish facts, estimates and creative invention; don't treat fictional worldbuilding as an empirical claim. Reuse editorial/style guides and record only deviations or conflicts.

中文：核对事实、来源、日期、单位以及图文数字一致性，区分事实、估计与创作设定，直接引用现有编辑规范。

## Evidence status

Use `pass` for checked criteria, `fail` for observed violations, `pending` for unfinished work, `not_applicable` with a concrete reason, or `not_run` with missing capability/condition. A conditional delivery names the unresolved premise. Never hide a missing tool as not applicable. State v2 validates these declarations, not visual quality, benchmark validity or semantic truth.
