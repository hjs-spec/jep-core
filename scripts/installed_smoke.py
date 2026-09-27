"""Run with -I in a fresh venv; disposable keys, no production service/state."""
from copy import deepcopy
from importlib.metadata import version
import json
from pathlib import Path
import tempfile

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from jep_conformance import jep_validate_07 as core
from jep_agent.core.event import build_event, sign_event, event_hash, parse_json
from jep_agent.core.verifier import JEPVerifier
from jep_cli import strict_json

key = Ed25519PrivateKey.generate()
public = key.public_key()
who = 'did:example:registry-smoke'
kid = who + '#key-1'
x = core.b64u(public.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw))
keys = {name: {'kty': 'OKP', 'crv': 'Ed25519', 'x': x, 'actors': [who]}
        for name in [kid, who + '#key-2']}
ref = {'type': 'jep:event', 'value': {'who': who, 'id': 'urn:example:registry:J'}}
bodies = {
    'J': {'claim': 'synthetic smoke', 'large': 1000000000000000100, 'exact': 1000000000000000128},
    'D': {'delegatee': 'did:example:worker', 'scope': {'action': 'smoke'}},
    'T': {'termination_scope': 'future_reliance'},
    'V': {'verification_scope': ['synthetic_smoke'], 'result': 'pass'},
}
events = []
for verb, what in bodies.items():
    unsigned = build_event(verb, who, what, event_id='urn:example:registry:' + verb,
                           ref=None if verb == 'J' else ref, ext={}, ext_crit=[], when=1)
    event = sign_event(unsigned, key, kid=kid)
    assert 'nonce' not in event
    checked = core.validate_event(event, keys=keys, trust_profile='inline')
    assert checked['status'] == 'valid', checked
    assert checked['checks']['cryptographic'] == 'pass'
    assert checked['checks']['actor_binding'] == 'pass'
    assert JEPVerifier().verify_result(event, public)['status'] == 'valid'
    transported = strict_json.loads(strict_json.dumps(event))
    assert event_hash(transported) == core.event_hash(event)
    assert transported['sig'] == event['sig']
    altered = deepcopy(event)
    altered['what']['test_tamper'] = True
    assert core.validate_event(altered, keys=keys)['status'] == 'invalid'
    assert JEPVerifier().verify_result(altered, public)['status'] == 'invalid'
    events.append(event)

assert core.validate_event(events[0], keys={})['status'] == 'indeterminate'
with tempfile.TemporaryDirectory() as directory:
    state = Path(directory) / 'acceptance.json'
    first = core.validate_event(events[0], mode='acceptance', keys=keys, acceptance_state=state)
    assert first['acceptance'] == {'outcome': 'accepted', 'effect_applied': True}
    resigned = sign_event(events[0], key, kid=who + '#key-2')
    assert core.event_hash(resigned) != core.event_hash(events[0])
    second = core.validate_event(resigned, mode='acceptance', keys=keys, acceptance_state=state)
    assert second['acceptance'] == {'outcome': 'already_accepted', 'effect_applied': False}
    conflict = deepcopy(events[0])
    conflict['what']['conflict'] = True
    conflict = sign_event(conflict, key, kid=kid)
    rejected = core.validate_event(conflict, mode='acceptance', keys=keys, acceptance_state=state)
    assert rejected['status'] == 'invalid' and not rejected['acceptance']['effect_applied']

bad = ['{"x":1,"x":2}', '{"x":{"a":1,"\\u0061":2}}',
       '{"x":NaN}', '{"x":1e400}', '{"x":9007199254740993}', '{"x":"\\ud800"}']
for loader in [core.parse_json, parse_json, strict_json.loads]:
    for raw in bad:
        try:
            loader(raw)
        except ValueError:
            pass
        else:
            raise AssertionError('malformed input accepted: ' + raw)

print(json.dumps({'status': 'pass', 'packages': {p: version(p) for p in
                 ['jep-core-conformance', 'jep-agent-sdk', 'jep-cli', 'jep-sdk-py']},
                 'signed_verbs': list(bodies), 'core_sdk_cli_roundtrips': 4,
                 'tamper_rejections': 8, 'strict_input_rejections': 18,
                 'acceptance': ['accepted', 'already_accepted', 'identity_conflict'],
                 'missing_key': 'indeterminate',
                 'limits': 'Synthetic local tests; no external truth, policy or deployed acceptance claim.'}, indent=2))
