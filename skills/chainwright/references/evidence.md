# Evidence map

Read only the sources relevant to a live task; do not load this bibliography into every conversation. [sources.json](sources.json) is the maintained registry, with exact URLs, inspected sections, bilingual summaries, numerical denominators, and limits. Reviewed 2026-10-28. This is a targeted primary-source collection, not an exhaustive systematic review or a reproduction of results.

| Need | Sources | Chainwright design inference |
| --- | --- | --- |
| Security and false confidence | R01, R02 | Record actual security evidence instead of confidence alone |
| Boundary failures and weak tests | R03, R16 | Use counterexamples and meaningful acceptance checks |
| Invented packages, APIs and repository context | R04, R05 | Verify dependencies against real definitions and versions |
| Cross-method/file consistency | R06, R07 | Keep explicit dependency contracts and integration checks |
| Unproductive correction | R08, R09, R14 | Use external feedback and bounded, classified recovery |
| Unfaithful explanations / context loss | R10, R11 | Keep compact observable evidence; never demand private CoT |
| Tests pass but task not solved | R12 | Preserve protections and audit intent against the diff |
| Protocol overhead | R13 | Measure elapsed time and cost, not just completion claims |
| Race conditions | R15 | Use concurrency-specific checks when the contract needs them |
| Packaging / adapters | R17–R21 | One canonical SKILL.md; host capability and execution are separate |
| Visual / interaction review | R22 | Inspect renderings and interactions against applicable accessibility criteria |
| Performance review | R23 | Compare relevant workloads and operational signals against a baseline |

The research establishes reasons to investigate these problems. It does **not** establish that Chainwright reduces errors or improves productivity. ReFlect (2026 preprint) and Reflexion (2023) are distinct; this skill borrows a protocol design idea, not their implementation or measured results. No third-party paper, dataset, figure, or code is vendored. Synthetic examples and tests in this repository are our own.
