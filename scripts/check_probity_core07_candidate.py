"""Qualify candidate Core 0.7 code without changing the agreed reader population."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

AGREED_REVISION = "a87a395b54b5685fd22d6cc86d120058f1c8850d"
READER_REVISION = "cbd3ea8f4de89b835d6d3c4182ff4b4b1c7608f9"
MANIFEST_DIGEST = "b05b6284f591f74e35065d24ef44466e610304134ca42416dbf2a6b8e4232565"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(root: Path, expression: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", expression], text=True).strip()


def write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def tracked_files(root: Path, prefix: str) -> dict[str, Any]:
    names = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "-z", "--", prefix]
    ).decode().split("\0")
    result = {}
    for name in filter(None, names):
        path = root / name
        if path.is_symlink():
            raise ValueError("Source symlink: " + name)
        content = path.read_bytes()
        blob = git(root, "HEAD:" + name)
        actual_blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if blob != actual_blob:
            raise ValueError("Tracked source differs from the recorded commit: " + name)
        result[name] = {"bytes": len(content), "sha256": sha(path), "git_blob": blob}
    return result


def native(candidate: Path, suite: Path, destination: Path, package: Path | None = None) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=False)
    base_revision = git(candidate, "HEAD")
    mutation = ({str(path.relative_to(package)): sha(path) for path in sorted(package.rglob("*.py"))}
                if package is not None else {})
    execution_revision = ("local-fault-sha256:" + hashlib.sha256(json.dumps(mutation, sort_keys=True).encode()).hexdigest()
                          if mutation else base_revision)
    identity = {"name": "candidate-reference-wrapper", "version": "source-checkout",
                "source": "https://github.com/" + os.environ.get("GITHUB_REPOSITORY", "astrogilda/jep-core"),
                "revision": execution_revision, "base_revision": base_revision,
                "fault_source_files": mutation,
                "independence": "reference-wrapper; not an independent implementation",
                "reused_components": ["candidate JEP validator, producer and BYOI runner"],
                "local_fault_control": package is not None}
    write(destination / "implementation.json", identity)
    env = os.environ.copy()
    if package is not None:
        env["PYTHONPATH"] = str(package)
    argv = [sys.executable, "-m", "jep_conformance.byoi", "run", "--suite", str(suite),
            "--implementation", str(destination / "implementation.json"),
            "--adapter", json.dumps([sys.executable, "-m", "jep_conformance.byoi_reference_adapter"]),
            "--role", "verifier", "--role", "producer", "--report", str(destination / "report.json")]
    done = subprocess.run(argv, cwd=candidate, env=env, capture_output=True, text=True, timeout=120)
    (destination / "stdout.log").write_text(done.stdout)
    (destination / "stderr.log").write_text(done.stderr)
    write(destination / "execution.json", {"argv": argv, "exit_status": done.returncode,
                                          "suite_manifest_sha256": sha(suite / "manifest.json")})
    report_path = destination / "report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {
        "outcome": "incomplete", "requested_roles": [], "tests_passed": 0,
        "tests_failed": 0, "tests_unsupported": 0, "tests_not_selected": 0, "results": []}
    return {"exit_status": done.returncode, "report": report}


def native_pass(result: dict[str, Any], suite: Path) -> bool:
    manifest = json.loads((suite / "manifest.json").read_text())
    report = result["report"]
    population = len(manifest["assertions"]) + len(manifest["producer_assertions"])
    return (result["exit_status"] == 0 and report["outcome"] == "pass"
            and report["requested_roles"] == ["producer", "verifier"]
            and (report["tests_passed"], report["tests_failed"], report["tests_unsupported"],
                 report["tests_not_selected"]) == (population, 0, 0, len(manifest["acceptance_assertions"])))


def reader_run(reader: Path, suite: Path, output: Path, logs: Path) -> dict[str, Any]:
    argv = [sys.executable, str(reader / "interop/jep-core07-reader/run.py"),
            "--upstream", str(suite), "--output", str(output), "--reader-revision", READER_REVISION]
    done = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    logs.mkdir(parents=True, exist_ok=False)
    (logs / "stdout.log").write_text(done.stdout)
    (logs / "stderr.log").write_text(done.stderr)
    write(logs / "execution.json", {"argv": argv, "exit_status": done.returncode,
                                    "suite_manifest_sha256": sha(suite / "manifest.json")})
    return {"exit_status": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def faults(candidate: Path, suite: Path, output: Path) -> dict[str, Any]:
    mutations = {
        "duplicate-admission": ("jep_validate_07.py",
            "json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)",
            "json.loads(text, parse_constant=_reject_constant)"),
        "signature-verification": ("jep_validate_07.py",
            "VerifyKey(raw_key).verify(signing_input, raw_sig)", "None  # synthetic signature bypass"),
        "producer-assignment": ("byoi_reference_adapter.py",
            "event = dict(request['unsigned_event'])",
            "event = dict(request['unsigned_event'])\n        event['id'] = 'synthetic-wrong-id'"),
    }
    results = {}
    for name, (filename, before, after) in mutations.items():
        root = output / name / "package"
        module = root / "jep_conformance"
        shutil.copytree(candidate / "reference-validator", module, ignore=shutil.ignore_patterns("__pycache__"))
        path = module / filename
        text = path.read_text()
        if text.count(before) != 1:
            raise ValueError("Fault control needs review after candidate refactoring: " + name)
        original_digest = sha(path)
        path.write_text(text.replace(before, after, 1))
        write(root.parent / "mutation.json", {"scope": "synthetic local fault; candidate source is unchanged",
              "candidate_revision": git(candidate, "HEAD"), "file": filename,
              "original_sha256": original_digest, "mutated_sha256": sha(path), "before": before, "after": after})
        measured = native(candidate, suite, output / name / "native", root)
        report = measured["report"]
        caught = measured["exit_status"] == 1 and report["outcome"] == "fail" and report["tests_failed"] > 0
        if not caught:
            raise ValueError("Frozen candidate gate did not catch " + name)
        results[name] = {"caught": caught, "failed_assertions": [row["assertion_id"]
            for row in report["results"] if row["outcome"] == "fail"]}
    return results


def suite_updates(candidate: Path, agreed: Path, reader: Path, output: Path) -> dict[str, Any]:
    updated = output / "metadata-update" / "suite"
    shutil.copytree(candidate / "reference-validator/byoi_suite", updated)
    manifest = json.loads((updated / "manifest.json").read_text())
    manifest["synthetic_update_control"] = "Metadata-only suite update; no assertions or expected results changed"
    write(updated / "manifest.json", manifest)
    updated_native = native(candidate, updated, output / "metadata-update" / "native")
    if not native_pass(updated_native, updated):
        raise ValueError("Candidate-native metadata update failed")
    refusal = reader_run(reader, updated, output / "metadata-update" / "reader-output",
                         output / "metadata-update" / "reader-refusal")
    if refusal["exit_status"] != 1 or "JEP manifest differs from the preregistered pin" not in refusal["stderr"]:
        raise ValueError("Pinned reader did not refuse changed suite bytes")

    # Deliberately poisoned candidate expectations are a negative control, never an agreement update.
    weakened = output / "weakened-expectations" / "suite"
    shutil.copytree(agreed, weakened)
    manifest = json.loads((weakened / "manifest.json").read_text())
    fault_report = json.loads((output.parent / "faults/duplicate-admission/native/report.json").read_text())
    failed = {row["assertion_id"]: row for row in fault_report["results"] if row["outcome"] == "fail"}
    altered = []
    for case in manifest["assertions"]:
        if case["assertion_id"] not in failed:
            continue
        actual = failed[case["assertion_id"]]["observations"][0]["result"]
        previous = case["expected"]
        case["expected"] = {key: (actual["errors"][0]["code"] if key == "error_code" else actual[key])
                            for key in previous}
        altered.append({"assertion_id": case["assertion_id"], "original_expected": previous,
                        "weakened_expected": case["expected"]})
    if not altered:
        raise ValueError("No duplicate-admission expectation was weakened")
    write(weakened / "manifest.json", manifest)
    write(output / "weakened-expectations/control.json", {"scope": "synthetic expectation poisoning only",
                                                           "altered_assertions": altered})
    package = output.parent / "faults/duplicate-admission/package"
    hidden = native(candidate, weakened, output / "weakened-expectations/native", package)
    if not native_pass(hidden, weakened):
        raise ValueError("Expectation-poisoning control did not isolate the intended regression")
    return {"metadata_only_candidate_suite_update_passes": True,
            "pinned_reader_refuses_mismatched_manifest": True,
            "weakened_current_expectations_hide_duplicate_fault": True,
            "frozen_agreed_gate_still_catches_duplicate_fault": True,
            "altered_expectations": len(altered),
            "approval_scope": "Synthetic controls, not maintainer review or a new agreed reader protocol"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--agreed", type=Path, required=True)
    parser.add_argument("--reader", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate, agreed, reader, output = (path.resolve() for path in
        (args.candidate, args.agreed, args.reader, args.output))
    output.mkdir(parents=True, exist_ok=False)
    suite = agreed / "reference-validator/byoi_suite"
    current_suite = candidate / "reference-validator/byoi_suite"
    try:
        if git(agreed, "HEAD") != AGREED_REVISION or git(reader, "HEAD") != READER_REVISION:
            raise ValueError("Agreed suite or reader checkout differs from its published pin")
        if sha(suite / "manifest.json") != MANIFEST_DIGEST:
            raise ValueError("Agreed suite manifest differs from its published pin")
        candidate_revision = git(candidate, "HEAD")
        if os.environ.get("EVENT_SHA") and candidate_revision != os.environ["EVENT_SHA"]:
            raise ValueError("Candidate checkout differs from the event SHA")
        before = tracked_files(candidate, "reference-validator")
        shutil.copyfile(candidate / "LICENSE", output / "CANDIDATE-LICENSE")
        shutil.copyfile(candidate / "LICENSING.md", output / "CANDIDATE-LICENSING.md")
        shutil.copyfile(reader / "LICENSE", output / "READER-LICENSE")
        identity = {"candidate_revision": candidate_revision, "candidate_tree": git(candidate, "HEAD^{tree}"),
                    "agreed_suite_revision": AGREED_REVISION, "reader_revision": READER_REVISION,
                    "candidate_files": before, "agreed_suite_files": tracked_files(agreed, "reference-validator/byoi_suite"),
                    "reader_files": tracked_files(reader, "interop/jep-core07-reader"),
                    "runner_sha256": sha(Path(__file__)),
                    "controller": os.environ.get("GITHUB_ACTOR", "author-operated local preflight"),
                    "executor": "GitHub Actions hosted runner" if os.environ.get("GITHUB_ACTIONS") else "local Python",
                    "event": {key: os.environ.get(key) for key in
                        ("EVENT_SHA", "PR_HEAD_SHA", "GITHUB_REPOSITORY", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT")}}
        write(output / "sources.json", identity)
        fixed = native(candidate, suite, output / "native-agreed")
        current = native(candidate, current_suite, output / "native-current-suite")
        separate = reader_run(reader, suite, output / "reader-agreed", output / "reader-logs")
        reader_report = json.loads((output / "reader-agreed/report.json").read_text())
        wanted = {"validation": {"total": 25, "passed": 25}, "producer": {"total": 4, "passed": 4},
                  "acceptance": {"total": 8, "passed": 8}}
        measured_faults = faults(candidate, suite, output / "faults")
        measured_updates = suite_updates(candidate, suite, reader, output / "suite-updates")
        candidate_unchanged = before == tracked_files(candidate, "reference-validator")
        passed = (native_pass(fixed, suite) and native_pass(current, current_suite)
                  and separate["exit_status"] == 0 and reader_report["summary"] == wanted and candidate_unchanged)
        summary = {"passed": passed, "candidate_frozen": {key: fixed["report"][key] for key in
                        ("tests_passed", "tests_failed", "tests_unsupported", "tests_not_selected")},
                   "candidate_current_suite": {key: current["report"][key] for key in
                        ("tests_passed", "tests_failed", "tests_unsupported", "tests_not_selected")},
                   "pinned_reader_agreed": reader_report["summary"], "faults": measured_faults,
                   "suite_update_controls": measured_updates, "candidate_source_unchanged": candidate_unchanged,
                   "scope": "Author-operated finite fixtures and synthetic fault controls; required host adoption pending"}
        write(output / "summary.json", summary)
        print(json.dumps(summary))
        return 0 if passed else 1
    except Exception as error:
        write(output / "failure.json", {"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        inventory = {str(path.relative_to(output)): {"bytes": path.stat().st_size, "sha256": sha(path)}
                     for path in sorted(output.rglob("*")) if path.is_file()}
        write(output / "ARTIFACT-MANIFEST.json", inventory)


if __name__ == "__main__":
    raise SystemExit(main())
