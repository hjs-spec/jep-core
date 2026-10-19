"""Explicit test-only bridge for the pinned Probity Core 0.7 fixture reader.

This JEP-owned bridge adds empty diagnostic arrays omitted by the selected reader
and connects its explicit database initializer to BYOI's setup hook. It does not
replace validation, signing, acceptance or effect observation with JEP code.
Use only a reviewed local reader checkout and disposable synthetic state.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

READER_REVISION = 'cbd3ea8f4de89b835d6d3c4182ff4b4b1c7608f9'


def diagnostics(response):
    """Expose omitted empty diagnostics without altering a measured decision."""
    result = copy.deepcopy(response)
    if isinstance(result.get('result'), dict):
        result['result'].setdefault('warnings', [])
        result['result'].setdefault('errors', [])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reader-root', type=Path, required=True,
                        help='Reviewed checkout of probityai/agent-evidence-vectors')
    parser.add_argument('role', choices=['adapter', 'probe', 'setup'])
    args = parser.parse_args()
    reader = args.reader_root.resolve() / 'interop/jep-core07-reader'
    if not all((reader / name).is_file() for name in ('adapter.py', 'state.py', 'validator.py')):
        parser.error('Reader checkout is incomplete')
    # This is explicitly supplied trusted local code, never an event-provided path.
    sys.path.insert(0, str(reader))
    from adapter import exchange
    from state import initialize

    request = json.load(sys.stdin)
    if request.get('adapter_protocol') != 'jep-byoi/1':
        parser.error('Unsupported adapter protocol')
    state = None
    if 'state_dir' in request:
        state = Path(request['state_dir']).resolve() / 'probity-core07'
        request['state_dir'] = str(state)
    if args.role == 'setup':
        if request.get('operation') != 'prepare_state' or state is None:
            parser.error('Setup requires an explicit prepare_state request')
        # Only setup may create state. initialize refuses an existing directory.
        initialize(state)
        response = {'prepared': True}
    elif args.role == 'probe':
        if request.get('operation') != 'observe_effects' or state is None:
            parser.error('Probe accepts only observe_effects requests')
        response = exchange(request)  # Reader opens the existing database read-only.
    else:
        if request.get('operation') not in {'validate', 'produce', 'set_state_availability'}:
            parser.error('Unsupported adapter operation')
        response = diagnostics(exchange(request))
    print(json.dumps(response, ensure_ascii=False))


if __name__ == '__main__':
    main()
