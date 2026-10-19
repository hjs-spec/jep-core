"""Run native BYOI against an unchanged, explicitly pinned Probity reader."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from probity_byoi_bridge import READER_REVISION

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reader-root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    reader = args.reader_root.resolve()
    revision = subprocess.check_output(['git', '-C', str(reader), 'rev-parse', 'HEAD'], text=True).strip()
    if revision != READER_REVISION:
        parser.error(f'Reader must be checked out at {READER_REVISION}')
    clean = subprocess.run(['git', '-C', str(reader), 'diff', '--quiet', 'HEAD', '--',
                            'interop/jep-core07-reader'], check=False)
    if clean.returncode:
        parser.error('Reader implementation has local changes')
    report = args.report.resolve()
    disclosure = report.with_suffix('.implementation.json')
    if report.exists() or disclosure.exists():
        parser.error('Use new report and implementation-disclosure paths')
    bridge = ROOT / 'integration/probity_byoi_bridge.py'
    bridge_digest = hashlib.sha256(bridge.read_bytes()).hexdigest()
    implementation = {
        'name': 'Probity Core 0.7 reader with JEP-owned BYOI bridge',
        'version': READER_REVISION,
        'source': f'https://github.com/probityai/agent-evidence-vectors/tree/{READER_REVISION}/interop/jep-core07-reader',
        'revision': READER_REVISION,
        'independence': 'separately implemented reader; JEP-owned adapter and reference producer cross-check',
        'reused_components': [
            'JEP BYOI runner, public fixtures, exposed expected answers and producer cross-check oracle',
            f'JEP-owned diagnostics/state-lifecycle bridge sha256:{bridge_digest}',
            'Probity signing, validation, synthetic SQLite acceptance and read-only observation remain unchanged',
        ],
    }
    with disclosure.open('x', encoding='utf-8') as output:
        json.dump(implementation, output, indent=2)
        output.write('\n')
    command = [sys.executable, str(bridge), '--reader-root', str(reader)]
    argv = [sys.executable, '-m', 'jep_conformance.byoi', 'run',
            '--implementation', str(disclosure), '--role', 'verifier', '--role', 'producer',
            '--role', 'acceptance', '--adapter', json.dumps(command + ['adapter']),
            '--effect-probe', json.dumps(command + ['probe']),
            '--state-setup', json.dumps(command + ['setup']),
            '--effect-scope', 'Synthetic local SQLite rows; setup is separate from the read-only probe. '
                              'No external actions, independent custody, power-loss or multi-host guarantee.',
            '--report', str(report)]
    return subprocess.run(argv, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
