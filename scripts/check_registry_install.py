"""Read-only registry/release hash comparison and clean installed-wheel smoke gate."""
from __future__ import annotations

import argparse
import hashlib
import platform
import re
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import venv

# Preserve the dated baseline; --current-release explicitly selects newer bytes.
PACKAGES = [
    ('jep-core-conformance', '0.7.4', 'hjs-spec/jep-core'),
    ('jep-agent-sdk', '2.1.5', 'hjs-spec/jep-agent-sdk'),
    ('jep-cli', '0.7.2', 'hjs-spec/cli'),
    ('jep-sdk-py', '0.7.0', 'hjs-spec/sdk-py'),
]
EXTRAS = [('hjs-spec/jep-quickstart', 'v0.7.0'), ('hjs-spec/sdk-go', 'v0.7.2'),
          ('hjs-spec/sdk-js', 'v0.7.1'), ('hjs-spec/jep-api', 'v0.8.4')]


def read(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in {
            'api.github.com', 'github.com', 'pypi.org', 'files.pythonhosted.org'}:
        raise ValueError('unexpected artifact URL host')
    headers = {'User-Agent': 'JEP-release-install-check'}
    if parsed.hostname == 'api.github.com' and os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    for attempt in range(6):
        try:
            with urlopen(Request(url, headers=headers), timeout=45) as response:
                return response.read()
        except Exception:
            if attempt == 5:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError('unreachable')


def release(repo, tag):
    return json.loads(read(f'https://api.github.com/repos/{repo}/releases/tags/{tag}'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def installation_set(current_release=False):
    """Default: historical baseline. Opt-in: the current coordinated release set."""
    packages, extras = list(PACKAGES), list(EXTRAS)
    if current_release:
        version = Path(__file__).resolve().parents[1].joinpath('VERSION').read_text().strip()
        if not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version):
            raise ValueError('invalid Core software version')
        packages[0] = ('jep-core-conformance', version, 'hjs-spec/jep-core')
        packages[1] = ('jep-agent-sdk', '2.1.6', 'hjs-spec/jep-agent-sdk')
        extras[-2] = ('hjs-spec/sdk-js', 'v0.7.2')
        extras[-1] = ('hjs-spec/jep-api', 'v0.8.5')
    return packages, extras


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', default='release-install-evidence')
    parser.add_argument('--current-release', action='store_true',
                        help='verify the coordinated current set, including the new npm scope')
    args = parser.parse_args(argv)
    packages, extras = installation_set(args.current_release)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = {'status': 'running', 'artifacts': [], 'packages': [],
              'platform': platform.platform(), 'python': platform.python_version(),
              'release_set': 'current-release' if args.current_release else 'published-baseline'}
    wheels = []
    try:
        for name, version, repo in packages:
            metadata = json.loads(read(f'https://pypi.org/pypi/{name}/{version}/json'))
            github = release(repo, 'v' + version)
            assets = {a['name']: a for a in github['assets']}
            files = [f for f in metadata['urls'] if f['packagetype'] in {'bdist_wheel', 'sdist'}]
            if len(files) != 2 or {f['packagetype'] for f in files} != {'bdist_wheel', 'sdist'}:
                raise ValueError(f'{name}: expected one wheel and one source')
            for file in files:
                filename = file['filename']
                if Path(filename).name != filename or file.get('yanked'):
                    raise ValueError('unsafe/yanked artifact')
                asset = assets[filename]
                actual = read(file['url'])
                hash_value = digest(actual)
                if hash_value != file['digests']['sha256'] or asset.get('digest') != 'sha256:' + hash_value:
                    raise ValueError(f'{filename}: registry/release hash mismatch')
                if digest(read(asset['browser_download_url'])) != hash_value:
                    raise ValueError('GitHub download differs from registry')
                path = output / 'python' / filename
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(actual)
                if filename.endswith('.whl'):
                    wheels.append(path)
                report['artifacts'].append({'file': str(path.relative_to(output)), 'sha256': hash_value,
                    'registry_url': file['url'], 'release_url': asset['browser_download_url']})
            report['packages'].append({'name': name, 'version': version, 'source': github['target_commitish']})
        for repo, tag in extras:
            github = release(repo, tag)
            for asset in github['assets']:
                filename = asset['name']
                if not filename.endswith(('.whl', '.tar.gz', '.tgz')):
                    continue
                if Path(filename).name != filename:
                    raise ValueError('unsafe artifact filename')
                data = read(asset['browser_download_url'])
                hash_value = digest(data)
                if asset.get('digest') != 'sha256:' + hash_value:
                    raise ValueError('release asset hash mismatch')
                path = output / repo.split('/')[1] / filename
                path.parent.mkdir(exist_ok=True)
                path.write_bytes(data)
                report['artifacts'].append({'file': str(path.relative_to(output)), 'sha256': hash_value,
                    'release_url': asset['browser_download_url']})
        if args.current_release:
            from check_npm_release import verify_npm
            report['npm'] = verify_npm(output / 'sdk-js')
        with tempfile.TemporaryDirectory() as temp:
            env = Path(temp) / 'venv'
            venv.EnvBuilder(with_pip=True).create(env)
            python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            subprocess.run([str(python), '-I', '-m', 'pip', '--isolated', 'install', '--no-cache-dir',
                '--index-url', 'https://pypi.org/simple', *map(str, wheels)], cwd=temp, check=True)
            freeze = subprocess.run([str(python), '-I', '-m', 'pip', 'freeze'], cwd=temp,
                                    check=True, capture_output=True, text=True)
            (output / 'installed-environment.txt').write_text(freeze.stdout, encoding='utf-8')
            smoke = Path(__file__).with_name('installed_smoke.py').resolve()
            result = subprocess.run([str(python), '-I', str(smoke)], cwd=temp,
                                    text=True, capture_output=True)
            (output / 'installed-smoke.json').write_text(result.stdout, encoding='utf-8')
            (output / 'installed-smoke.stderr.txt').write_text(result.stderr, encoding='utf-8')
            if result.returncode:
                print(result.stderr, file=sys.stderr)
            result.check_returncode()
            for command in ['jep-validate', 'jep-validate-07', 'jep-validate-06', 'jep']:
                executable = python.parent / (command + '.exe' if os.name == 'nt' else command)
                subprocess.run([str(executable), '--help'], cwd=temp, check=True, capture_output=True)
        report['status'] = 'pass'
        checksums = ''.join(item['sha256'] + '  ' + item['file'].replace('\\', '/') + '\n'
                            for item in report['artifacts'])
        (output / 'SHA256SUMS.txt').write_text(checksums, encoding='utf-8')
        instructions = ('# Verified installation set\n\nThis contains original release bytes, not newly built replacements. '
                        'Do not upload them again. Third-party dependencies still require network access.\n\n'
                        'Use a fresh environment; do not install historical jep-v06-conformance-seed beside current Core.\n\n'
                        '```sh\npython -m pip install ' + ' '.join(n + '==' + v for n, v, _ in packages) + '\n')
        if args.current_release:
            instructions += 'npm install @hjs-api-db/jep-sdk-js@0.7.2\n'
        instructions += ('```\n\nCore and Agent SDK run locally. HTTP clients need a separately configured API; '
                         'maintainer hosting is deferred. The local Agent SDK example exports public material, not a production identity. '
                         'See https://github.com/hjs-spec/jep-agent-sdk#local-create--export--independent-verification .\n')
        (output / 'INSTALL-README.md').write_text(instructions, encoding='utf-8')
    except Exception as exc:
        report['status'] = 'fail'
        report['error'] = type(exc).__name__ + ': ' + str(exc)
        raise
    finally:
        (output / 'registry-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
