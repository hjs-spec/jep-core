"""Reproduce public synthetic BYOI fixtures; never use these keys in production.

Uses RFC8785 plus cryptography directly, not the reference validator as an oracle.
Expected outcomes are derived from the named specification sections.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path

import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parents[1] / "reference-validator/byoi_suite"
CORE = "draft-wang-jep-judgment-event-protocol-07"
CONF = "draft-wang-jep-conformance-02"


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def build(root=ROOT):
    root.mkdir(parents=True, exist_ok=True)
    files = {}

    def put(path, value, raw=False):
        data = value.encode() if raw else (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        files[path] = "sha256:" + hashlib.sha256(data).hexdigest()
        return path

    # Public test seeds, deliberately fixed and reproducible.
    private = {f"byoi-key-{i}": Ed25519PrivateKey.from_private_bytes(bytes([i]) * 32) for i in (1, 2)}
    keys = {kid: {"kty": "OKP", "crv": "Ed25519", "x": b64(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))}
            for kid, key in private.items()}
    put("keys.json", keys)
    put("empty-keys.json", {})

    def sign(unsigned, kid="byoi-key-1", header=None):
        event = copy.deepcopy(unsigned)
        protected = b64(json.dumps(header or {"alg": "Ed25519", "kid": kid}, separators=(",", ":")).encode())
        payload = b64(rfc8785.dumps(event))
        event["sig"] = protected + ".." + b64(private[kid].sign((protected + "." + payload).encode()))
        return event

    def source(section, document=CORE):
        return [{"document": document, "section": section}]

    assertions = []
    signed = {}
    for verb in "JDTV":
        unsigned = {"jep": "1", "id": f"urn:example:byoi:{verb}", "verb": verb,
                    "who": "example:byoi-actor", "when": 1790726400, "what": {"claim": "approve-result"}}
        if verb == "D":
            unsigned["what"] = {"delegatee": "example:delegatee", "scope": "review-result"}
        if verb in "TV":
            unsigned["ref"] = {"type": "jep:event", "value": {"who": "example:byoi-actor", "id": "urn:example:byoi:J"}}
        if verb == "T":
            unsigned["what"] = {"termination_scope": "delegation"}
        if verb == "V":
            unsigned["what"] = {"verification_scope": "cryptographic", "result": "pass"}
        signed[verb] = sign(unsigned)
        put(f"templates/{verb}.json", unsigned)

    def case(identifier, name, value, status, checks, section, *, raw=False, keyfile="keys.json", error=None):
        path = put(f"vectors/{name}.json", value, raw)
        expected = {"status": status, "checks": checks}
        if status == "valid":
            expected["event_hash"] = "sha256:" + hashlib.sha256(rfc8785.dumps(value)).hexdigest()
            expected["event_identity"] = {"who": value["who"], "id": value["id"]}
        if error:
            expected["error_code"] = error
        assertions.append({"assertion_id": identifier, "name": name, "requirements": source(section),
                           "input": path, "keys": keyfile, "mode": "archival", "profile": "jep-core-0.7",
                           "expected": expected})

    valid = {"syntax": "pass", "cryptographic": "pass", "event_identity": "pass", "extension_processing": "pass"}
    for i, verb in enumerate("JDTV", 1):
        case(f"JEP-A-VERB-{i:03}", f"{verb}-basic", signed[verb], "valid", valid, f"8.{i}")
    array_v = {k: copy.deepcopy(v) for k, v in signed['V'].items() if k != 'sig'}
    array_v['what']['verification_scope'] = ['cryptographic']
    case('JEP-A-VERB-005', 'V-array-scope', sign(array_v), 'valid', valid, '8.4')

    base = {k: v for k, v in signed["J"].items() if k != "sig"}
    syntax_cases = [("missing-id", {k: v for k, v in signed['J'].items() if k != 'id'}, "7.2"),
                    ("empty-id", {**signed['J'], "id": ""}, "7.2"),
                    ("unknown-verb", {**signed['J'], "verb": "X"}, "7.3"),
                    ("invalid-timestamp", {**signed['J'], "when": "1790726400"}, "7.5")]
    for verb, field in [("D", "delegatee"), ("D", "scope"), ("T", "termination_scope"),
                        ("V", "verification_scope"), ("V", "result")]:
        event = copy.deepcopy(signed[verb]); del event['what'][field]
        syntax_cases.append((f"{verb}-missing-{field}", event, f"8.{'JDTV'.index(verb)+1}"))
    for verb in "TV":
        event = copy.deepcopy(signed[verb]); del event['ref']
        syntax_cases.append((f"{verb}-missing-ref", event, f"8.{'JDTV'.index(verb)+1}"))
    for i, (name, event, section) in enumerate(syntax_cases, 1):
        case(f"JEP-A-SYN-{i:03}", name, event, "invalid", {"syntax": "fail"}, section)
    case("JEP-A-SYN-012", "duplicate-member", '{"id":"a","id":"b"}', "invalid",
         {"syntax": "fail"}, "6", raw=True, error="ERR_DUPLICATE_MEMBER")
    case("JEP-A-SYN-013", "invalid-json", '{', "invalid", {"syntax": "fail"}, "6", raw=True)
    case("JEP-A-SIG-001", "tampered-claim", {**signed['J'], "what": {"claim": "changed"}}, "invalid",
         {"syntax": "pass", "cryptographic": "fail"}, "12", error="ERR_SIGNATURE_INVALID")
    case("JEP-A-SIG-002", "unresolved-key", signed['J'], "indeterminate", {"cryptographic": "indeterminate"},
         "15.2", keyfile="empty-keys.json")
    case("JEP-A-SIG-003", "unsupported-algorithm", sign(base, header={"alg": "none", "kid": "byoi-key-1"}),
         "invalid", {"cryptographic": "fail"}, "23.4")
    case("JEP-A-EXT-001", "unknown-critical", sign({**base, "ext": {"example.byoi.unknown": {}},
         "ext_crit": ["example.byoi.unknown"]}), "invalid", {"cryptographic": "pass", "extension_processing": "fail"},
         "18", error="ERR_UNKNOWN_CRITICAL_EXTENSION")
    case("JEP-A-EXT-002", "unknown-noncritical", sign({**base, "ext": {"example.byoi.unknown": {"x": 1}}}),
         "valid", valid, "18")
    case("JEP-A-JCS-001", "unicode-numbers", sign({**base, "what": {"\U0001f600": "emoji", "\ue000": "bmp",
         "values": [1.0, 1e-7, 1e20, -0.0], "text": "<>&"}}), "valid", valid, "12")
    # Raw formatting/order changes preserve signing input and Event Hash.
    event = signed['J']
    path = put("vectors/J-reordered.json", json.dumps(dict(reversed(list(event.items()))), separators=(',', ':')), True)
    assertions.append({"assertion_id": "JEP-A-JCS-002", "name": "wire-reordered", "requirements": source("12"),
                       "input": path, "keys": "keys.json", "mode": "archival", "profile": "jep-core-0.7",
                       "expected": copy.deepcopy(assertions[0]['expected'])})

    put("stateful/conflict.json", sign({**base, "what": {"claim": "different"}}))
    put("stateful/resigned.json", sign(base, kid="byoi-key-2"))
    put("stateful/other-actor.json", sign({**base, "who": "example:other-actor"}))
    acceptance = []

    def step(path="vectors/J-basic.json", outcome="accepted", effects=1, *, mode="acceptance", domain="a", status="valid"):
        expected = {"status": status}
        if mode == "acceptance":
            expected['acceptance'] = {"outcome": outcome, "effect_applied": outcome == "accepted"}
        return {"operation": "validate", "input": path, "mode": mode, "acceptance_domain": domain,
                "expected": expected, "expected_effect_count": effects}

    def state_case(i, name, steps, section="9"):
        acceptance.append({"assertion_id": f"JEP-A-ACC-{i:03}", "name": name, "requirements": source(section),
                           "initial_state": "empty", "state_scope": "per-assertion", "steps": steps})

    state_case(1, "archival-safe-retry-process-restart", [step(mode="archival", effects=0), step(),
               step(mode="archival", effects=1), step(outcome="already_accepted")])
    state_case(2, "conflicting-reuse", [step(), step("stateful/conflict.json", "rejected", status="invalid")])
    state_case(3, "resigned-same-content", [step(), step("stateful/resigned.json", "already_accepted")])
    state_case(4, "same-id-different-actor", [step(), step("stateful/other-actor.json", effects=2)])
    state_case(5, "separate-acceptance-domains", [step(), step(domain="b"), step(outcome="already_accepted")])
    state_case(6, "rejection-does-not-consume-identity", [step("vectors/tampered-claim.json", "rejected", 0, status="invalid"), step()])
    state_case(7, "concurrent-delivery", [{"operation": "concurrent", "input": "vectors/J-basic.json",
               "deliveries": 8, "acceptance_domain": "a", "expected_effect_count": 1}], "9.4")
    state_case(8, "unavailable-state", [{"operation": "set_state_availability", "available": False},
               step(outcome="indeterminate", effects=0, status="indeterminate"),
               {"operation": "set_state_availability", "available": True}, step()], "23.3")

    coverage = {"complete_core_coverage": False, "basis": "Scoped executable assertions; not a complete normative inventory",
                "covered": ["J/D/T/V minimum fields", "selected malformed JSON and signature cases", "unknown critical extension",
                            "selected JCS/hash cases", "identity/retry/concurrency/state-unavailable acceptance scenarios"],
                "partially_covered": ["I-JSON/JCS input domain", "producer behavior beyond submitted templates",
                                      "acceptance durability: fresh processes, not power-loss or distributed failover"],
                "out_of_scope": ["reference resolution and exact-artifact pin verification", "actor/key trust establishment",
                                 "freshness/audience profiles", "profile composition and downgrade", "chain/policy semantics",
                                 "real-world truth, legal validity, production security"],
                "not_machine_testable_at_core": ["external target facts"]}
    put("coverage.json", coverage)
    put("report.schema.json", json.loads((Path(__file__).resolve().parents[1] / 'schemas/jep-byoi-report.schema.json').read_text()))
    manifest = {"name": "jep-core-0.7-byoi", "version": "1.0.0", "jep_core": "0.7", "wire_major": "1",
                "conformance_draft": CONF, "signature_class": "JEP-Baseline-Ed25519-JWS-JCS-0.7",
                "adapter_protocol": "jep-byoi/1", "files": dict(sorted(files.items())), "assertions": assertions,
                "producer_assertions": [{"assertion_id": f"JEP-A-PRO-{i:03}", "template": f"templates/{verb}.json",
                                         "requirements": source("19.1")} for i, verb in enumerate("JDTV", 1)],
                "acceptance_assertions": acceptance}
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"BYOI suite: {len(assertions)} verifier, 4 producer, {len(acceptance)} acceptance assertions")


if __name__ == "__main__":
    build()
