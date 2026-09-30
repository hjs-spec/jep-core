"""Verify notices/data in distributions and exercise the standalone installed wheel."""
from email.parser import BytesParser
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def check():
    wheel, = (ROOT / 'dist').glob('*.whl')
    source, = (ROOT / 'dist').glob('*.tar.gz')
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_name, = [name for name in names if name.endswith('.dist-info/METADATA')]
        metadata = BytesParser().parsebytes(archive.read(metadata_name))
        assert metadata['License-Expression'] == 'BSD-3-Clause'
        for suffix in ('/licenses/LICENSE', '/licenses/LICENSING.md', '/licenses/licenses/IETF-CODE-COMPONENTS.txt'):
            assert any(name.endswith(suffix) for name in names), suffix
        assert 'jep_conformance/byoi_suite/manifest.json' in names
        assert 'jep_conformance/byoi_suite/report.schema.json' in names
        assert 'jep_conformance/byoi_suite/vectors/duplicate-member.json' in names
    with tarfile.open(source) as archive:
        names = archive.getnames()
        for suffix in ('/LICENSE', '/LICENSING.md', '/licenses/IETF-CODE-COMPONENTS.txt', '/reference-validator/byoi_suite/manifest.json'):
            assert any(name.endswith(suffix) for name in names), suffix
    with tempfile.TemporaryDirectory(prefix='jep-byoi-installed-') as temporary:
        work = Path(temporary)
        environment = work / 'venv'
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        subprocess.run([str(python), '-m', 'pip', 'install', str(wheel)], check=True, cwd=work)
        code = "import pathlib,jep_conformance.byoi as b; print(pathlib.Path(b.__file__).resolve())"
        installed = Path(subprocess.check_output([str(python), '-c', code], cwd=work, text=True).strip())
        assert installed.is_relative_to(environment.resolve()), installed
        subprocess.run([str(python), '-m', 'jep_conformance.byoi', 'export', str(work / 'suite')], cwd=work, check=True)
        descriptor = {'name': 'installed-reference-wrapper', 'version': metadata['Version'],
                      'source': wheel.name, 'revision': 'locally-built-wheel', 'independence': 'reference-wrapper',
                      'reused_components': ['jep-core-conformance']}
        (work / 'implementation.json').write_text(json.dumps(descriptor), encoding='utf-8')
        scripts = environment / ('Scripts' if sys.platform == 'win32' else 'bin')
        cli = scripts / ('jep-byoi.exe' if sys.platform == 'win32' else 'jep-byoi')
        # Execute the commands users actually copy from the installed README.
        first_use = re.search(r'^## Verify your first event\r?\n(.*?)(?=^## |\Z)',
                              metadata.get_payload(), flags=re.S | re.M)
        assert first_use, 'Installed README must contain the first-use section'
        blocks = re.findall(r'```sh\r?\n(.*?)```', first_use.group(1), flags=re.S)
        assert len(blocks) == 1, 'First-use section must contain one runnable command block'
        first = blocks[0].strip().splitlines()
        assert shlex.split(first[0]) == ['python', '-m', 'pip', 'install', 'jep-core-conformance==' + metadata['Version']]
        assert any(line.startswith('jep-validate ') for line in first[1:]), 'First-use commands must validate an event'
        for line in first[1:]:
            argv = shlex.split(line)
            argv[0] = str(scripts / (argv[0] + ('.exe' if sys.platform == 'win32' else '')))
            result = subprocess.run(argv, cwd=work, check=True, capture_output=True, text=True)
            if line.startswith('jep-validate '):
                validation = json.loads(result.stdout)
                assert validation['status'] == 'valid' and validation['checks']['cryptographic'] == 'pass'
        # The full reference demonstration is documented in the BYOI guide.
        subprocess.run([str(cli), 'demo', '--report', 'byoi-reference-report.json'],
                       cwd=work, check=True, capture_output=True, text=True)
        demo = json.loads((work / 'byoi-reference-report.json').read_text())
        assert demo['tests_passed'] == 29 and demo['outcome'] == 'pass'
        assert demo['implementation']['version'] == metadata['Version']
        assert demo['implementation']['independence'].startswith('reference-wrapper')
        assert demo['tests_not_selected'] == 8 and demo['certification'] is False
        subprocess.run([str(cli), 'run', '--implementation', 'implementation.json', '--role', 'producer',
                        '--role', 'verifier', '--suite', str(work / 'suite'),
                        '--adapter', json.dumps([str(python), '-m', 'jep_conformance.byoi_reference_adapter']),
                        '--report', 'report.json'], cwd=work, check=True)
        report = json.loads((work / 'report.json').read_text())
        assert report['outcome'] == 'pass' and report['tests_passed'] == 29
        assert report['tests_not_selected'] == 8 and report['complete_core_coverage'] is False
    print('BSD/IETF notices and standalone installed BYOI producer/verifier flow verified.')


if __name__ == '__main__':
    check()
