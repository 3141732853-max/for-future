import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/chainwright/scripts"
sys.path.insert(0, str(SCRIPTS))
from audit_state import audit, DIMENSIONS, PROFILES
from check_python import inspect
from review_diff import review, parse_diff
from export_adapters import render
from common import read_json


def initial():
    return json.loads((ROOT / "skills/chainwright/assets/state.example.json").read_text(encoding="utf-8"))


def finished():
    data = initial()
    for s in data["steps"]:
        s.update(status="passed", output="Observed artifact", evidence=["Fixture evidence; synthetic, not a real task result"])
    for r in data["review"].values():
        r.update(status="pass", evidence=["Fixture check"])
    data["conclusion"]["status"] = "complete"
    return data


def codes(findings):
    return {f["code"] for f in findings}


class StateTests(unittest.TestCase):
    def test_initial_and_finished(self):
        self.assertEqual(audit(initial()), [])
        self.assertEqual(audit(finished()), [])

    def test_cycle_and_forward_dependency(self):
        d = finished()
        d["steps"][0]["depends_on"] = ["S2"]
        self.assertTrue({"DEPENDENCY_CYCLE", "DEPENDENCY_ORDER"} <= codes(audit(d)))

    def test_unknown_references(self):
        d = initial()
        d["steps"][0].update(premises=["PX"], depends_on=["SX"])
        self.assertTrue({"UNKNOWN_PREMISE", "UNKNOWN_STEP"} <= codes(audit(d)))

    def test_failed_predecessor_blocks_success(self):
        d = finished()
        d["steps"][0]["status"] = "failed"
        self.assertTrue({"DEPENDENCY_STATUS", "RECOVERY_MISSING", "INCOMPLETE_STEPS"} <= codes(audit(d)))

    def test_unverified_given_still_needs_condition(self):
        d = finished()
        d["premises"][0]["verification"] = "unverified"
        self.assertIn("UNRESOLVED_PREMISE", codes(audit(d)))
        d["conclusion"].update(status="conditional", conditions=["P1"])
        self.assertEqual(audit(d), [])

    def test_refuted_cannot_be_conditionally_accepted(self):
        d = finished()
        d["premises"][0]["verification"] = "refuted"
        d["conclusion"].update(status="conditional", conditions=["P1"])
        self.assertTrue({"REFUTED_PREMISE", "CONDITION_REFERENCE"} <= codes(audit(d)))

    def test_evidence_required(self):
        d = finished()
        d["steps"][0]["evidence"] = []
        d["premises"][0]["evidence"] = []
        d["review"]["boundaries"]["evidence"] = []
        self.assertTrue({"STEP_EVIDENCE", "PREMISE_EVIDENCE", "REVIEW_EVIDENCE"} <= codes(audit(d)))

    def test_each_dimension_required(self):
        for dimension in DIMENSIONS:
            d = finished()
            del d["review"][dimension]
            self.assertIn("REVIEW_INCOMPLETE", codes(audit(d)))

    def test_intent_cannot_be_na(self):
        d = finished()
        d["review"]["intent_alignment"]["status"] = "not_applicable"
        self.assertIn("INTENT_REQUIRED", codes(audit(d)))

    def test_noncode_task_needs_no_code_review(self):
        d = finished()
        d.update(code_changed=False, review={}, profiles=[])
        self.assertEqual(audit(d), [])

    def test_recovery_budget(self):
        d = initial()
        d["steps"][0]["status"] = "failed"
        d["recoveries"] = [{"step":"S1", "action":"repair", "attempt":n, "evidence":["Failure still reproduced"]} for n in (1,2,3)]
        self.assertIn("REPAIR_BUDGET", codes(audit(d)))
        d["recoveries"][-1]["action"] = "redesign"
        self.assertEqual(audit(d), [])

    def test_recovery_sequence(self):
        d = initial()
        d["recoveries"] = [{"step":"S1", "action":"stop", "attempt":2, "evidence":["Unavailable tool"]}]
        self.assertIn("RECOVERY_SEQUENCE", codes(audit(d)))

    def test_explicit_repair_budget(self):
        d = initial()
        d["recoveries"] = [{"step":"S1", "action":"repair", "attempt":1, "evidence":["Failed check"]}]
        self.assertIn("REPAIR_BUDGET", codes(audit(d, max_repairs=0)))
        self.assertEqual(audit(d, max_repairs=1), [])

    def test_duplicate_id(self):
        d = initial()
        d["steps"][0]["id"] = "P1"
        with self.assertRaises(ValueError): audit(d)

    def test_wrong_types_and_unknown_fields(self):
        for key, value in [("schema_version", True), ("code_changed", "false"), ("scope", {}), ("review", []), ("steps", [])]:
            d = initial()
            d[key] = value
            with self.assertRaises(ValueError): audit(d)
        d = initial()
        d["steps"][0]["depend_on"] = []
        with self.assertRaises(ValueError): audit(d)

    def test_long_chain_no_recursion(self):
        d = initial()
        template = d["steps"][0]
        d["steps"] = []
        for i in range(500):
            s = copy.deepcopy(template)
            s.update(id="S"+str(i), depends_on=["S"+str(i-1)] if i else [])
            d["steps"].append(s)
        self.assertEqual(audit(d), [])

    def test_v1_compatibility(self):
        d = finished()
        d["schema_version"] = 1
        del d["profiles"]
        self.assertEqual(audit(d), [])

    def test_each_selected_profile_requires_its_checks(self):
        for profile, dimensions in PROFILES.items():
            d = finished()
            d.update(code_changed=False, profiles=[profile], review={})
            result = audit(d)
            self.assertEqual(len([f for f in result if f["code"] == "REVIEW_INCOMPLETE"]),len(dimensions))
            d["review"] = {name:{"status":"pass","evidence":["Observed acceptance check"]} for name in dimensions}
            self.assertEqual(audit(d), [])

    def test_no_code_flag_cannot_bypass_code_profile(self):
        d = finished()
        d.update(code_changed=False, profiles=["code"], review={})
        self.assertIn("REVIEW_INCOMPLETE",codes(audit(d)))

    def test_not_run_requires_explicit_conditional_delivery(self):
        d = finished()
        d["profiles"].append("performance")
        d["review"]["performance"] = {"status":"not_run","evidence":["Benchmark environment unavailable"],"condition":"P1"}
        self.assertIn("REVIEW_CONDITION",codes(audit(d)))
        d["premises"][0]["verification"] = "unverified"
        self.assertIn("REVIEW_INCOMPLETE",codes(audit(d)))
        d["conclusion"].update(status="conditional",conditions=["P1"])
        self.assertEqual(audit(d), [])

    def test_failed_unselected_profile_is_not_hidden(self):
        d = finished()
        d["review"]["visual_quality"] = {"status":"fail","evidence":["Clipping observed"]}
        self.assertIn("REVIEW_INCOMPLETE",codes(audit(d)))

    def test_visual_without_interaction_can_explain_na(self):
        d = finished()
        d.update(code_changed=False,profiles=["visual"],review={
            "visual_quality":{"status":"pass","evidence":["Rendered illustration inspected"]},
            "interaction_accessibility":{"status":"not_applicable","evidence":["Static illustration with no controls"]}})
        self.assertEqual(audit(d), [])

    def test_unknown_profiles_and_not_run_without_condition(self):
        d = finished()
        d["profiles"] = ["magic"]
        with self.assertRaises(ValueError): audit(d)
        d = finished()
        d["review"]["control_flow"] = {"status":"not_run","evidence":["No tool"]}
        with self.assertRaises(ValueError): audit(d)


class PythonTests(unittest.TestCase):
    def test_clean_function(self):
        self.assertEqual(inspect("def add(a,b):\n    result=a+b\n    return result\n"), [])

    def test_unreachable(self):
        self.assertIn("PY_UNREACHABLE", codes(inspect("def f():\n    return 1\n    print('dead')\n")))

    def test_not_infer_if_terminates(self):
        self.assertNotIn("PY_UNREACHABLE", codes(inspect("def f(x):\n    if x:\n        return 1\n    return 2\n")))

    def test_unused_binding_and_import(self):
        findings = inspect("def f():\n    import os\n    forgotten=3\n    _ignored=4\n    return 1\n")
        self.assertEqual(len([f for f in findings if f["code"] == "PY_UNUSED_LOCAL"]), 2)

    def test_closure_and_comprehension_not_false_unused(self):
        source = "def outer():\n    x=2\n    def inner():\n        return x\n    return inner\n"
        self.assertNotIn("PY_UNUSED_LOCAL", codes(inspect(source)))
        self.assertNotIn("PY_UNUSED_LOCAL", codes(inspect("def f(xs):\n    offset=2\n    return [x+offset for x in xs]\n")))

    def test_dynamic_scope_skips_unused(self):
        self.assertNotIn("PY_UNUSED_LOCAL", codes(inspect("def f():\n    x=2\n    return locals()\n")))

    def test_augmented_assignment_reads_binding(self):
        self.assertNotIn("PY_UNUSED_LOCAL", codes(inspect("def f():\n    x=[]\n    x += [1]\n")))

    def test_literal_zero_and_indexes(self):
        self.assertTrue({"PY_ZERO_DIVISION", "PY_LITERAL_INDEX"} <= codes(inspect("x=2/0\ny=[][0]\n")))
        self.assertNotIn("PY_LITERAL_INDEX", codes(inspect("x=[1][-1]\ny=[*a][9]\n")))

    def test_boundary_notice_is_candidate_even_with_guard(self):
        findings = inspect("def f(xs):\n    return xs[0] if xs else None\n")
        self.assertEqual(findings[0]["certainty"], "review_candidate")

    def test_syntax_error(self):
        with self.assertRaises(SyntaxError): inspect("def broken(:")

    def test_never_execute_input(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".chainwright-test-") as folder:
            marker = Path(folder) / "must-not-exist"
            inspect("open(" + repr(str(marker)) + ", 'w').write('bad')\n")
            self.assertFalse(marker.exists())


class DiffTests(unittest.TestCase):
    def test_allowed_normal_change(self):
        result, count = review("--- a/src/a.py\n+++ b/src/a.py\n@@ -1 +1 @@\n-x=1\n+x=2\n", {"allowed_paths":["src/*"]})
        self.assertEqual((result, count), ([], 1))

    def test_out_of_scope_removed_assert_and_skip(self):
        diff = "--- a/tests/test_a.py\n+++ b/tests/test_a.py\n@@ -1 +1 @@\n-assert valid(x)\n+pytest.skip('temporary')\n"
        result, _ = review(diff, {"allowed_paths":["src/*"]})
        self.assertTrue({"DIFF_SCOPE", "DIFF_REMOVED_CHECK", "DIFF_SKIP", "DIFF_TEST_CHANGE"} <= codes(result))

    def test_rename_both_paths(self):
        diff = 'diff --git a/private.py b/src/a.py\nsimilarity index 100%\nrename from private.py\nrename to src/a.py\n'
        result, count = review(diff, {"allowed_paths":["src/*"]})
        self.assertEqual(count, 1)
        self.assertEqual(result[0]["file"], "private.py")

    def test_new_and_deleted_file(self):
        for diff in ["--- /dev/null\n+++ b/a.py\n@@ -0,0 +1 @@\n+x=1\n", "--- a/a.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x=1\n"]:
            self.assertEqual(review(diff, {"allowed_paths":["a.py"]}), ([], 1))

    def test_rename_with_content_is_one_file(self):
        diff = "diff --git a/old.py b/new.py\nsimilarity index 50%\nrename from old.py\nrename to new.py\n--- a/old.py\n+++ b/new.py\n@@ -1 +1 @@\n-x\n+y\n"
        files = parse_diff(diff)
        self.assertEqual(len(files),1)
        self.assertEqual((files[0]["old"],files[0]["new"]),("old.py","new.py"))

    def test_multiple_files_and_header_like_content(self):
        diff = "--- a/a.py\n+++ b/a.py\n@@ -1 +1 @@\n--- content\n+++ content\n--- a/b.py\n+++ b/b.py\n@@ -1 +1 @@\n-x\n+y\n"
        self.assertEqual(len(parse_diff(diff)), 2)

    def test_quoted_unicode_and_spaces(self):
        diff = '--- "a/\\344\\270\\255.py"\n+++ "b/\\344\\270\\255.py"\n@@ -1 +1 @@\n-a\n+b\n'
        self.assertEqual(parse_diff(diff)[0]["new"], "中.py")
        self.assertEqual(parse_diff('--- a/my file.py\n+++ b/my file.py\n@@ -1 +1 @@\n-a\n+b\n')[0]["new"], "my file.py")

    def test_malformed_binary_combined(self):
        for text in ["GIT binary patch\n", "@@@ -1 -1 +1 @@@\n", "--- a/a.py\n+++ b/a.py\n@@ -2 +2 @@\n-a\n", "hello", "+++ b/a.py"]:
            with self.assertRaises(ValueError): parse_diff(text)

    def test_unsafe_path(self):
        with self.assertRaises(ValueError): parse_diff("--- a/../secret\n+++ b/../secret\n")

    def test_missing_old_header_in_git_diff(self):
        with self.assertRaises(ValueError): parse_diff("diff --git a/a.py b/a.py\n+++ b/a.py\n@@ -0,0 +1 @@\n+x=1\n")

    def test_header_only_files_not_silently_dropped(self):
        self.assertEqual(len(parse_diff("--- a/a.py\n+++ b/a.py\n--- a/b.py\n+++ b/b.py\n")), 2)

    def test_empty_diff(self):
        self.assertEqual(review("", {"allowed_paths":["src/*"]}), ([],0))


class InterfaceTests(unittest.TestCase):
    def test_cli_exit_codes_json_and_readonly(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".chainwright-test-") as folder:
            file = Path(folder) / "样例.py"
            for source, code in [("x=1\n",0),("x=1/0\n",1),("if :\n",2)]:
                file.write_text(source,encoding="utf-8")
                result = subprocess.run([sys.executable,str(SCRIPTS/"check_python.py"),str(file)],capture_output=True,encoding="utf-8")
                self.assertEqual(result.returncode,code,result.stderr)
                self.assertIn("findings",json.loads(result.stdout))
                self.assertEqual(file.read_text(encoding="utf-8"),source)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT, prefix=".chainwright-test-") as folder:
            p=Path(folder)/"state.json"
            p.write_text('{"a":1,"a":2}',encoding="utf-8")
            with self.assertRaises(ValueError): read_json(p)

    def test_adapter_source_hash_and_prompt(self):
        skill=(ROOT/"skills/chainwright/SKILL.md").read_text(encoding="utf-8")
        a=render(skill)
        b=render(skill+"\nChange\n")
        self.assertNotEqual(a["manifest.json"],b["manifest.json"])
        self.assertLess(len(a["minimal.txt"]),1500)
        self.assertNotIn("](references/",a["system-prompt.md"])
        self.assertIn("control_flow",a["system-prompt.md"])


if __name__ == "__main__":
    unittest.main()
