"""Offline repository consistency and published -07 integrity gate."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Published snapshots are immutable. Future edits belong in a new revision.
FROZEN = {'releases/draft-07/draft-wang-jep-judgment-event-protocol-07.xml': '601809b4053d485fa68367db22f5e43919e859c4f0227609b8f851c627e9caab', 'ietf-rendered/draft-wang-jep-judgment-event-protocol-07.xml': '601809b4053d485fa68367db22f5e43919e859c4f0227609b8f851c627e9caab', 'ietf-rendered/draft-wang-jep-judgment-event-protocol-07.txt': '2d6dbb3725a35a009e61f574031843395a41db4175d1b41961f6ee5894594c76', 'draft-wang-jep-judgment-event-protocol-07.md': '1d6d04f1003914199b510b0cd51f5ac143af0e4e6bc21d8d82d25376551c1741'}


def check(root=ROOT):
    companion_frozen = {
        'releases/conformance-02/draft-wang-jep-conformance-02.xml': '7f1d1afd31b92a013e4d00b0f144eb433f20937aa709708d1cb70ac6ae2ace34',
        'releases/conformance-02/draft-wang-jep-conformance-02.txt': '1337d661017ec7d8d1bf86606f98b8a494281693c2ef99d0bd09167b0bb55fd9',
        'releases/profiles-01/draft-wang-jep-profiles-01.xml': 'f18f50ba52975ee82c0d36a8a8f5004135fbcfe8e60d4f84f79152cf638383a3',
        'releases/profiles-01/draft-wang-jep-profiles-01.txt': '9cdf2dc7db3180ceaefe927cfe21d260f955a0298a9bf5f09bba7f4ea64c5c3c',
    }
    for name, expected in FROZEN.items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen publication changed: {name}; create a new draft revision")
    for name, expected in companion_frozen.items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Frozen companion publication changed: {name}")
    checksum = (root / "releases/draft-07/SHA256SUMS").read_text().split()[0]
    if checksum != FROZEN["releases/draft-07/draft-wang-jep-judgment-event-protocol-07.xml"]:
        raise ValueError("Published -07 checksum changed")
    current = json.loads((root / "test-manifest.json").read_text())
    versioned = json.loads((root / "test-manifest-0.7.json").read_text())
    if current != versioned:
        raise ValueError("Default conformance manifest must match current 0.7 manifest")
    for name in ("test-manifest-0.7.json", "test-manifest-0.6.json"):
        manifest = json.loads((root / name).read_text())
        for case in manifest["cases"]:
            for field in ("path", "keys"):
                if case.get(field) and not (root / case[field]).is_file():
                    raise ValueError(f"Missing {field} in {name}: {case[field]}")
    print("Published -07 hashes, current manifest, and current/legacy vector paths verified.")


if __name__ == "__main__":
    check()
