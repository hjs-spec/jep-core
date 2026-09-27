"""Release verification names the exact set; it never treats old bytes as new."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('registry_install', ROOT / 'scripts/check_registry_install.py')
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


def test_default_is_already_published_baseline():
    packages, extras = registry.installation_set()
    assert packages[0][1] == '0.7.4'
    assert packages[1][1] == '2.1.5'
    assert extras[-1] == ('hjs-spec/jep-api', 'v0.8.4')


def test_post_publication_targets_actual_core_version_and_paired_fixes():
    packages, extras = registry.installation_set(True)
    assert packages[0][1] == (ROOT / 'VERSION').read_text().strip()
    assert packages[1][1] == '2.1.6'
    assert extras[-1] == ('hjs-spec/jep-api', 'v0.8.5')
    assert registry.PACKAGES[0][1] == '0.7.4'
    assert registry.EXTRAS[-1][1] == 'v0.8.4'
