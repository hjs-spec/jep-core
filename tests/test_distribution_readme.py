"""Registry README links must resolve without a GitHub-relative base URL."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_distribution_readme_links_are_absolute():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    targets = re.findall(r'\]\(([^)]+)\)', text)
    assert targets
    assert all(url.startswith(('https://', '#')) for url in targets)


def test_registry_install_is_distinct_from_source_development():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'python -m pip install jep-core-conformance' in text
    assert '## Develop and test from source' in text
    assert 'Do not install historical `jep-v06-conformance-seed` alongside' in text


def test_distribution_readme_uses_current_validator_subcommand():
    text = (ROOT / 'README.md').read_text(encoding='utf-8')
    assert 'jep-validate validate jep-example/vectors/J-basic.json --keys jep-example/keys.json' in text
    assert 'jep-validate event.json --keys keys.json' not in text
