"""Malformed-input, storage and publication regressions for the current path."""
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from nacl.signing import SigningKey

from jep_conformance import jep_validate_07 as core

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "test-vectors/0.7"


@pytest.fixture
def event():
    return json.loads((VECTORS / "valid/J-basic.json").read_text())


@pytest.mark.parametrize("patch", [
    {"ext_crit": [{}]}, {"ext_crit": [[]]}, {"ext_crit": None},
    {"verb": []}, {"who": "\ud800"}, {"when": 2**53},
    {"what": {"value": float("nan")}}, {"what": {1: "non-string member"}},
    {"verb": "V", "ref": "sha256:" + "0" * 64,
     "what": {"verification_scope": [{}], "result": "pass"}},
])
def test_malformed_input_returns_structured_rejection(event, patch):
    result = core.validate_event({**event, **patch}, mode="acceptance")
    assert result["status"] == "invalid"
    assert result["acceptance"] == {"outcome": "rejected", "effect_applied": False}


def test_missing_key_is_indeterminate(event):
    result = core.validate_event(event, mode="acceptance")
    assert result["status"] == "indeterminate"
    assert result["errors"][0]["code"] == "ERR_KEY_UNRESOLVED"
    assert result["acceptance"]["effect_applied"] is False


@pytest.mark.parametrize("stored", ["{", "[]", '{"identity":null}', '{"identity":{}}'])
def test_corrupt_storage_does_not_reset_or_mislabel_event(event, stored, tmp_path):
    state = tmp_path / "state.json"
    state.write_text(stored)
    keys = json.loads((VECTORS / "keys.json").read_text())
    result = core.validate_event(event, keys=keys, mode="acceptance", acceptance_state=state)
    assert result["status"] == "indeterminate"
    assert result["errors"][0]["code"] == "ERR_ACCEPTANCE_STATE_UNAVAILABLE"
    assert result["checks"]["cryptographic"] == "pass"
    assert result["acceptance"]["effect_applied"] is False
    assert state.read_text() == stored
    assert not state.with_suffix('.json.lock').exists()


def test_wrong_payload_encoding_rejected_before_state_change(event, tmp_path):
    key = SigningKey.generate()
    protected = core.b64u(b'{"alg":"Ed25519","kid":"key","b64":false}')
    payload = core.b64u(core.canonicalize({k: v for k, v in event.items() if k != "sig"}))
    event["sig"] = protected + ".." + core.b64u(key.sign((protected + "." + payload).encode()).signature)
    keys = {"key": {"kty": "OKP", "crv": "Ed25519", "x": core.b64u(bytes(key.verify_key))}}
    state = tmp_path / "state.json"
    result = core.validate_event(event, keys=keys, mode="acceptance", acceptance_state=state)
    assert result["errors"][0]["code"] == "ERR_SIGNATURE_CONTAINER_INVALID"
    assert not state.exists()


def test_malformed_file_has_acceptance_outcome(tmp_path):
    path = tmp_path / "event.json"
    path.write_text('{"id":"a","id":"b"}')
    result = core.validate_file(path, mode="acceptance")
    assert result["errors"][0]["code"] == "ERR_DUPLICATE_MEMBER"
    assert result["acceptance"] == {"outcome": "rejected", "effect_applied": False}


@pytest.mark.parametrize("identity", ["x", "with space", "\u0001", "\u007f", "urn:uuid:x"])
def test_schema_matches_core_ascii_identity(event, identity):
    event["id"] = identity
    schema = json.loads((ROOT / "schemas/jep-event.schema.json").read_text())
    Draft202012Validator(schema).validate(event)
    core.validate_shape(event)


@pytest.mark.parametrize("digest", ["sha256:abc", "sha256:" + "f" * 64, "other:ab"])
def test_standalone_ref_and_event_schema_agree(event, digest):
    reference = Draft202012Validator(json.loads((ROOT / "schemas/jep-ref.schema.json").read_text()))
    whole = Draft202012Validator(json.loads((ROOT / "schemas/jep-event.schema.json").read_text()))
    for ref in (digest, {"type": "evidence", "value": "x", "hash": digest}):
        assert reference.is_valid(ref) == whole.is_valid({**event, "ref": ref})


def test_repository_guard_and_frozen_artifact(tmp_path):
    spec = importlib.util.spec_from_file_location("repository_guard", ROOT / "scripts/check_repository.py")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.check()
    first = next(iter(guard.FROZEN))
    corrupted = tmp_path / first
    corrupted.parent.mkdir(parents=True)
    corrupted.write_text("changed publication")
    with pytest.raises(ValueError, match="Frozen publication changed"):
        guard.check(tmp_path)
