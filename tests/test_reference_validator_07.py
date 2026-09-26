from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "reference-validator" / "jep_validate_07.py"
VECTORS = ROOT / "test-vectors" / "0.7"
KEYS = VECTORS / "keys.json"


def run(*args: str):
    p = subprocess.run(
        [sys.executable, str(VALIDATOR), *map(str, args)],
        cwd=ROOT, text=True, capture_output=True, check=False,
    )
    try:
        data = json.loads(p.stdout)
    except Exception as exc:
        raise AssertionError(f"non-JSON validator output: {p.stdout!r} {p.stderr!r}") from exc
    return p, data


def test_manifest_07():
    p, out = run("run-tests", ROOT / "test-manifest-0.7.json")
    assert p.returncode == 0, p.stderr + p.stdout
    assert out["failed"] == 0
    assert out["passed"] == len(out["details"])


def test_valid_v_reports_independent_checks():
    p, out = run("validate", VECTORS / "valid" / "V-basic.json", "--keys", KEYS, "--trust-profile", "inline")
    assert p.returncode == 0
    assert out["status"] == "valid"
    assert out["checks"]["syntax"] == "pass"
    assert out["checks"]["cryptographic"] == "pass"
    assert out["checks"]["actor_binding"] == "pass"
    assert "level" not in out


def test_safe_retry_is_valid_not_error(tmp_path: Path):
    state = tmp_path / "acceptance.json"
    args = [
        "validate", VECTORS / "valid" / "J-basic.json", "--keys", KEYS,
        "--trust-profile", "inline", "--mode", "acceptance",
        "--acceptance-state", state,
    ]
    p1, first = run(*args)
    p2, second = run(*args)
    assert p1.returncode == 0 and p2.returncode == 0
    assert first["acceptance"] == {"outcome": "accepted", "effect_applied": True}
    assert second["acceptance"] == {"outcome": "already_accepted", "effect_applied": False}
    assert second["status"] == "valid"


def test_event_identity_conflict_is_rejected(tmp_path: Path):
    state = tmp_path / "acceptance.json"
    common = ["--keys", KEYS, "--trust-profile", "inline", "--mode", "acceptance", "--acceptance-state", state]
    p1, _ = run("validate", VECTORS / "valid" / "J-basic.json", *common)
    p2, conflict = run("validate", VECTORS / "acceptance" / "J-conflict.json", *common)
    assert p1.returncode == 0
    assert p2.returncode == 1
    assert conflict["status"] == "invalid"
    assert conflict["errors"][0]["code"] == "ERR_EVENT_ID_CONFLICT"
    assert conflict["acceptance"]["effect_applied"] is False
