"""Flag scope and review risks in unified diffs, without applying them."""
import argparse
import ast
import fnmatch
import re
from common import emit, read_json, read_text, run


def path_name(value, strip_prefix=False):
    value = value.split("\t", 1)[0]
    if value.startswith('"'):
        decoded = ast.literal_eval(value)
        if not isinstance(decoded, str):
            raise ValueError("Invalid quoted diff path")
        if re.search(r"\\[0-7]{3}", value):
            decoded = decoded.encode("latin1").decode("utf-8")
        value = decoded
    if value == "/dev/null":
        return None
    if strip_prefix and value.startswith(("a/", "b/")):
        value = value[2:]
    if not value or value.startswith(("/", "\\")) or "\\" in value or ":" in value or any(x in ("", ".", "..") for x in value.split("/")):
        raise ValueError("Unsupported or unsafe diff path: " + repr(value))
    return value


def parse_diff(text):
    files, current = [], None
    old_left = new_left = 0
    old_line = new_line = 0
    in_hunk = False

    def finish():
        if old_left or new_left:
            raise ValueError("Truncated diff hunk")
        if current is not None:
            if not current["paired"] or (current["old"] is None and current["new"] is None):
                raise ValueError("Missing file headers; unsupported metadata-only diff")
            files.append(current)

    for line in text.splitlines():
        if in_hunk and (old_left or new_left):
            if line == r"\ No newline at end of file":
                continue
            if not line or line[0] not in " +-":
                raise ValueError("Malformed hunk content")
            marker, content = line[0], line[1:]
            if marker in " -":
                old_left -= 1
                old_line += 1
            if marker in " +":
                new_left -= 1
                new_line += 1
            if old_left < 0 or new_left < 0:
                raise ValueError("Diff hunk line count mismatch")
            if marker != " ":
                current["changes"].append((marker, content, old_line - 1 if marker == "-" else new_line - 1))
            continue
        in_hunk = False
        if line.startswith(("GIT binary patch", "Binary files ", "@@@", "diff --cc ", "diff --combined ")):
            raise ValueError("Binary/combined diffs require manual review")
        if line.startswith("diff --git "):
            finish()
            current = {"old": None, "new": None, "paired": False, "old_seen": False, "changes": []}
        elif line.startswith("--- "):
            if current is not None and current["paired"] and current["old_seen"]:
                finish()
                current = None
            if current is None:
                current = {"old": None, "new": None, "paired": False, "old_seen": False, "changes": []}
            if current["old_seen"]:
                raise ValueError("Repeated old-file header")
            current["paired"] = False
            current["old"] = path_name(line[4:], True)
            current["old_seen"] = True
        elif line.startswith("+++ "):
            if current is None or not current["old_seen"] or current["paired"]:
                raise ValueError("New path without old header")
            current["new"] = path_name(line[4:], True)
            current["paired"] = True
        elif line.startswith("rename from ") or line.startswith("copy from "):
            if current is None:
                raise ValueError("Rename outside diff")
            current["old"] = path_name(line.split(" from ", 1)[1])
        elif line.startswith("rename to ") or line.startswith("copy to "):
            if current is None or current["old"] is None:
                raise ValueError("Rename lacks origin")
            current["new"] = path_name(line.split(" to ", 1)[1])
            current["paired"] = True
        elif line.startswith("@@ "):
            match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:.*)$", line)
            if not match or current is None or not current["paired"]:
                raise ValueError("Invalid unified hunk/header")
            old_line, old_count, new_line, new_count = match.groups()
            old_line, new_line = int(old_line), int(new_line)
            old_left = int(old_count) if old_count is not None else 1
            new_left = int(new_count) if new_count is not None else 1
            in_hunk = True
        elif line == r"\ No newline at end of file" or not line:
            continue
        elif line.startswith(("index ", "new file mode ", "deleted file mode ", "old mode ", "new mode ", "similarity index ", "dissimilarity index ")) and current is not None:
            continue
        else:
            raise ValueError("Unrecognized diff line; supply a plain unified diff")
    finish()
    return files


def review(text, scope):
    if not isinstance(scope, dict) or set(scope) != {"allowed_paths"} or not isinstance(scope["allowed_paths"], list) or not scope["allowed_paths"]:
        raise ValueError("scope needs a nonempty allowed_paths array")
    for pattern in scope["allowed_paths"]:
        if not isinstance(pattern, str):
            raise ValueError("Scope paths must be strings")
        path_name(pattern)
    files = parse_diff(text)
    findings = []
    for item in files:
        paths = {p for p in (item["old"], item["new"]) if p is not None}
        target = item["new"] or item["old"]
        for path in sorted(paths):
            if not any(fnmatch.fnmatchcase(path, pattern) for pattern in scope["allowed_paths"]):
                findings.append({"code": "DIFF_SCOPE", "file": path, "message": "Path is outside the declared scope"})
        if any(re.search(r"(^|/)(tests?(/|_)|.*[._]test[.])|(^|/)test_[^/]+$", p) for p in paths):
            findings.append({"code": "DIFF_TEST_CHANGE", "file": target, "message": "Test changed: review whether coverage/expectations were weakened"})
        if any(p.rsplit("/", 1)[-1] in {"package.json", "package-lock.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod"} or p.startswith(".github/") for p in paths):
            findings.append({"code": "DIFF_CONFIG", "file": target, "message": "Dependency or workflow change needs contract/version review"})
        for marker, content, line in item["changes"]:
            if marker == "-" and re.search(r"\b(assert|raise|throw|validate|authorize|check_permission)\b", content):
                findings.append({"code": "DIFF_REMOVED_CHECK", "file": item["old"], "line": line, "message": "Removed check/exception candidate; confirm equivalent behavior remains"})
            if marker == "+" and re.search(r"\b(skip|skipIf|xfail)\b|\.skip\s*\(", content):
                findings.append({"code": "DIFF_SKIP", "file": target, "line": line, "message": "Added skip/xfail candidate; verify it does not hide the requested fix"})
    return findings, len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diff")
    parser.add_argument("--scope", required=True)
    args = parser.parse_args()
    findings, count = review(read_text(args.diff), read_json(args.scope))
    return emit("review_diff", findings, "File scope and textual risk signals only; semantic regressions and intent require review", files=count)


if __name__ == "__main__":
    run(main)
