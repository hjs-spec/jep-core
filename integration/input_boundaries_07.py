"""Cross-implementation hostile-input checks for the current baseline only.

Every case is signed with a disposable synthetic key. Malformed protected headers
are signed as their original bytes, not repaired/re-encoded before verification.
This checks format and acceptance-state behavior, not actor trust or domain policy.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run(workspace):
    sys.path.insert(0, str(workspace / "jep-api"))
    sys.path.insert(0, str(workspace / "jep-agent-sdk"))
    from jep_agent.core.verifier import JEPVerifier

    core = load("boundary_core07", ROOT / "reference-validator/jep_validate_07.py")
    key = Ed25519PrivateKey.generate()
    public = key.public_key()
    kid = "urn:example:disposable-input-boundary-key"
    keys = {kid: {"kty": "OKP", "crv": "Ed25519", "x": core.b64u(
        public.public_bytes(Encoding.Raw, PublicFormat.Raw))}}
    header = json.dumps({"alg": "Ed25519", "kid": kid}).encode("utf-8")
    base = {"jep": "1", "id": "boundary", "verb": "J",
            "who": "did:example:input-boundary", "when": 1700000000,
            "what": {"claim": "synthetic format test"}}

    def signed(event, protected_bytes=header):
        unsigned = {k: v for k, v in event.items() if k != "sig"}
        protected = core.b64u(protected_bytes)
        signing_input = (protected + "." + core.b64u(core.canonicalize(unsigned))).encode("ascii")
        signature = key.sign(signing_input)
        public.verify(signature, signing_input)
        return {**copy.deepcopy(unsigned), "sig": protected + ".." + core.b64u(signature)}

    cases = []

    def add(name, *, patch=None, raw=header, check=None):
        event = {**copy.deepcopy(base), "id": name}
        cases.append((name, signed({**event, **(patch or {})}, raw), signed(event), check))

    add("valid-utf8")
    add("valid-noncanonical-header", raw=json.dumps(
        {"note": {"text": "合法 UTF-8", "number": 1e20}, "kid": kid, "alg": "Ed25519"},
        ensure_ascii=False, indent=2).encode("utf-8"))
    add("valid-empty-optional-members", patch={"ext": {}, "ext_crit": []})
    add("valid-unknown-noncritical-extension", patch={"ext": {"urn:example:note": {}}})
    add("empty-extension-name", patch={"ext": {"": {}}}, check="syntax")
    digest = "sha256:" + "a" * 64
    add("what-digest-newline", patch={"what": digest + "\n"}, check="syntax")
    add("ref-digest-newline", patch={"ref": digest + "\n"}, check="syntax")
    add("ref-hash-newline", patch={"ref": {"type": "evidence", "value": "demo", "hash": digest + "\n"}}, check="syntax")
    add("other-digest-newline", patch={"what": "other:aa\n"}, check="syntax")
    for encoding in ("utf-16", "utf-16-le", "utf-16-be", "utf-32", "utf-32-le", "utf-32-be"):
        add("header-" + encoding, raw=header.decode().encode(encoding), check="cryptographic")
    for name, suffix in {
        "surrogate-value": b',"extra":"\\ud800"}',
        "surrogate-nested-key": b',"extra":{"\\udfff":true}}',
        "overflow-number": b',"extra":1e400}',
        "nan": b',"extra":NaN}',
        "infinity": b',"extra":Infinity}',
        "duplicate-member": b',"extra":1,"extra":2}',
        "duplicate-nested-member": b',"extra":{"x":1,"x":2}}',
        "b64-false": b',"b64":false}',
        "critical-header": b',"crit":["extra"],"extra":true}',
    }.items():
        add("header-" + name, raw=header[:-1] + suffix, check="cryptographic")
    add("header-invalid-utf8", raw=header[:-1] + b',"extra":"\xff"}', check="cryptographic")

    report = {"profile": "jep-core-0.7", "status": "running", "cases": [],
              "scope": "Core/API/Agent baseline archival and acceptance rejection; no external effects"}
    with tempfile.TemporaryDirectory(prefix="jep07-input-boundaries-") as directory:
        root = Path(directory)
        previous = os.environ.get("JEP_STATE_DIR")
        os.environ["JEP_STATE_DIR"] = str(root / "api")
        try:
            api = load("boundary_api07", workspace / "jep-api/main.py")
        finally:
            if previous is None:
                os.environ.pop("JEP_STATE_DIR", None)
            else:
                os.environ["JEP_STATE_DIR"] = previous
        for key_id, jwk in keys.items():
            api.STATE.register_public_key(key_id, jwk)
        result_schema = Draft202012Validator(core.load_json(ROOT / "schemas/jep-validation-result.schema.json"))
        schemas = [Draft202012Validator(core.load_json(ROOT / "schemas/jep-event.schema.json")), api.SCHEMA_07]
        for index, (name, event, recovery, failed_check) in enumerate(cases):
            item = {"name": name, "expected": "invalid" if failed_check else "valid", "results": {}, "problems": []}
            if failed_check == "syntax":
                for schema in schemas:
                    if schema.is_valid(event):
                        item["problems"].append("structural schema accepted malformed event")
            verifier = JEPVerifier()
            state = root / f"core-{index}.json"
            engines = {
                "core": lambda e, mode: core.validate_event(e, keys=keys, mode=mode, acceptance_state=state),
                "api": lambda e, mode: api.validate_event_07(e, mode=mode),
                "agent": lambda e, mode: verifier.verify_result(e, public, mode=mode),
            }
            for label, verify in engines.items():
                outcomes = {}
                for mode in ("archival", "acceptance"):
                    result = verify(copy.deepcopy(event), mode)
                    result_schema.validate(result)
                    outcomes[mode] = {"status": result["status"], "errors": result["errors"],
                                      "acceptance": result.get("acceptance")}
                    if result["status"] != item["expected"]:
                        item["problems"].append(f"{label}/{mode}: unexpected status")
                    if failed_check:
                        if result["checks"][failed_check] != "fail":
                            item["problems"].append(f"{label}/{mode}: wrong failed check")
                        if not any(e.get("check") == failed_check for e in result["errors"]):
                            item["problems"].append(f"{label}/{mode}: wrong diagnostic category")
                        if mode == "acceptance" and result.get("acceptance") != {"outcome": "rejected", "effect_applied": False}:
                            item["problems"].append(f"{label}: rejected input applied an effect")
                    elif result["event_hash"] != core.event_hash(event):
                        item["problems"].append(f"{label}/{mode}: signed artifact changed")
                if failed_check:
                    first = verify(copy.deepcopy(recovery), "acceptance")
                    retry = verify(copy.deepcopy(recovery), "acceptance")
                    if first.get("acceptance") != {"outcome": "accepted", "effect_applied": True}:
                        item["problems"].append(f"{label}: rejection consumed the event identity")
                    if retry.get("acceptance") != {"outcome": "already_accepted", "effect_applied": False}:
                        item["problems"].append(f"{label}: corrected event retry was not idempotent")
                    outcomes["recovery"] = [first.get("acceptance"), retry.get("acceptance")]
                item["results"][label] = outcomes
            report["cases"].append(item)
    report["case_count"] = len(cases)
    report["failed_cases"] = sum(bool(case["problems"]) for case in report["cases"])
    report["status"] = "fail" if report["failed_cases"] else "pass"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT.parent)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = run(args.workspace.resolve())
    text = json.dumps(report, indent=2)
    if args.report:
        args.report.write_text(text + "\n", encoding="utf-8")
    print(text)
    raise SystemExit(bool(report["failed_cases"]))
