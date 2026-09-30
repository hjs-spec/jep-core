"""Offline publication provenance and adoption-entry consistency checks."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from jep_conformance import byoi

ROOT = Path(__file__).resolve().parents[1]


def check(root=ROOT):
    for directory in ('conformance-02', 'profiles-01'):
        folder = root / 'releases' / directory
        provenance = json.loads((folder / 'provenance.json').read_text())
        sums = dict(line.split(maxsplit=1)[::-1] for line in (folder / 'SHA256SUMS').read_text().splitlines())
        for artifact in provenance['artifacts']:
            name = artifact['file']
            assert '/' not in name and '\\' not in name
            raw = (folder / name).read_bytes()
            actual = hashlib.sha256(raw).hexdigest()
            assert actual == artifact['sha256'] == sums[name], name
            assert artifact['source'] == 'https://www.ietf.org/archive/id/' + name
            if name.endswith('.xml'):
                assert ET.fromstring(raw).attrib['docName'] == provenance['document']
    manifest, _ = byoi.load_suite(root / 'reference-validator/byoi_suite')
    report_schema = json.loads((root / 'schemas/jep-byoi-report.schema.json').read_text())
    assert report_schema == json.loads((root / 'reference-validator/byoi_suite/report.schema.json').read_text())
    for group in ('assertions', 'producer_assertions', 'acceptance_assertions'):
        for case in manifest[group]:
            assert all(source['document'] == 'draft-wang-jep-judgment-event-protocol-07' for source in case['requirements'])
    entries = ['README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'LICENSING.md',
               'docs/README.md', 'docs/ONE-PAGE-OVERVIEW.md', 'docs/POSITIONING.md',
               'docs/BYOI-CONFORMANCE.md', 'docs/INTEROPERABILITY-REPORT.md',
               'docs/INTEROPERABILITY-REPORT-TEMPLATE.md', 'docs/SPECIFICATION-SOURCES.md']
    for entry in entries:
        source = root / entry
        for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                continue
            path = target.split('#', 1)[0]
            assert (source.parent / path).exists(), f'{entry}: broken link {target}'
    print('Companion provenance, BYOI manifest/schema and adoption links verified.')


if __name__ == '__main__':
    check()
