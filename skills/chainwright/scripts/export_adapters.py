"""Generate prompt-only adapters from SKILL.md; never changes host settings."""
import argparse
import hashlib
from pathlib import Path
from common import read_text, run


def render(skill):
    if not skill.startswith("---\n"):
        raise ValueError("SKILL.md frontmatter missing")
    body = skill.split("---\n", 2)[2]
    start, end = "<!-- minimal:start -->", "<!-- minimal:end -->"
    if body.count(start) != 1 or body.count(end) != 1:
        raise ValueError("Minimal protocol markers missing or duplicated")
    minimum = body.split(start, 1)[1].split(end, 1)[0].strip()
    digest = hashlib.sha256(skill.encode("utf-8")).hexdigest()
    preamble = "<!-- Generated from skills/chainwright/SKILL.md; SHA256 " + digest + " -->\n"
    # Retain workflow and command examples, but make resource availability explicit.
    full = body.replace(start, "").replace(end, "")
    full = rehome_links(full)
    return {"minimal.txt": minimum + "\n", "system-prompt.md": preamble +
            "Use these instructions within the host's existing permissions. Referenced resources and commands are optional and may be unavailable; never claim to load or run them without access. The host must provide any file/command tools.\n\n" + full,
            "manifest.json": '{\n  "source": "skills/chainwright/SKILL.md",\n  "sha256": "' + digest + '"\n}\n'}


def rehome_links(text):
    import re
    return re.sub(r"\[([^\]]+)\]\((?:references|assets)/[^)]+\)", r"\1 (optional bundled resource)", text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.out)
    files = render(read_text(root / "SKILL.md").replace("\r\n", "\n"))
    if args.check:
        if any(not (output / name).is_file() or read_text(output / name).replace("\r\n", "\n") != value for name, value in files.items()):
            raise ValueError("Generated adapters are missing or stale")
        print("Adapters match SKILL.md")
    else:
        output.mkdir(parents=True, exist_ok=True)
        for name, value in files.items():
            (output / name).write_text(value, encoding="utf-8", newline="\n")
        print("Generated prompt adapters; no host settings were changed")
    return 0


if __name__ == "__main__":
    run(main)
