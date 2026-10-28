"""Create deterministic local ZIPs from an allowlisted source tree. No upload."""
import hashlib
import re
import zipfile
from pathlib import Path
from validate_repo import validate, ROOT

ROOT_FILES = {"README.md", "README.zh-CN.md", "LICENSE", "VERSION", "CONTRIBUTING.md", "SECURITY.md", ".gitignore", ".gitattributes"}
DIRECTORIES = ("skills", "adapters", "docs", "eval", "tests", "tools", ".github")


def selected_files():
    files = [ROOT / name for name in ROOT_FILES]
    for directory in DIRECTORIES:
        base = ROOT / directory
        if base.is_symlink():
            raise ValueError("Symlinks cannot be packaged: " + directory)
        for path in base.rglob("*"):
            if path.is_symlink():
                raise ValueError("Symlinks cannot be packaged: " + str(path))
            excluded = {"__pycache__", ".git", ".chainwright", ".venv", "dist", ".verification-deps"}
            if path.is_file() and not excluded.intersection(path.parts) and path.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".txt"} and not path.name.startswith(".env"):
                files.append(path)
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError("File escaped source root")
    return sorted(files)


def make_zip(destination, entries):
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 28, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt ZIP")


def main():
    validate()
    version = (ROOT / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Invalid version")
    output = ROOT / "dist"
    if output.is_symlink():
        raise ValueError("dist must not be a symlink")
    output.mkdir(exist_ok=True)
    files = selected_files()
    source = output / f"chainwright-{version}-source.zip"
    skill = output / f"chainwright-{version}-skill.zip"
    make_zip(source, [("chainwright/" + p.relative_to(ROOT).as_posix(), p) for p in files])
    skill_root = ROOT / "skills/chainwright"
    skill_entries = [("chainwright/" + p.relative_to(skill_root).as_posix(), p) for p in files if p.is_relative_to(skill_root)]
    skill_entries.append(("chainwright/LICENSE", ROOT / "LICENSE"))
    make_zip(skill, skill_entries)
    manifest = "".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + p.name + "\n" for p in (skill, source))
    (output / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8", newline="\n")
    print(f"Packaged {len(files)} source files; no upload performed")
    print(manifest, end="")


if __name__ == "__main__":
    main()
