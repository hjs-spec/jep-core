"""Synthetic harness test target, not a JEP product or an independent implementation.

The protected test effect is a SQLite receipt inserted in the same transaction
as identity acceptance. The separate probe opens the ledger read-only and counts
receipts. Fault switches prove the harness does not trust effect_applied alone.
"""
import json
from pathlib import Path
import sqlite3
import sys

from jep_conformance import byoi_reference_adapter as reference
from jep_conformance import jep_validate_07 as core


def main(request, *, probe=False, duplicate_effects=False, no_effect=False):
    if not probe and request.get('operation') == 'validate' and request.get('mode') == 'archival':
        return reference.respond(request)
    state = Path(request['state_dir'])
    database = state / 'synthetic-effects.sqlite'
    domain = request['acceptance_domain']
    if probe:
        if not database.exists():
            return {'effect_count': 0}
        with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as connection:
            return {'effect_count': connection.execute('SELECT count(*) FROM effects WHERE domain=?', (domain,)).fetchone()[0]}
    unavailable = state / 'state-unavailable'
    if request['operation'] == 'set_state_availability':
        if request['available']:
            unavailable.unlink(missing_ok=True)
        else:
            unavailable.touch()
        return {'configured': True}
    response = reference.respond({**request, 'mode': 'archival'})
    result = response['result']
    if request['mode'] == 'archival':
        return response
    result['mode'] = 'acceptance'

    def finish(outcome, status='valid', error=None):
        result['status'] = status
        result['acceptance'] = {'outcome': outcome, 'effect_applied': outcome == 'accepted'}
        if error:
            result['errors'] = [{'code': error, 'message': 'Synthetic fixture state outcome'}]
            result['checks']['event_identity'] = 'indeterminate' if status == 'indeterminate' else 'fail'
        return response

    if result['status'] != 'valid':
        return finish('rejected' if result['status'] == 'invalid' else 'indeterminate', result['status'])
    if unavailable.exists():
        return finish('indeterminate', 'indeterminate', 'ERR_ACCEPTANCE_STATE_UNAVAILABLE')
    event = core.parse_json(request['event_json'])
    key = (domain, event['who'], event['id'])
    payload = core.payload_digest(event)
    with sqlite3.connect(database, timeout=10) as connection:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('CREATE TABLE IF NOT EXISTS identities (domain TEXT, who TEXT, event_id TEXT, digest TEXT, PRIMARY KEY(domain, who, event_id))')
        connection.execute('CREATE TABLE IF NOT EXISTS effects (domain TEXT, who TEXT, event_id TEXT)')
        previous = connection.execute('SELECT digest FROM identities WHERE domain=? AND who=? AND event_id=?', key).fetchone()
        if previous:
            if previous[0] != payload:
                return finish('rejected', 'invalid', 'ERR_EVENT_ID_CONFLICT')
            return finish('already_accepted')
        connection.execute('INSERT INTO identities VALUES (?,?,?,?)', (*key, payload))
        if not no_effect:
            connection.execute('INSERT INTO effects VALUES (?,?,?)', key)
        if duplicate_effects:
            connection.execute('INSERT INTO effects VALUES (?,?,?)', key)
    return finish('accepted')


if __name__ == '__main__':
    print(json.dumps(main(json.load(sys.stdin), probe='--probe' in sys.argv,
                          duplicate_effects='--duplicate-effects' in sys.argv, no_effect='--no-effect' in sys.argv)))
