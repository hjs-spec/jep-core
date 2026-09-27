"""No network or credential is needed for negative registry-check tests."""
import importlib.util
import base64
import hashlib
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('npm_release', ROOT / 'scripts/check_npm_release.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def metadata(data):
    return {'name': module.NAME, 'version': module.VERSION, 'dist': {
        'integrity': 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode(),
        'shasum': hashlib.sha1(data).hexdigest()}}


def test_rejects_other_identity():
    with pytest.raises(ValueError, match='identity'):
        module.validate({'name': '@hjs-spec/jep-sdk-js', 'version': '0.7.2'}, b'')


def test_rejects_other_bytes():
    with pytest.raises(ValueError, match='bytes'):
        module.validate(metadata(b'changed'), b'changed')


def test_checks_integrity_metadata(monkeypatch):
    data = b'unit-test-only'
    monkeypatch.setattr(module, 'SHA256', hashlib.sha256(data).hexdigest())
    record = metadata(data)
    assert module.validate(record, data) == module.SHA256
    record['dist']['integrity'] = 'sha512-invalid'
    with pytest.raises(ValueError, match='integrity'):
        module.validate(record, data)


def test_install_environment_strips_credentials(monkeypatch, tmp_path):
    for name in ('NODE_AUTH_TOKEN', 'NPM_TOKEN', 'GH_TOKEN', 'npm_config_registry'):
        monkeypatch.setenv(name, 'not-a-real-secret')
    env = module.clean_env(tmp_path)
    assert all(name not in env for name in ('NODE_AUTH_TOKEN', 'NPM_TOKEN', 'GH_TOKEN', 'npm_config_registry'))
    assert Path(env['NPM_CONFIG_USERCONFIG']).read_text() == ''


def test_rejects_foreign_registry_before_network():
    with pytest.raises(ValueError, match='host'):
        module.read_public('https://example.invalid/package.tgz')
