"""Offline release checks; no external tools or network required."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/chainwright"
sys.path.insert(0, str(SKILL / "scripts"))
from audit_state import audit
from export_adapters import render


def validate():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n"), "Missing skill frontmatter"
    front = text.split("---\n", 2)[1]
    assert re.search(r"^name: chainwright$", front, re.M), "Invalid skill name"
    assert re.search(r'^description: "[^"]{1,1024}"$', front, re.M), "Missing description"
    assert "TODO" not in text and "[TODO" not in text, "Unfinished scaffold"
    version = (ROOT / "VERSION").read_text().strip()
    assert f'version: "{version}"' in front, "Version mismatch"
    for name, expected in render(text).items():
        assert (ROOT / "adapters" / name).read_text(encoding="utf-8") == expected, "Stale adapter: " + name
    assert not audit(json.loads((SKILL / "assets/state.example.json").read_text(encoding="utf-8"))), "Example ledger invalid"
    sources = json.loads((SKILL / "references/sources.json").read_text(encoding="utf-8"))
    entries = sources["sources"]
    assert len(entries) == len({s["id"] for s in entries}), "Duplicate source ID"
    for s in entries:
        assert s["url"].startswith("https://") and all(s[k] for k in ("locator", "claim_en", "claim_zh", "limit_en", "limit_zh")), "Incomplete provenance"
    # Build research in place, then require byte-for-byte unchanged artifacts.
    paths = [ROOT / "docs" / name for name in ("RESEARCH.md", "RESEARCH.zh-CN.md")]
    before = [p.read_bytes() for p in paths]
    subprocess.run([sys.executable, str(ROOT / "tools/build_research.py")], check=True)
    assert before == [p.read_bytes() for p in paths], "Research docs were stale; review regenerated versions"
    for base in (ROOT / "skills", ROOT / "docs"):
        for document in base.rglob("*.md"):
            for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
                if "://" in destination or destination.startswith("#"):
                    continue
                assert (document.parent / destination.split("#")[0]).exists(), f"Broken reference in {document.name}: {destination}"
    print(f"Validated skill, adapters, example, local references and {len(entries)} source records")


if __name__ == "__main__":
    validate()
