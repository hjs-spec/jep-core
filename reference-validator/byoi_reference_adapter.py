"""Protocol wiring example using the existing reference verifier; not independent.

Supports producer/verifier testing only. No external acceptance-effect claim.
The fixed signing key is public test material.
"""
import json
import sys

from nacl.signing import SigningKey

from . import jep_validate_07 as core


def respond(request):
    if request.get('adapter_protocol') != 'jep-byoi/1':
        return {'unsupported': 'adapter protocol'}
    if request['operation'] == 'produce':
        event = dict(request['unsigned_event'])
        key = SigningKey(bytes([3]) * 32)
        protected = core.b64u(b'{"alg":"Ed25519","kid":"reference-adapter-test-key"}')
        signing_input = (protected + '.' + core.b64u(core.canonicalize(event))).encode()
        event['sig'] = protected + '..' + core.b64u(key.sign(signing_input).signature)
        return {'event_json': json.dumps(event), 'keys': {'reference-adapter-test-key': {
            'kty': 'OKP', 'crv': 'Ed25519', 'x': core.b64u(bytes(key.verify_key))}}}
    if request['operation'] != 'validate' or request.get('mode') != 'archival':
        return {'unsupported': 'reference adapter supports producer and archival verifier only'}
    if request.get('profile') != 'jep-core-0.7' or request.get('signature_class') != core.BASELINE_CLASS:
        return {'unsupported': 'profile or signature class'}
    try:
        event = core.parse_json(request['event_json'])
    except (ValueError, UnicodeError) as exc:
        code = 'ERR_DUPLICATE_MEMBER' if isinstance(exc, core.DuplicateKeyError) else 'ERR_INVALID_JSON'
        checks = {name: 'not_checked' for name in core.CHECKS}
        checks['syntax'] = 'fail'
        return {'result': {'status': 'invalid', 'mode': 'archival', 'profile': 'jep-core-0.7',
                           'checks': checks, 'warnings': [], 'errors': [{'code': code, 'message': 'Malformed test input'}]}}
    return {'result': core.validate_event(event, keys=request['keys'], mode='archival')}


def main():
    print(json.dumps(respond(json.load(sys.stdin))))


if __name__ == '__main__':
    main()
