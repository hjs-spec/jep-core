#!/usr/bin/env python3
"""Reference validator for JEP Core 0.7.

This validator implements the repository baseline signature class and the
Core 0.7 identity/acceptance model. It intentionally does not implement
chain, policy, legal, factual, or domain semantics.

Pre-0.7 artifacts belong to jep_validate.py (legacy 0.6 compatibility).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence

import rfc8785
from nacl.signing import VerifyKey

CORE_PROFILE = "jep-core-0.7"
BASELINE_CLASS = "JEP-Baseline-Ed25519-JWS-JCS-0.7"
WIRE_VERSION = "1"
VERBS = {"J", "D", "T", "V"}
CHECKS = (
    "syntax", "cryptographic", "actor_binding", "freshness", "audience",
    "event_identity", "reference_integrity", "extension_processing",
    "chain_integrity", "policy",
)
TOP_LEVEL_FIELDS = {
    "jep", "id", "verb", "who", "when", "what", "aud", "ref",
    "ext", "ext_crit", "sig",
}
DIGEST_RE = __import__("re").compile(r"^[a-z0-9][a-z0-9-]*:[0-9a-f]+$")
B64U_RE = __import__("re").compile(r"^[A-Za-z0-9_-]*$")
SAFE_INTEGER_MAX = 2**53 - 1
CRITICAL_EXTENSION_HANDLERS: dict[str, Any] = {}


class DuplicateKeyError(ValueError):
    pass


class Fault(Exception):
    def __init__(self, code: str, message: str, check: str = "syntax", *, indeterminate: bool = False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.check = check
        self.indeterminate = indeterminate

    def diagnostic(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "check": self.check}


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKeyError(f"duplicate JSON member: {key}")
        out[key] = value
    return out


def _reject_constant(value: str):
    raise ValueError(f"non-JSON numeric constant: {value}")


def _validate_i_json(value: Any, path: str = "$") -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        _binary64_numbers(value)
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{path}: non-finite number")
        return
    if isinstance(value, str):
        value.encode("utf-8", errors="strict")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _validate_i_json(item, f"{path}[{i}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path}: non-string member name")
            _validate_i_json(key, f"{path}.<key>")
            _validate_i_json(item, f"{path}.{key}")
        return
    raise ValueError(f"{path}: unsupported JSON value")


def parse_json(text: str) -> Any:
    value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
    _validate_i_json(value)
    return value


def load_json(path: str | Path) -> Any:
    try:
        return parse_json(Path(path).read_text(encoding="utf-8", errors="strict"))
    except DuplicateKeyError as exc:
        raise Fault("ERR_DUPLICATE_MEMBER", str(exc), "syntax") from exc
    except Exception as exc:
        if isinstance(exc, Fault):
            raise
        raise Fault("ERR_INVALID_JSON", f"invalid JSON: {exc}", "syntax") from exc


def _binary64_numbers(value):
    """Adapt integer tokens to their preserved JCS binary64 value.

    JSON.stringify(1e20) emits an integer token. Parsing that token into a
    Python int must not invalidate that number. Accept an exact binary64
    integer or its canonical shortest decimal spelling, which can differ
    (1000000000000000100 represents the float 1000000000000000128).
    Other precision-losing integers remain rejected. Never edit the input.
    """
    if type(value) is int and abs(value) > 2**53 - 1:
        try:
            number = float(value)
            if not math.isfinite(number):
                raise ValueError("Integer exceeds binary64 range")
            if int(number) != value and rfc8785.dumps(number) != str(value).encode("ascii"):
                raise ValueError("Integer is neither exact binary64 nor its canonical JCS spelling")
        except OverflowError as exc:
            raise ValueError("Integer exceeds binary64 range") from exc
        return number
    if isinstance(value, dict):
        return {key: _binary64_numbers(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_binary64_numbers(item) for item in value]
    return value


def canonicalize(value: Any) -> bytes:
    try:
        return rfc8785.dumps(_binary64_numbers(value))
    except Exception as exc:
        raise Fault("ERR_CANONICALIZATION_FAILED", str(exc), "cryptographic") from exc


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def b64u_decode(value: str, label: str) -> bytes:
    if not isinstance(value, str) or not B64U_RE.fullmatch(value):
        raise Fault("ERR_SIGNATURE_CONTAINER_INVALID", f"{label} is not unpadded base64url", "cryptographic")
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        if b64u(raw) != value:
            raise ValueError("non-canonical base64url")
        return raw
    except Exception as exc:
        raise Fault("ERR_SIGNATURE_CONTAINER_INVALID", f"invalid {label}: {exc}", "cryptographic") from exc


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonicalize(value)).hexdigest()


def payload_digest(event: Mapping[str, Any]) -> str:
    return digest({k: v for k, v in event.items() if k != "sig"})


def event_hash(event: Mapping[str, Any]) -> str:
    return digest(dict(event))


def _require(condition: bool, code: str, message: str, check: str = "syntax") -> None:
    if not condition:
        raise Fault(code, message, check)


def _validate_digest(value: Any, field: str) -> None:
    _require(isinstance(value, str) and bool(DIGEST_RE.fullmatch(value)),
             "ERR_INVALID_FIELD_TYPE", f"{field} must be an algorithm-tagged lowercase-hex digest")
    alg, hexdigest = value.split(":", 1)
    if alg == "sha256":
        _require(len(hexdigest) == 64, "ERR_INVALID_FIELD_TYPE", f"{field} SHA-256 digest must be 64 hex chars")


def _validate_ref(value: Any, field: str = "ref") -> None:
    if isinstance(value, str):
        _validate_digest(value, field)
        return
    _require(isinstance(value, dict), "ERR_INVALID_FIELD_TYPE", f"{field} must be a digest or typed reference object")
    _require("type" in value and "value" in value, "ERR_MISSING_REQUIRED_FIELD", f"{field} requires type and value")
    _require(isinstance(value["type"], str) and bool(value["type"]), "ERR_INVALID_FIELD_TYPE", f"{field}.type must be non-empty")
    if value["type"] == "jep:event":
        ident = value["value"]
        _require(isinstance(ident, dict), "ERR_INVALID_FIELD_TYPE", f"{field}.value must contain event identity")
        _require(set(ident) == {"who", "id"}, "ERR_INVALID_FIELD_TYPE", f"{field}.value must contain exactly who and id")
        _require(isinstance(ident["who"], str) and bool(ident["who"]), "ERR_INVALID_FIELD_TYPE", f"{field}.value.who invalid")
        _require(isinstance(ident["id"], str) and bool(ident["id"]), "ERR_INVALID_FIELD_TYPE", f"{field}.value.id invalid")
    if "hash" in value:
        _validate_digest(value["hash"], f"{field}.hash")


def validate_shape(event: Any) -> Mapping[str, Any]:
    _require(isinstance(event, dict), "ERR_INVALID_FIELD_TYPE", "event must be an object")
    try:
        _validate_i_json(event)
    except (TypeError, ValueError) as exc:
        raise Fault("ERR_INVALID_JSON", str(exc), "syntax") from exc
    unknown = sorted(set(event) - TOP_LEVEL_FIELDS)
    _require(not unknown, "ERR_INVALID_FIELD_TYPE", f"unknown top-level member(s): {', '.join(unknown)}")
    for name in ("jep", "id", "verb", "who", "when", "what"):
        _require(name in event, "ERR_MISSING_REQUIRED_FIELD", f"missing required field: {name}")
    if "sig" not in event:
        raise Fault("ERR_SIGNATURE_MISSING", "missing required field: sig", "cryptographic")

    _require(event["jep"] == WIRE_VERSION, "ERR_UNSUPPORTED_JEP_VERSION", "jep must be '1'")
    _require(isinstance(event["id"], str) and bool(event["id"]) and event["id"].isascii(),
             "ERR_EVENT_ID_INVALID", "id must be a non-empty ASCII string")
    _require(isinstance(event["verb"], str) and event["verb"] in VERBS,
             "ERR_UNKNOWN_VERB", "verb must be J, D, T, or V")
    _require(isinstance(event["who"], str) and bool(event["who"]), "ERR_INVALID_FIELD_TYPE", "who must be non-empty")
    _require(isinstance(event["when"], int) and not isinstance(event["when"], bool), "ERR_INVALID_TIMESTAMP", "when must be integer")
    _require(abs(event["when"]) <= SAFE_INTEGER_MAX, "ERR_INVALID_TIMESTAMP", "when exceeds interoperable integer range")
    _require(isinstance(event["what"], (dict, str)), "ERR_INVALID_FIELD_TYPE", "what must be object or permitted digest")
    if isinstance(event["what"], str):
        _validate_digest(event["what"], "what")
    elif not event["what"]:
        raise Fault("ERR_INVALID_FIELD_TYPE", "what object must not be empty")

    if "aud" in event:
        _require(isinstance(event["aud"], str) and bool(event["aud"]), "ERR_INVALID_FIELD_TYPE", "aud must be non-empty")
    if "ref" in event:
        _validate_ref(event["ref"])
    if "ext" in event:
        _require(isinstance(event["ext"], dict), "ERR_INVALID_FIELD_TYPE", "ext must be object")
        for ext_id, body in event["ext"].items():
            _require(isinstance(ext_id, str) and bool(ext_id), "ERR_INVALID_FIELD_TYPE", "extension id invalid")
            _require(isinstance(body, dict), "ERR_INVALID_FIELD_TYPE", f"extension {ext_id} must be object")
    if "ext_crit" in event:
        crit = event["ext_crit"]
        _require(isinstance(crit, list) and all(isinstance(x, str) and bool(x) for x in crit)
                 and len(crit) == len(set(crit)), "ERR_INVALID_FIELD_TYPE", "ext_crit must be a unique string array")
    _require(isinstance(event["sig"], str) and bool(event["sig"]),
             "ERR_SIGNATURE_CONTAINER_INVALID", "baseline sig must be detached compact JWS", "cryptographic")

    verb, what = event["verb"], event["what"]
    if verb == "D":
        _require(isinstance(what, dict), "ERR_INVALID_FIELD_TYPE", "D what must be object")
        _require("delegatee" in what, "ERR_MISSING_REQUIRED_FIELD", "D requires what.delegatee")
        _require("scope" in what, "ERR_MISSING_REQUIRED_FIELD", "D requires what.scope")
        _require(isinstance(what["delegatee"], str) and bool(what["delegatee"]), "ERR_INVALID_FIELD_TYPE", "what.delegatee invalid")
    elif verb == "T":
        _require("ref" in event, "ERR_MISSING_REQUIRED_FIELD", "T requires ref")
        _require(isinstance(what, dict), "ERR_INVALID_FIELD_TYPE", "T what must be object")
        _require("termination_scope" in what, "ERR_MISSING_REQUIRED_FIELD", "T requires what.termination_scope")
        _require(isinstance(what["termination_scope"], str) and bool(what["termination_scope"]),
                 "ERR_INVALID_FIELD_TYPE", "termination_scope invalid")
    elif verb == "V":
        _require("ref" in event, "ERR_MISSING_REQUIRED_FIELD", "V requires ref")
        _require(isinstance(what, dict), "ERR_INVALID_FIELD_TYPE", "V what must be object")
        for name in ("verification_scope", "result"):
            _require(name in what, "ERR_MISSING_REQUIRED_FIELD", f"V requires what.{name}")
        scopes = what["verification_scope"]
        # Published Conformance -02 section 9.4 uses a single scope string.
        # Preserve the list representation used by existing signed 0.7 fixtures.
        _require((isinstance(scopes, str) and bool(scopes)) or
                 (isinstance(scopes, list) and bool(scopes)
                  and all(isinstance(x, str) and bool(x) for x in scopes)
                  and len(scopes) == len(set(scopes))),
                 "ERR_INVALID_FIELD_TYPE", "verification_scope must be a non-empty string or unique string array")
    return event


def load_keys(path: str | Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    data = load_json(path)
    _require(isinstance(data, dict), "ERR_INVALID_FIELD_TYPE", "key file must be object")
    return data


def verify_jws(event: Mapping[str, Any], keys: Mapping[str, Mapping[str, Any]]) -> tuple[str, Mapping[str, Any]]:
    sig = event["sig"]
    parts = sig.split(".")
    _require(len(parts) == 3 and parts[1] == "", "ERR_SIGNATURE_CONTAINER_INVALID", "detached compact JWS must have empty payload segment", "cryptographic")
    protected, _, signature = parts
    try:
        header = parse_json(b64u_decode(protected, "protected header").decode("utf-8"))
    except Exception as exc:
        if isinstance(exc, Fault):
            raise
        raise Fault("ERR_SIGNATURE_CONTAINER_INVALID", f"invalid protected header: {exc}", "cryptographic") from exc
    _require(isinstance(header, dict), "ERR_SIGNATURE_CONTAINER_INVALID", "protected header must be object", "cryptographic")
    _require(header.get("alg") == "Ed25519", "ERR_UNSUPPORTED_SIGNATURE_ALG", "baseline requires Ed25519", "cryptographic")
    kid = header.get("kid")
    _require(isinstance(kid, str) and bool(kid), "ERR_SIGNATURE_CONTAINER_INVALID", "protected header requires kid", "cryptographic")
    if "crit" in header:
        raise Fault("ERR_SIGNATURE_CONTAINER_INVALID", "baseline implements no JOSE critical parameters", "cryptographic")
    _require(header.get("b64", True) is True, "ERR_SIGNATURE_CONTAINER_INVALID",
             "baseline requires base64url-encoded payload", "cryptographic")
    _require(isinstance(keys, Mapping), "ERR_KEY_UNRESOLVED", "key store must be a mapping", "cryptographic")
    jwk = keys.get(kid)
    if jwk is None:
        raise Fault("ERR_KEY_UNRESOLVED", f"no key for kid {kid}", "cryptographic", indeterminate=True)
    _require(isinstance(jwk, Mapping) and jwk.get("kty") == "OKP" and jwk.get("crv") == "Ed25519",
             "ERR_ALG_KEY_TYPE_MISMATCH", "Ed25519 requires OKP/Ed25519 JWK", "cryptographic")
    raw_key = b64u_decode(jwk.get("x"), "JWK x")
    raw_sig = b64u_decode(signature, "signature")
    unsigned = {k: v for k, v in event.items() if k != "sig"}
    signing_input = (protected + "." + b64u(canonicalize(unsigned))).encode("ascii")
    try:
        VerifyKey(raw_key).verify(signing_input, raw_sig)
    except Exception as exc:
        raise Fault("ERR_SIGNATURE_INVALID", "Ed25519 signature verification failed", "cryptographic") from exc
    return kid, jwk


def actor_binding(event: Mapping[str, Any], kid: str, jwk: Mapping[str, Any], profile: str) -> None:
    if profile == "none":
        return
    if profile == "kid-prefix":
        _require(kid.startswith(str(event["who"]) + "#"), "ERR_KEY_NOT_BOUND_TO_ACTOR", "kid is not bound to who", "actor_binding")
        return
    if profile == "inline":
        actors = jwk.get("actors")
        _require(isinstance(actors, list) and event["who"] in actors,
                 "ERR_KEY_NOT_BOUND_TO_ACTOR", "key is not bound to who", "actor_binding")
        return
    raise Fault("ERR_TRUST_PROFILE_UNSUPPORTED", f"unsupported local trust profile: {profile}", "actor_binding", indeterminate=True)


def process_extensions(event: Mapping[str, Any]) -> None:
    critical = event.get("ext_crit") or []
    ext = event.get("ext") or {}
    for ext_id in critical:
        if ext_id not in ext:
            raise Fault("ERR_EXTENSION_SCHEMA_INVALID", f"critical extension {ext_id} absent", "extension_processing")
        handler = CRITICAL_EXTENSION_HANDLERS.get(ext_id)
        if handler is None:
            raise Fault("ERR_UNKNOWN_CRITICAL_EXTENSION", f"unsupported critical extension: {ext_id}", "extension_processing")
        handler(ext[ext_id], event)


def _checks() -> dict[str, str]:
    return {name: "not_checked" for name in CHECKS}


def _result(status: str, mode: str, checks: Mapping[str, str], *, event=None, errors=(), acceptance=None, profile=CORE_PROFILE):
    artifact_hash = None
    if isinstance(event, dict) and "sig" in event:
        try:
            _validate_i_json(event)
            artifact_hash = event_hash(event)
        except (Fault, TypeError, ValueError):
            pass  # Malformed input must still produce a structured diagnostic.
    out = {
        "status": status,
        "mode": mode,
        "profile": profile,
        "conformance_class": BASELINE_CLASS,
        "event_identity": {"who": event["who"], "id": event["id"]} if (isinstance(event, dict) and isinstance(event.get("who"), str) and event["who"]
            and isinstance(event.get("id"), str) and event["id"] and event["id"].isascii()) else None,
        "event_hash": artifact_hash,
        "checks": dict(checks),
        "warnings": [],
        "errors": list(errors),
    }
    if acceptance is not None:
        out["acceptance"] = acceptance
    return out


def _identity_key(event: Mapping[str, Any]) -> str:
    who, eid = str(event["who"]), str(event["id"])
    return f"{len(who.encode())}:{who}{len(eid.encode())}:{eid}"


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = load_json(path)
        if not isinstance(data, dict):
            raise ValueError("acceptance state must be object")
        for record in data.values():
            if not isinstance(record, dict):
                raise ValueError("acceptance record must be object")
            for name in ("payload_digest", "event_hash"):
                value = record.get(name)
                if not isinstance(value, str) or not __import__("re").fullmatch(r"sha256:[0-9a-f]{64}", value):
                    raise ValueError(f"invalid acceptance record {name}")
            if type(record.get("accepted_at")) is not int:
                raise ValueError("invalid acceptance timestamp")
    except (Fault, ValueError) as exc:
        raise Fault("ERR_ACCEPTANCE_STATE_UNAVAILABLE", str(exc), "event_identity", indeterminate=True) from exc
    return data


@contextmanager
def _lock(path: Path):
    lock = path.with_name(path.name + ".lock")
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise Fault("ERR_ACCEPTANCE_ATOMICITY_UNAVAILABLE", "acceptance state is locked", "event_identity", indeterminate=True) from exc
    try:
        yield
    finally:
        lock.rmdir()


def _save_state(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def validate_event(
    event: Any,
    *,
    mode: str = "archival",
    keys=None,
    trust_profile: str = "none",
    expected_audience: str | None = None,
    now: int | None = None,
    max_age: int | None = None,
    max_future_skew: int = 60,
    acceptance_state: str | Path | None = None,
) -> dict[str, Any]:
    checks = _checks()
    profile = CORE_PROFILE if trust_profile == "none" else f"{CORE_PROFILE}+local-{trust_profile}"
    try:
        _require(mode in {"archival", "acceptance"}, "ERR_DOMAIN_REQUIREMENT_UNSATISFIED", "mode must be archival or acceptance")
        validate_shape(event)
        checks["syntax"] = "pass"

        kid, jwk = verify_jws(event, keys or {})
        checks["cryptographic"] = "pass"

        # Identity consistency is stateful; archival mode without state can only
        # validate identity shape, not historical uniqueness.
        checks["event_identity"] = "pass"

        if trust_profile != "none":
            actor_binding(event, kid, jwk, trust_profile)
            checks["actor_binding"] = "pass"

        if expected_audience is not None:
            if event.get("aud") != expected_audience:
                raise Fault("ERR_DOMAIN_REQUIREMENT_UNSATISFIED", "aud does not match expected audience", "audience")
            checks["audience"] = "pass"

        if max_age is not None:
            current = int(time.time()) if now is None else now
            if event["when"] < current - max_age:
                raise Fault("ERR_EVENT_EXPIRED", "event is older than freshness window", "freshness")
            if event["when"] > current + max_future_skew:
                raise Fault("ERR_TIMESTAMP_OUT_OF_WINDOW", "event is too far in future", "freshness")
            checks["freshness"] = "pass"

        process_extensions(event)
        checks["extension_processing"] = "pass"

        if "ref" not in event:
            checks["reference_integrity"] = "not_applicable"

        if mode == "archival":
            return _result("valid", mode, checks, event=event, profile=profile)

        if acceptance_state is None:
            raise Fault("ERR_ACCEPTANCE_STATE_UNAVAILABLE", "acceptance mode requires persistent acceptance state", "event_identity", indeterminate=True)

        state_path = Path(acceptance_state).resolve()
        state_path.parent.mkdir(parents=True, exist_ok=True)
        key = _identity_key(event)
        pdigest = payload_digest(event)

        with _lock(state_path):
            state = _load_state(state_path)
            previous = state.get(key)
            if previous is not None:
                if previous.get("payload_digest") != pdigest:
                    raise Fault("ERR_EVENT_ID_CONFLICT", "same Event Identity has different unsigned content", "event_identity")
                return _result(
                    "valid", mode, checks, event=event, profile=profile,
                    acceptance={"outcome":"already_accepted","effect_applied":False},
                )
            state[key] = {"payload_digest": pdigest, "event_hash": event_hash(event), "accepted_at": int(time.time())}
            _save_state(state_path, state)

        return _result(
            "valid", mode, checks, event=event, profile=profile,
            acceptance={"outcome":"accepted","effect_applied":True},
        )
    except Fault as fault:
        checks[fault.check] = "indeterminate" if fault.indeterminate else "fail"
        status = "indeterminate" if fault.indeterminate else "invalid"
        acceptance = None
        if mode == "acceptance":
            acceptance = {"outcome":"indeterminate" if fault.indeterminate else "rejected","effect_applied":False}
        return _result(status, mode, checks, event=event if isinstance(event, dict) else None,
                       errors=[fault.diagnostic()], acceptance=acceptance, profile=profile)
    except OSError as exc:
        fault = Fault("ERR_ACCEPTANCE_STATE_UNAVAILABLE", str(exc), "event_identity", indeterminate=True)
        checks["event_identity"] = "indeterminate"
        return _result("indeterminate", mode, checks, event=event if isinstance(event, dict) else None,
                       errors=[fault.diagnostic()],
                       acceptance={"outcome":"indeterminate","effect_applied":False} if mode == "acceptance" else None,
                       profile=profile)


def validate_file(path: str | Path, **kwargs) -> dict[str, Any]:
    try:
        event = load_json(path)
    except Fault as fault:
        checks = _checks()
        checks[fault.check] = "fail"
        mode = kwargs.get("mode", "archival")
        return _result("invalid", mode, checks, errors=[fault.diagnostic()],
                       acceptance={"outcome": "rejected", "effect_applied": False}
                       if mode == "acceptance" else None)
    return validate_event(event, **kwargs)


def run_tests(manifest_or_root: str | Path) -> dict[str, Any]:
    p = Path(manifest_or_root)
    manifest_path = p / "test-manifest-0.7.json" if p.is_dir() else p
    manifest = load_json(manifest_path)
    details, passed, failed = [], 0, 0
    temp_dir = Path(tempfile.mkdtemp(prefix="jep07-tests-"))
    states: dict[str, Path] = {}
    for case in manifest.get("cases", []):
        path = (manifest_path.parent / case["path"]).resolve()
        keys = load_keys((manifest_path.parent / case["keys"]).resolve()) if case.get("keys") else {}
        state_name = case.get("state")
        state_path = states.setdefault(state_name, temp_dir / f"{state_name}.json") if state_name else None
        result = validate_file(
            path,
            mode=case.get("mode","archival"),
            keys=keys,
            trust_profile=case.get("trust_profile","none"),
            expected_audience=case.get("expected_audience"),
            now=case.get("now"),
            max_age=case.get("max_age"),
            acceptance_state=state_path,
        )
        problems = []
        if case.get("expected_status") and result.get("status") != case["expected_status"]:
            problems.append(f"status {result.get('status')} != {case['expected_status']}")
        if case.get("expected_error"):
            codes = [x.get("code") for x in result.get("errors",[])]
            if case["expected_error"] not in codes:
                problems.append(f"missing error {case['expected_error']}; got {codes}")
        if case.get("expected_outcome"):
            actual = (result.get("acceptance") or {}).get("outcome")
            if actual != case["expected_outcome"]:
                problems.append(f"outcome {actual} != {case['expected_outcome']}")
        ok = not problems
        passed += int(ok)
        failed += int(not ok)
        details.append({"name":case.get("name"),"ok":ok,"problems":problems,"result":result})
    return {"suite":manifest.get("suite","jep-core-0.7"),"version":"0.7","passed":passed,"failed":failed,"details":details}


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="JEP Core 0.7 reference validator")
    sub = ap.add_subparsers(dest="command", required=True)
    v = sub.add_parser("validate")
    v.add_argument("event")
    v.add_argument("--keys")
    v.add_argument("--mode", choices=["archival","acceptance"], default="archival")
    v.add_argument("--trust-profile", choices=["none","kid-prefix","inline"], default="none")
    v.add_argument("--aud")
    v.add_argument("--now", type=int)
    v.add_argument("--max-age", type=int)
    v.add_argument("--acceptance-state")
    t = sub.add_parser("run-tests")
    t.add_argument("manifest_or_root", nargs="?", default=".")
    c = sub.add_parser("canonicalize")
    c.add_argument("json_file")
    args = ap.parse_args(argv)

    try:
        if args.command == "validate":
            output = validate_file(args.event, keys=load_keys(args.keys), mode=args.mode,
                                   trust_profile=args.trust_profile, expected_audience=args.aud,
                                   now=args.now, max_age=args.max_age,
                                   acceptance_state=args.acceptance_state)
        elif args.command == "run-tests":
            output = run_tests(args.manifest_or_root)
        else:
            sysout = canonicalize(load_json(args.json_file))
            import sys
            sys.stdout.buffer.write(sysout + b"\n")
            return 0
    except (Fault, OSError, ValueError) as exc:
        ap.exit(2, f"JEP input/configuration error: {exc}\n")

    print(json.dumps(output, ensure_ascii=False, indent=2))
    if args.command == "run-tests":
        return 1 if output["failed"] else 0
    return 0 if output["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
