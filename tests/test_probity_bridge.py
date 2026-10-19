"""Bridge diagnostics must preserve the separate reader's measured decisions."""
import copy
import importlib.util
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / 'integration/probity_byoi_bridge.py'
SPEC = importlib.util.spec_from_file_location('probity_bridge_test', PATH)
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


@pytest.mark.parametrize('status', ['valid', 'invalid', 'indeterminate'])
def test_bridge_only_supplies_absent_diagnostic_arrays(status):
    response = {'result': {'status': status, 'checks': {'cryptographic': 'fail'},
                           'errors': [{'code': 'original-error', 'message': 'retain me'}],
                           'acceptance': {'outcome': 'rejected', 'effect_applied': False}}}
    original = copy.deepcopy(response)
    adapted = bridge.diagnostics(response)
    assert adapted == {'result': {**original['result'], 'warnings': []}}
    assert response == original


def test_bridge_does_not_erase_malformed_diagnostics_or_unsupported_result():
    malformed = {'result': {'status': 'valid', 'warnings': None, 'errors': 'wrong type'}}
    assert bridge.diagnostics(malformed) == malformed
    assert bridge.diagnostics({'unsupported': 'profile'}) == {'unsupported': 'profile'}
