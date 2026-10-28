"""Render bilingual reading lists from the maintained primary-source registry."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "skills/chainwright/references/sources.json").read_text(encoding="utf-8"))
count = len(data["sources"])
for language, filename in [("en", "RESEARCH.md"), ("zh", "RESEARCH.zh-CN.md")]:
    lines = (["# Research dossier", "", "Reviewed: " + data["reviewed_on"], "", data["method"], "",
              f"{count} primary sources covering research, evaluations, software weaknesses and official practice/platform documentation. This collection does not measure overall failure prevalence. Chainwright efficacy is unmeasured.", ""]
             if language == "en" else ["# 研究资料汇编", "", "核实日期：" + data["reviewed_on"], "",
              "定向收集一手资料，不是穷尽性的系统综述；除注明具体章节外，仅核实摘要层面的结论。未复现实验。中文为原创摘要，不转载论文正文。", "",
              f"共 {count} 项一手来源，覆盖研究、评估、软件弱点与官方实践/平台文档。不提供失误的整体发生率；Chainwright 的实际效果尚未测量。", ""])
    for s in data["sources"]:
        lines += ["## " + s["id"] + " · " + s["title"], "",
                  f'[{s["title"]}]({s["url"]}) · {s["year"]} · `{s["kind"]}`', "",
                  s["claim_" + language], "", ("Limit: " if language == "en" else "边界：") + s["limit_" + language], "",
                  ("Inspected: " if language == "en" else "核实位置：") + s["locator"], "",
                  ("Protocol mapping (our design judgment): " if language == "en" else "协议映射（本项目的设计判断）：") + "`" + s["checkpoint"] + "`", ""]
    lines += (["## Interpretation", "", "A prompt adapter is not an enforced runtime, and valid JSON does not prove correctness. Historical model metrics are not current model comparisons. General review guidance motivates checks but does not establish a measured Chainwright improvement rate.", ""]
              if language == "en" else ["## 解释边界", "", "提示词适配不等于强制执行环境，JSON 合法也不证明正确性。历史模型指标不能作为当前模型对比。通用审查指导支持检查方法的选择，不构成 Chainwright 效果提升的测量。", ""])
    output = ROOT / "docs" / filename
    output.parent.mkdir(exist_ok=True)
    output.write_text("\n".join(lines),encoding="utf-8",newline="\n")
