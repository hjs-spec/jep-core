from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys

from jsonschema import Draft202012Validator
import pytest

from jep_conformance import byoi
from jep_conformance import jep_validate_07 as core

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = [sys.executable, '-m', 'jep_conformance.byoi_reference_adapter']
ACCEPTANCE = [sys.executable, str(ROOT / 'tests/support/byoi_acceptance_fixture.py')]
DISCLOSURE = {'name': 'synthetic-test-adapter', 'version': 'test', 'source': 'local test fixture',
              'revision': 'working-tree', 'independence': 'reference-wrapper', 'reused_components': ['jep-core-conformance']}


@pytest.mark.parametrize('name', ['V-basic', 'V-array-scope'])
def test_published_and_existing_v_scope_forms_preserve_signed_artifacts(name):
    path = byoi.SUITE / f'vectors/{name}.json'
    original = path.read_bytes()
    event = core.parse_json(original.decode())
    schema = Draft202012Validator(json.loads((ROOT / 'schemas/jep-event.schema.json').read_text()))
    schema.validate(event)
    result = core.validate_event(event, keys=byoi.read_json(byoi.SUITE / 'keys.json'))
    assert result['status'] == 'valid'
    assert result['event_hash'] == core.event_hash(event)
    assert path.read_bytes() == original


def test_reference_producer_and_verifier_end_to_end():
    report = byoi.run_suite(byoi.SUITE, REFERENCE, DISCLOSURE, ['producer', 'verifier'])
    assert report['outcome'] == 'pass', report['results']
    assert report['tests_passed'] == 29
    assert report['tests_not_selected'] == 8
    assert report['complete_core_coverage'] is False
    assert report['certification'] is False
    Draft202012Validator(json.loads((ROOT / 'schemas/jep-byoi-report.schema.json').read_text())).validate(report)


def test_acceptance_uses_real_ledger_observations_and_fresh_processes():
    report = byoi.run_suite(byoi.SUITE, ACCEPTANCE, DISCLOSURE, ['acceptance'],
                           probe=ACCEPTANCE + ['--probe'], effect_scope='Synthetic SQLite receipts')
    assert report['outcome'] == 'pass', report['results']
    assert report['tests_passed'] == 33
    concurrency = next(item for item in report['results'] if item['assertion_id'] == 'JEP-A-ACC-007')
    assert len(concurrency['observations'][0]['results']) == 9
    assert concurrency['observations'][0]['observed_effect_count'] == 1


@pytest.mark.parametrize('fault', ['--duplicate-effects', '--no-effect'])
def test_false_effect_applied_flags_do_not_pass(fault):
    report = byoi.run_suite(byoi.SUITE, ACCEPTANCE + [fault], DISCLOSURE, ['acceptance'],
                           probe=ACCEPTANCE + ['--probe'], effect_scope='Synthetic SQLite receipts')
    assert report['outcome'] == 'fail'
    assert any('Observed' in problem for item in report['results'] for problem in item['problems'])


def test_acceptance_cannot_be_claimed_without_a_probe():
    with pytest.raises(ValueError, match='separate read-only effect probe'):
        byoi.run_suite(byoi.SUITE, REFERENCE, DISCLOSURE, ['acceptance'])


def test_unsupported_is_not_a_pass():
    adapter = [sys.executable, '-c', 'import json; print(json.dumps({"unsupported":"no producer"}))']
    report = byoi.run_suite(byoi.SUITE, adapter, DISCLOSURE, ['producer'])
    assert report['outcome'] == 'incomplete'
    assert report['tests_passed'] == 0 and report['tests_unsupported'] == 4


def test_timeout_cannot_produce_a_pass():
    adapter = [sys.executable, '-c', 'import time; time.sleep(1)']
    report = byoi.run_suite(byoi.SUITE, adapter, DISCLOSURE, ['producer'], timeout=0.02)
    assert report['outcome'] == 'fail' and report['tests_failed'] == 4


def test_manifest_binds_every_fixture_byte(tmp_path):
    target = tmp_path / 'suite'
    shutil.copytree(byoi.SUITE, target)
    path = target / 'vectors/J-basic.json'
    path.write_text(path.read_text() + ' ')
    with pytest.raises(ValueError, match='digest mismatch'):
        byoi.load_suite(target)


def test_manifest_rejects_escape_and_unbound_input(tmp_path):
    target = tmp_path / 'suite'; shutil.copytree(byoi.SUITE, target)
    path = target / 'manifest.json'; original = json.loads(path.read_text())
    changed = copy.deepcopy(original); changed['files']['../outside.json'] = 'sha256:0'
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='escapes'):
        byoi.load_suite(target)
    changed = copy.deepcopy(original); changed['assertions'][0]['input'] = 'unbound.json'
    path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='not bound'):
        byoi.load_suite(target)


def test_export_is_self_contained_and_does_not_overwrite(tmp_path):
    target = tmp_path / 'export'
    process = subprocess.run([sys.executable, '-m', 'jep_conformance.byoi', 'export', str(target)], capture_output=True)
    assert process.returncode == 0, process.stderr
    assert byoi.load_suite(target)[1] == byoi.load_suite(byoi.SUITE)[1]
    again = subprocess.run([sys.executable, '-m', 'jep_conformance.byoi', 'export', str(target)], capture_output=True)
    assert again.returncode == 2
