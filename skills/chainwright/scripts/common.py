"""Shared, bounded, read-only input and JSON output helpers."""
import json
import sys
from pathlib import Path

LIMIT = 2 * 1024 * 1024


def read_text(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError("Input exceeds 2 MiB")
    return raw.decode("utf-8-sig")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(read_text(path), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Invalid JSON constant: " + value)))


def emit(tool, findings, coverage, **extra):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps({"tool": tool, "ok": not findings, "findings": findings,
                      "coverage": coverage, **extra}, ensure_ascii=False, indent=2))
    return 1 if findings else 0


def run(main):
    try:
        code = main()
    except (OSError, ValueError, TypeError, RecursionError, SyntaxError) as exc:
        code = emit("input_error", [{"code": "INPUT", "message": str(exc)}], "No successful analysis", error=True)
        code = 2
    raise SystemExit(code)
