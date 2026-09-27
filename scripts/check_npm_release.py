"""Read-only npm check for the reviewed new-scope SDK; no publishing credentials."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

NAME = '@hjs-api-db/jep-sdk-js'
VERSION = '0.7.2'
SHA256 = '18e557ea6cbe6c46b42f18ddfb2368d4f7a3eb1ab75916fd7a0031d128010e40'
TARBALL = 'hjs-api-db-jep-sdk-js-0.7.2.tgz'
REGISTRY = 'https://registry.npmjs.org/'


def read_public(url: str) -> bytes:
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname != 'registry.npmjs.org':
        raise ValueError('unexpected npm host')
    for attempt in range(6):
        try:
            with urlopen(Request(url, headers={'Accept': 'application/json'}), timeout=30) as response:
                if urlsplit(response.url).hostname != 'registry.npmjs.org':
                    raise ValueError('unexpected npm redirect')
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in (404, 429, 500, 502, 503, 504):
                raise
            if attempt == 5:
                raise
            time.sleep(5)
    raise RuntimeError('unreachable')


def validate(metadata: dict, data: bytes) -> str:
    if metadata.get('name') != NAME or metadata.get('version') != VERSION:
        raise ValueError('npm identity mismatch')
    actual = hashlib.sha256(data).hexdigest()
    if actual != SHA256:
        raise ValueError('npm bytes differ from reviewed GitHub release')
    sri = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode('ascii')
    if metadata['dist'].get('integrity') != sri or metadata['dist'].get('shasum') != hashlib.sha1(data).hexdigest():
        raise ValueError('npm integrity metadata mismatch')
    return actual


def clean_env(home: Path) -> dict:
    allowed = {'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT', 'TMP', 'TEMP', 'TMPDIR', 'LANG', 'LC_ALL'}
    env = {k: v for k, v in os.environ.items() if k.upper() in allowed}
    (home / 'user.npmrc').write_text('', encoding='utf-8')
    (home / 'global.npmrc').write_text('', encoding='utf-8')
    env.update(HOME=str(home), USERPROFILE=str(home),
               NPM_CONFIG_USERCONFIG=str(home / 'user.npmrc'),
               NPM_CONFIG_GLOBALCONFIG=str(home / 'global.npmrc'),
               NPM_CONFIG_CACHE=str(home / 'cache'), NPM_CONFIG_UPDATE_NOTIFIER='false')
    return env


def verify_npm(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    metadata = json.loads(read_public(REGISTRY + '@hjs-api-db%2fjep-sdk-js/' + VERSION))
    if metadata.get('name') != NAME or metadata.get('version') != VERSION:
        raise ValueError('npm identity mismatch')
    data = read_public(metadata['dist']['tarball'])
    actual = validate(metadata, data)
    archive = output / TARBALL
    if not archive.is_file() or archive.read_bytes() != data:
        raise ValueError('independently downloaded GitHub and npm archives differ')
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    node = shutil.which('node')
    if not npm or not node:
        raise RuntimeError('Node.js and npm are required for the current installation set')
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        home = root / 'home'
        home.mkdir()
        env = clean_env(home)
        for attempt in range(6):
            work = root / str(attempt)
            work.mkdir()
            install = subprocess.run([npm, 'install', NAME + '@' + VERSION, '--ignore-scripts', '--no-audit',
                                      '--no-fund', '--package-lock=false', '--prefer-online', '--registry=' + REGISTRY],
                                     cwd=work, env=env, capture_output=True, text=True, timeout=120)
            log = install.stdout + install.stderr
            (output / ('install-' + str(attempt) + '.txt')).write_text(log, encoding='utf-8')
            if install.returncode == 0:
                break
            if attempt == 5 or not any(code in log for code in ('E404', 'ETARGET')):
                install.check_returncode()
            time.sleep(5)
        smoke = subprocess.run([node, '--input-type=module', '-e',
            "import {JEPClient,JEP_CORE_PROFILE} from '@hjs-api-db/jep-sdk-js'; if(typeof JEPClient!=='function'||JEP_CORE_PROFILE!=='jep-core-0.7') throw Error('Bad installed SDK');"],
            cwd=work, env=env, check=True, capture_output=True, text=True, timeout=30)
        (output / 'import.txt').write_text(smoke.stdout + smoke.stderr, encoding='utf-8')
    report = {'name': NAME, 'version': VERSION, 'sha256': actual,
              'registry_url': metadata['dist']['tarball'], 'anonymous_install': 'pass', 'installed_import': 'pass',
              'limits': 'No live API, actor identity, business outcome or OIDC publication is tested.'}
    (output / 'npm-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report
