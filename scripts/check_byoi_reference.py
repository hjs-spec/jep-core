"""Run the documented local reference-wiring example without a shell adapter."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from jep_conformance import byoi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip():
        revision += '+working-tree-changes'
    disclosure = {'name': 'jep-core-reference-wiring-example', 'version': 'source-checkout',
                  'source': 'https://github.com/hjs-spec/jep-core', 'revision': revision,
                  'independence': 'reference-wrapper; not an independent implementation',
                  'reused_components': ['jep-core-conformance reference validator and signing helpers']}
    report = byoi.run_suite(byoi.SUITE, [sys.executable, '-m', 'jep_conformance.byoi_reference_adapter'],
                            disclosure, ['producer', 'verifier'])
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: report[key] for key in ('outcome', 'tests_passed', 'tests_failed', 'tests_unsupported', 'tests_not_selected')}))
    if report['outcome'] != 'pass':
        for row in report['results']:
            if row['outcome'] != 'pass':
                print(json.dumps(row))
    return 0 if report['outcome'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
