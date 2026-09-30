"""Language-neutral, scoped conformance runner. No Core semantics are defined here."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

PROTOCOL = "jep-byoi/1"
SUITE = Path(__file__).with_name("byoi_suite")
CHECK_STATUSES = {"pass", "fail", "not_checked", "not_applicable", "unsupported", "indeterminate"}


class Unsupported(Exception):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()


def suite_file(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError(f"Suite path escapes its root: {name}")
    return path


def load_suite(root):
    raw = (root / "manifest.json").read_bytes()
    manifest = json.loads(raw)
    if manifest['adapter_protocol'] != PROTOCOL:
        raise ValueError("Unsupported suite adapter protocol")
    if manifest['jep_core'] != '0.7' or manifest['signature_class'] != 'JEP-Baseline-Ed25519-JWS-JCS-0.7':
        raise ValueError("This runner supports Core 0.7 and the declared Ed25519 baseline only")
    if not all(manifest[name] for name in ('assertions', 'producer_assertions', 'acceptance_assertions')):
        raise ValueError("Suite role groups must not be empty")
    if not {'keys.json', 'coverage.json', 'report.schema.json'}.issubset(manifest['files']):
        raise ValueError("Suite metadata files must be bound by the manifest")
    for name, expected in manifest['files'].items():
        if digest(suite_file(root, name).read_bytes()) != expected:
            raise ValueError(f"Suite file digest mismatch: {name}")
    assertions = manifest['assertions'] + manifest['producer_assertions'] + manifest['acceptance_assertions']
    ids = [case['assertion_id'] for case in assertions]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Suite assertions need unique identifiers")
    for case in assertions:
        if not case.get('requirements'):
            raise ValueError("Missing normative-source mapping")
        paths = [case.get('input'), case.get('keys'), case.get('template')]
        paths += [step.get('input') for step in case.get('steps', [])]
        if any(path not in manifest['files'] for path in paths if path):
            raise ValueError("Assertion references a file not bound by the manifest")
    return manifest, digest(raw)


def command(value):
    parts = json.loads(value) if isinstance(value, str) else value
    if not isinstance(parts, list) or not parts or not all(isinstance(x, str) and x for x in parts):
        raise ValueError("A command must be a nonempty JSON array of argument strings")
    return parts


def invoke(argv, request, timeout):
    process = subprocess.run(argv, input=json.dumps({"adapter_protocol": PROTOCOL, **request}),
                             capture_output=True, text=True, encoding="utf-8", timeout=timeout, shell=False)
    if process.returncode != 0:
        # Do not copy arbitrary stderr (which might contain local secrets) into a public report.
        raise ValueError(f"Adapter/probe exited with code {process.returncode}; inspect locally")
    if len(process.stdout) > 1_000_000:
        raise ValueError("Adapter/probe response exceeds 1 MB")
    response = json.loads(process.stdout)
    if not isinstance(response, dict):
        raise ValueError("Adapter/probe must return one JSON object")
    if 'unsupported' in response:
        raise Unsupported(str(response['unsupported']))
    return response


def validation(response, mode, expected=None):
    result = response.get('result')
    if not isinstance(result, dict):
        raise ValueError("Missing structured validation result")
    required = {'status', 'mode', 'profile', 'checks', 'warnings', 'errors'}
    if not required.issubset(result) or result['mode'] != mode:
        raise ValueError("Incomplete result or wrong validation mode")
    if result['status'] not in {'valid', 'invalid', 'indeterminate'}:
        raise ValueError("Invalid overall status")
    if not isinstance(result['profile'], str) or not result['profile']:
        raise ValueError("Missing profile identifier")
    checks = result['checks']
    if not isinstance(checks, dict) or any(value not in CHECK_STATUSES for value in checks.values()):
        raise ValueError("Invalid independent checks")
    for name in ('warnings', 'errors'):
        if not isinstance(result[name], list) or any(not isinstance(item, dict) or not
                isinstance(item.get('code'), str) or not isinstance(item.get('message'), str) for item in result[name]):
            raise ValueError("Invalid structured diagnostics")
    if 'level' in result or 'validation_level' in result:
        raise ValueError("Current reports must not substitute cumulative Validation Levels")
    if mode == 'archival' and 'acceptance' in result:
        raise ValueError("Archival validation must not claim acceptance")
    if mode == 'acceptance':
        acceptance = result.get('acceptance', {})
        outcome = acceptance.get('outcome')
        pairs = {'accepted': ('valid', True), 'already_accepted': ('valid', False),
                 'rejected': ('invalid', False), 'indeterminate': ('indeterminate', False)}
        if outcome not in pairs or (result['status'], acceptance.get('effect_applied')) != pairs[outcome] \
                or type(acceptance.get('effect_applied')) is not bool:
            raise ValueError("Inconsistent validation/acceptance outcome")
    for key, wanted in (expected or {}).items():
        if key == 'checks':
            for check, status in wanted.items():
                if checks.get(check) != status:
                    raise ValueError(f"Expected {check}={status}; got {checks.get(check)}")
        elif key == 'error_code':
            if wanted not in [item.get('code') for item in result['errors']]:
                raise ValueError(f"Missing expected error {wanted}")
        elif result.get(key) != wanted:
            raise ValueError(f"Expected {key}={wanted!r}; got {result.get(key)!r}")
    return result


def run_suite(root, adapter, implementation, roles, *, probe=None, effect_scope=None, timeout=15):
    manifest, suite_digest = load_suite(root)
    adapter = command(adapter)
    probe = command(probe) if probe else None
    roles = sorted(set(roles))
    if not roles or any(role not in {'producer', 'verifier', 'acceptance'} for role in roles):
        raise ValueError("Choose producer, verifier and/or acceptance roles")
    if 'acceptance' in roles:
        if probe is None or not effect_scope:
            raise ValueError("Acceptance testing requires a separate read-only effect probe and effect scope")
        if 'verifier' not in roles:
            roles.append('verifier')
    for field in ('name', 'version', 'source', 'revision', 'independence'):
        if not isinstance(implementation.get(field), str) or not implementation[field]:
            raise ValueError(f"Implementation descriptor requires {field}")
    if not isinstance(implementation.get('reused_components'), list) or not all(isinstance(x, str) for x in implementation['reused_components']):
        raise ValueError("Disclose reused_components (an empty array is allowed)")
    results = []

    def execute(case, action):
        detail = {'assertion_id': case['assertion_id'], 'requirements': case['requirements'],
                  'outcome': 'pass', 'observations': [], 'problems': []}
        try:
            action(detail['observations'])
        except Unsupported as exc:
            detail['outcome'] = 'unsupported'; detail['problems'].append(str(exc))
        except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
            detail['outcome'] = 'fail'; detail['problems'].append(str(exc))
        results.append(detail)

    def request(path, *, mode='archival', keyfile='keys.json', **context):
        return {'operation': 'validate', 'event_json': suite_file(root, path).read_text(encoding='utf-8'),
                'keys': read_json(suite_file(root, keyfile)), 'mode': mode, 'profile': 'jep-core-0.7',
                'signature_class': manifest['signature_class'], **context}

    if 'verifier' in roles:
        for case in manifest['assertions']:
            def check(observations, case=case):
                response = invoke(adapter, request(case['input'], keyfile=case['keys']), timeout)
                observations.append(response)
                validation(response, 'archival', case['expected'])
            execute(case, check)

    if 'producer' in roles:
        # This is a disclosed reference cross-check, not an independent normative authority.
        from . import jep_validate_07 as core
        for case in manifest['producer_assertions']:
            def check(observations, case=case):
                template = read_json(suite_file(root, case['template']))
                response = invoke(adapter, {'operation': 'produce', 'unsigned_event': template,
                                           'signature_class': manifest['signature_class']}, timeout)
                event = core.parse_json(response['event_json'])
                if {k: v for k, v in event.items() if k != 'sig'} != template:
                    raise ValueError("Producer changed the assigned unsigned event")
                result = core.validate_event(event, keys=response['keys'])
                observations.append({'event_json': response['event_json'], 'keys': response['keys'], 'reference_result': result})
                validation({'result': result}, 'archival', {'status': 'valid', 'checks': {'cryptographic': 'pass'}})
            execute(case, check)

    def count(context):
        response = invoke(probe, {'operation': 'observe_effects', **context}, timeout)
        value = response.get('effect_count')
        if type(value) is not int or value < 0:
            raise ValueError("Probe must return a nonnegative integer effect_count")
        return value

    if 'acceptance' in roles:
        for case in manifest['acceptance_assertions']:
            def check(observations, case=case):
                with tempfile.TemporaryDirectory(prefix='jep-byoi-') as state_dir:
                    contexts = {domain: {'state_dir': state_dir, 'acceptance_domain': domain} for domain in ('a', 'b')}
                    for context in contexts.values():
                        if count(context) != 0:
                            raise ValueError("Test effect scope must initially be empty")
                    for step in case['steps']:
                        context = contexts[step.get('acceptance_domain', 'a')]
                        if step['operation'] == 'set_state_availability':
                            reply = invoke(adapter, {'operation': 'set_state_availability', 'available': step['available'], **context}, timeout)
                            if reply.get('configured') is not True:
                                raise ValueError("Adapter did not configure synthetic state availability")
                            observations.append({'operation': step['operation'], 'available': step['available']})
                            continue
                        if step['operation'] == 'concurrent':
                            req = request(step['input'], mode='acceptance', **context)
                            with ThreadPoolExecutor(max_workers=step['deliveries']) as executor:
                                futures = [executor.submit(invoke, adapter, req, timeout) for _ in range(step['deliveries'])]
                                replies = [future.result() for future in futures]
                            # Every call reaches the target; the harness never deduplicates inputs.
                            replies.append(invoke(adapter, req, timeout))
                            accepted = 0
                            for reply in replies:
                                result = validation(reply, 'acceptance')
                                outcome = result['acceptance']['outcome']
                                if outcome not in {'accepted', 'already_accepted', 'indeterminate'}:
                                    raise ValueError("Unexpected rejection of the valid concurrent fixture")
                                accepted += int(outcome == 'accepted')
                            if accepted != 1:
                                raise ValueError(f"Expected one accepted response after retry; got {accepted}")
                            observed = count(context)
                            observations.append({'operation': 'concurrent', 'results': replies, 'observed_effect_count': observed})
                        else:
                            reply = invoke(adapter, request(step['input'], mode=step['mode'], **context), timeout)
                            observations.append({'operation': 'validate', 'result': reply, 'acceptance_domain': context['acceptance_domain']})
                            validation(reply, step['mode'], step['expected'])
                            observed = count(context)
                            observations[-1]['observed_effect_count'] = observed
                        if observed != step['expected_effect_count']:
                            raise ValueError(f"Observed {observed} effects; expected {step['expected_effect_count']}")
            execute(case, check)

    totals = {name: sum(item['outcome'] == name for item in results) for name in ('pass', 'fail', 'unsupported')}
    total_assertions = sum(len(manifest[key]) for key in ('assertions', 'producer_assertions', 'acceptance_assertions'))
    outcome = 'fail' if totals['fail'] else 'incomplete' if totals['unsupported'] else 'pass'
    coverage = read_json(root / 'coverage.json')
    return {'report_format': 'jep-byoi-report/1', 'implementation': implementation,
            'generated_at': datetime.now(timezone.utc).isoformat(), 'jep_core': manifest['jep_core'], 'wire_major': '1',
            'conformance_draft': manifest['conformance_draft'], 'signature_class': manifest['signature_class'],
            'requested_roles': sorted(roles), 'profiles': ['jep-core-0.7'],
            'conformance_suite': {'name': manifest['name'], 'version': manifest['version'], 'digest': suite_digest},
            'runner': {'module_digest': digest(Path(__file__).read_bytes()),
                       'producer_oracle_digest': digest(Path(__file__).with_name('jep_validate_07.py').read_bytes())
                       if 'producer' in roles else None},
            'commands': {'adapter': adapter, 'effect_probe': probe}, 'effect_scope': effect_scope,
            'outcome': outcome, 'tests_passed': totals['pass'], 'tests_failed': totals['fail'],
            'tests_unsupported': totals['unsupported'], 'tests_not_selected': total_assertions - len(results),
            'certification': False, 'complete_core_coverage': False, 'coverage': coverage,
            'limitations': ['Pass applies only to executed assertions and declared modes/profiles.',
                            'Producer fixtures are cross-checked with the bundled reference verifier.',
                            'Acceptance effects are observed through the supplied probe; its correctness needs independent review.',
                            'Fresh processes test restart persistence, not power-loss or multi-host correctness.',
                            'This report does not establish truth, actor trust, authorization, legal validity or deployment security.'],
            'results': results}


def main(argv=None):
    parser = argparse.ArgumentParser(description='JEP BYOI: scoped, reproducible external implementation testing')
    commands = parser.add_subparsers(dest='command', required=True)
    export = commands.add_parser('export', help='Export the bundled suite to a new directory')
    export.add_argument('directory', type=Path)
    run = commands.add_parser('run')
    run.add_argument('--adapter', required=True, help='Trusted command as a JSON argv array; no shell expansion')
    run.add_argument('--implementation', required=True, type=Path, help='Implementation disclosure JSON')
    run.add_argument('--role', action='append', required=True, choices=['producer', 'verifier', 'acceptance'])
    run.add_argument('--effect-probe', help='Separate read-only effect observer command as a JSON argv array')
    run.add_argument('--effect-scope', help='Describe exactly which synthetic effect the probe observes')
    run.add_argument('--timeout', type=float, default=15)
    run.add_argument('--suite', type=Path, default=SUITE)
    run.add_argument('--report', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'export':
            manifest, suite_digest = load_suite(SUITE)
            shutil.copytree(SUITE, args.directory)
            print(json.dumps({'suite': manifest['name'], 'version': manifest['version'], 'digest': suite_digest}))
            return 0
        if not 0 < args.timeout <= 60:
            raise ValueError('Timeout must be greater than zero and at most 60 seconds')
        report = run_suite(args.suite, args.adapter, read_json(args.implementation), args.role,
                           probe=args.effect_probe, effect_scope=args.effect_scope, timeout=args.timeout)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({key: report[key] for key in ('outcome', 'tests_passed', 'tests_failed', 'tests_unsupported', 'tests_not_selected')}))
        return 0 if report['outcome'] == 'pass' else 1
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(2, f'BYOI configuration/artifact error: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
