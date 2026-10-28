"""Validate an external checkpoint ledger; never evaluates its evidence."""
import argparse
import re
from collections import deque
from common import emit, read_json, run

DIMENSIONS = {"control_flow", "data_dependencies", "boundaries", "intent_alignment"}
PROFILES = {
    "code": DIMENSIONS,
    "debug": {"semantic_validity"},
    "performance": {"performance"},
    "concurrency": {"concurrency"},
    "visual": {"visual_quality", "interaction_accessibility"},
    "content": {"factual_integrity"},
}
ALL_DIMENSIONS = set().union(*PROFILES.values())
ACTIONS = {"decompose", "verify_premise", "conditionalize", "repair", "redesign", "stop"}


def obj(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields.split()):
        raise ValueError(label + " must have exactly these fields: " + fields)


def string(value, label, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ValueError(label + " must be a nonempty string")


def strings(value, label):
    if not isinstance(value, list) or len(value) > 500:
        raise ValueError(label + " must be an array of at most 500 strings")
    for item in value:
        string(item, label)
    if len(value) != len(set(value)):
        raise ValueError(label + " has duplicate entries")


def choice(value, options, label):
    if not isinstance(value, str) or value not in options:
        raise ValueError(label + " must be one of: " + ", ".join(sorted(options)))


def audit(data, max_repairs=2):
    if type(max_repairs) is not int or not 0 <= max_repairs <= 20:
        raise ValueError("max_repairs must be an integer from 0 to 20")
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] not in (1, 2):
        raise ValueError("Unsupported schema_version")
    version = data["schema_version"]
    obj(data, "schema_version goal scope premises steps code_changed review recoveries conclusion" + (" profiles" if version == 2 else ""), "ledger")
    profiles = data.get("profiles", [])
    strings(profiles, "profiles")
    if set(profiles) - PROFILES.keys():
        raise ValueError("Unknown review profile")
    string(data["goal"], "goal")
    strings(data["scope"], "scope")
    if not data["scope"] or type(data["code_changed"]) is not bool:
        raise ValueError("scope must be nonempty and code_changed must be boolean")
    for key in ("premises", "steps", "recoveries"):
        if not isinstance(data[key], list) or len(data[key]) > 500:
            raise ValueError(key + " must be an array of at most 500 objects")
    if not data["steps"]:
        raise ValueError("At least one step is required")
    findings = []

    def flag(code, message):
        findings.append({"code": code, "message": message})

    ids = set()
    for item in data["premises"] + data["steps"]:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", item["id"]):
            raise ValueError("Invalid premise/step ID")
        if item["id"] in ids:
            raise ValueError("Duplicate ID: " + item["id"])
        ids.add(item["id"])
    premises = {}
    for p in data["premises"]:
        obj(p, "id claim basis verification evidence", "premise")
        string(p["claim"], "claim")
        choice(p["basis"], {"given", "inferred", "assumed"}, "basis")
        choice(p["verification"], {"verified", "unverified", "refuted"}, "verification")
        strings(p["evidence"], "premise evidence")
        if p["verification"] != "unverified" and not p["evidence"]:
            flag("PREMISE_EVIDENCE", p["id"] + " has a verification claim without evidence")
        premises[p["id"]] = p
    steps = {s["id"]: s for s in data["steps"]}
    positions = {s["id"]: i for i, s in enumerate(data["steps"])}
    used = set()
    children = {sid: [] for sid in steps}
    indegree = {sid: 0 for sid in steps}
    for s in data["steps"]:
        obj(s, "id premises depends_on expected check status output evidence", "step")
        for key in ("premises", "depends_on", "evidence"):
            strings(s[key], key)
        for key in ("expected", "check"):
            string(s[key], key)
        string(s["output"], "output", empty=True)
        choice(s["status"], {"pending", "running", "passed", "failed", "blocked"}, "step status")
        used.update(s["premises"])
        for pid in s["premises"]:
            if pid not in premises:
                flag("UNKNOWN_PREMISE", s["id"] + " refers to " + pid)
            elif premises[pid]["verification"] == "refuted" and s["status"] in {"running", "passed"}:
                flag("REFUTED_PREMISE", s["id"] + " uses refuted " + pid)
        if s["status"] == "passed" and (not s["output"].strip() or not s["evidence"]):
            flag("STEP_EVIDENCE", s["id"] + " passed without output/evidence")
        for dep in s["depends_on"]:
            if dep not in steps:
                flag("UNKNOWN_STEP", s["id"] + " depends on " + dep)
                continue
            children[dep].append(s["id"])
            indegree[s["id"]] += 1
            if positions[dep] >= positions[s["id"]]:
                flag("DEPENDENCY_ORDER", s["id"] + " must depend only on earlier steps")
            if s["status"] in {"running", "passed"} and steps[dep].get("status") != "passed":
                flag("DEPENDENCY_STATUS", s["id"] + " consumes unfinished/failed " + dep)
    queue = deque(sid for sid, degree in indegree.items() if degree == 0)
    visited = 0
    while queue:
        sid = queue.popleft()
        visited += 1
        for child in children[sid]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    if visited != len(steps):
        flag("DEPENDENCY_CYCLE", "Step dependencies contain a cycle")
    if not isinstance(data["review"], dict) or set(data["review"]) - (ALL_DIMENSIONS if version == 2 else DIMENSIONS):
        raise ValueError("Unknown review dimension or invalid review object")
    for dimension, review in data["review"].items():
        is_not_run = version == 2 and isinstance(review, dict) and review.get("status") == "not_run"
        obj(review, "status evidence" + (" condition" if is_not_run else ""), "review")
        choice(review["status"], {"pending", "pass", "fail", "not_applicable"} | ({"not_run"} if version == 2 else set()), "review status")
        strings(review["evidence"], "review evidence")
        if review["status"] != "pending" and not review["evidence"]:
            flag("REVIEW_EVIDENCE", dimension + " lacks evidence/reason")
        if is_not_run:
            pid = review["condition"]
            string(pid, "review condition")
            if pid not in used or pid not in premises or premises[pid]["verification"] != "unverified":
                flag("REVIEW_CONDITION", dimension + " needs an unverified used premise for the missing check")
    attempts, repairs = {}, {}
    for recovery in data["recoveries"]:
        obj(recovery, "step action attempt evidence", "recovery")
        string(recovery["step"], "recovery step")
        choice(recovery["action"], ACTIONS, "recovery action")
        strings(recovery["evidence"], "recovery evidence")
        sid = recovery["step"]
        if sid not in steps:
            flag("RECOVERY_STEP", "Recovery references unknown " + sid)
        if type(recovery["attempt"]) is not int or recovery["attempt"] != attempts.get(sid, 0) + 1:
            flag("RECOVERY_SEQUENCE", sid + " recovery attempts must start at 1 and increment")
        if type(recovery["attempt"]) is int:
            attempts[sid] = recovery["attempt"]
        if not recovery["evidence"]:
            flag("RECOVERY_EVIDENCE", sid + " recovery lacks evidence")
        if recovery["action"] == "repair":
            repairs[sid] = repairs.get(sid, 0) + 1
            if repairs[sid] > max_repairs:
                flag("REPAIR_BUDGET", sid + " exceeds the local repair budget; redesign a new contract or stop")
    for s in data["steps"]:
        if s["status"] in {"failed", "blocked"} and s["id"] not in attempts:
            flag("RECOVERY_MISSING", s["id"] + " requires a recovery decision")
    conclusion = data["conclusion"]
    obj(conclusion, "status summary conditions", "conclusion")
    choice(conclusion["status"], {"in_progress", "complete", "conditional", "blocked"}, "conclusion status")
    string(conclusion["summary"], "conclusion summary")
    strings(conclusion["conditions"], "conditions")
    unresolved = {pid for pid in used if pid in premises and premises[pid]["verification"] == "unverified"}
    for pid in conclusion["conditions"]:
        if pid not in unresolved:
            flag("CONDITION_REFERENCE", pid + " is not an unresolved used premise")
    if conclusion["status"] in {"complete", "conditional"}:
        if any(s["status"] != "passed" for s in data["steps"]):
            flag("INCOMPLETE_STEPS", "Final conclusion requires all steps passed")
        if unresolved and (conclusion["status"] != "conditional" or unresolved - set(conclusion["conditions"])):
            flag("UNRESOLVED_PREMISE", "Retain every unresolved premise as an explicit final condition")
        if conclusion["status"] == "conditional" and not conclusion["conditions"]:
            flag("EMPTY_CONDITIONS", "Conditional conclusion has no conditions")
        required = set(DIMENSIONS) if data["code_changed"] else set()
        for profile in profiles:
            required.update(PROFILES[profile])
        # A declared failure cannot disappear merely because its profile is omitted.
        required.update(data["review"])
        for dimension in sorted(required):
            review = data["review"].get(dimension, {})
            status = review.get("status")
            conditional_check = (status == "not_run" and conclusion["status"] == "conditional"
                                 and review.get("condition") in conclusion["conditions"])
            if status not in {"pass", "not_applicable"} and not conditional_check:
                flag("REVIEW_INCOMPLETE", dimension + " must be reviewed or explicitly conditionalized before finalization")
            if dimension == "intent_alignment" and status == "not_applicable":
                flag("INTENT_REQUIRED", "Changed code always requires intent alignment review")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state")
    parser.add_argument("--max-repairs", type=int, default=2)
    args = parser.parse_args()
    return emit("audit_state", audit(read_json(args.state), args.max_repairs), "Snapshot structure/status only; evidence truth, history and semantics are not verified")


if __name__ == "__main__":
    run(main)
