"""Structural schemas must agree with the current reference validator."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from jep_conformance import jep_validate_07 as core

ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = Draft202012Validator(json.loads((ROOT / 'schemas/jep-event.schema.json').read_text()))
REF_SCHEMA = Draft202012Validator(json.loads((ROOT / 'schemas/jep-ref.schema.json').read_text()))


def event():
    return json.loads((ROOT / 'test-vectors/0.7/valid/J-basic.json').read_text())


@pytest.mark.parametrize('suffix', ['', '\n', '\r\n', '\u2028', '\x00', ' '])
@pytest.mark.parametrize('digest', ['sha256:' + 'a' * 64, 'other:ab'])
def test_digest_end_matches_full_string(suffix, digest):
    value = digest + suffix
    expected = suffix == ''
    for patch in ({'what': value}, {'ref': value},
                  {'ref': {'type': 'evidence', 'value': 'demo', 'hash': value}}):
        candidate = {**event(), **patch}
        assert EVENT_SCHEMA.is_valid(candidate) is expected
        if expected:
            core.validate_shape(candidate)
        else:
            with pytest.raises(core.Fault):
                core.validate_shape(candidate)
    assert REF_SCHEMA.is_valid(value) is expected
    assert REF_SCHEMA.is_valid({'type': 'evidence', 'value': 'demo', 'hash': value}) is expected


@pytest.mark.parametrize('ext,expected', [({}, True), ({'urn:example:note': {}}, True), ({'': {}}, False)])
def test_extension_identifier_shape(ext, expected):
    candidate = {**event(), 'ext': ext}
    assert EVENT_SCHEMA.is_valid(candidate) is expected
    if expected:
        core.validate_shape(candidate)
    else:
        with pytest.raises(core.Fault):
            core.validate_shape(candidate)
