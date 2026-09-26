"""Current 0.7 signed-artifact interoperability; no production policy/acceptance claim."""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def command(argv, **kwargs):
    process = subprocess.run(argv, text=True, capture_output=True, check=True, **kwargs)
    return json.loads(process.stdout)


def run(workspace):
    for repo in ("jep-api", "jep-agent-sdk", "sdk-py", "Agent-Blackbox/src"):
        sys.path.insert(0, str(workspace / repo))
    from jep.client import JEPEvent
    from jep_agent.core.event import build_event, sign_event, event_hash as agent_hash
    from jep_agent.core.verifier import JEPVerifier
    from agent_blackbox.jep import JEPEvent as BlackboxEvent
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    from jsonschema import Draft202012Validator

    core = load("interop_core07", ROOT / "reference-validator/jep_validate_07.py")
    binding = load("interop_binding02", workspace / "tsto-spec/scripts/check-binding-02.py")
    data = core.load_json(workspace / "tsto-spec/examples/binding-02/vectors.json")
    events, keys = copy.deepcopy(data["events"]), copy.deepcopy(data["keys"])
    # An independent producer supplies explicit empty signed members that Go used to drop.
    key = Ed25519PrivateKey.generate()
    kid = "urn:example:ephemeral-interop-key"
    keys[kid] = {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": core.b64u(key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)),
    }
    events.append(
        sign_event(
            build_event("J", "did:example:interop", {"value": 1e20}, ext={}, ext_crit=[]), key, kid=kid
        )
    )
    with tempfile.TemporaryDirectory(prefix="jep07-interop-") as directory:
        temporary = Path(directory)
        os.environ["JEP_STATE_DIR"] = str(temporary / "state")
        api = load("interop_api07", workspace / "jep-api/main.py")
        for key_id, jwk in keys.items():
            api.STATE.register_public_key(key_id, jwk)
        node_script = temporary / "transport.mjs"
        node_script.write_text("""import fs from 'node:fs';
const {JEPClient} = await import(process.argv[2]);
const events = JSON.parse(fs.readFileSync(0,'utf8'));
const sent = [];
const client = new JEPClient({fetchImpl: async (url,options) => {
  sent.push(JSON.parse(options.body).event);
  return {ok:true,text:async()=>'{"status":"valid"}'};
}});
for (const event of events) await client.verifyEvent({event});
process.stdout.write(JSON.stringify(sent));
""")
        javascript = command(
            ["node", str(node_script), (workspace / "sdk-js/src/index.js").as_uri()], input=json.dumps(events)
        )
        (temporary / "go.mod").write_text(
            "module jep-interop-test\n\ngo 1.21\n\nrequire github.com/hjs-spec/sdk-go v0.0.0\nreplace github.com/hjs-spec/sdk-go => "
            + str(workspace / "sdk-go")
            + "\n"
        )
        (temporary / "main.go").write_text("""package main
import("encoding/json";"os";jep "github.com/hjs-spec/sdk-go")
func main(){var events []jep.JEPEvent;if err:=json.NewDecoder(os.Stdin).Decode(&events);err!=nil{panic(err)};if err:=json.NewEncoder(os.Stdout).Encode(events);err!=nil{panic(err)}}
""")
        golang = command(["go", "run", "."], cwd=temporary, input=json.dumps(events))
        transports = {
            "original": events,
            "python": [JEPEvent.from_dict(e).to_dict() for e in events],
            "javascript": javascript,
            "go": golang,
            "blackbox": [BlackboxEvent.from_dict(e).to_dict() for e in events],
        }
        binding_verifier = binding.FixtureVerifier(core, data["keys"])
        result_schema = Draft202012Validator(
            core.load_json(ROOT / "schemas/jep-validation-result.schema.json")
        )
        for transport, received in transports.items():
            assert len(received) == len(events)
            for i, event in enumerate(received):
                expected_hash = core.event_hash(events[i])
                assert core.event_hash(event) == expected_hash, (transport, i, "hash")
                protected = core.parse_json(core.b64u_decode(event["sig"].split(".")[0], "header").decode())
                public = Ed25519PublicKey.from_public_bytes(
                    core.b64u_decode(keys[protected["kid"]]["x"], "key")
                )
                results = [
                    core.validate_event(event, keys=keys),
                    api.validate_event_07(event),
                    JEPVerifier().verify_result(event, public),
                ]
                for result in results:
                    assert result["status"] == "valid", (transport, i, result)
                    assert result["checks"]["cryptographic"] == "pass"
                    assert result["event_hash"] == expected_hash
                    result_schema.validate(result)
                assert agent_hash(event) == expected_hash
                assert BlackboxEvent.from_dict(event).verify(public)
                if i < len(data["events"]):
                    binding_verifier.validate(event, data["tsto"], events[: len(data["events"])])
        # Core-valid does not imply policy-reference equality or full TSTO validity.
        bad = next(c["event"] for c in data["hostile"] if c["name"] == "V-wrong-policy")
        assert api.validate_event_07(bad)["status"] == "valid"
        try:
            binding_verifier.validate(bad, data["tsto"], data["events"])
        except binding.BindingFailure as exc:
            assert exc.code == "POLICY_REFERENCE"
        else:
            raise AssertionError("wrong TSTO policy accepted")
        for event in [{}, {**events[0], "id": 3}, {**events[0], "who": ""}]:
            for result in [
                core.validate_event(event),
                api.validate_event_07(event),
                JEPVerifier().verify_result(event),
            ]:
                assert result["status"] == "invalid"
                assert result["event_identity"] is None
                result_schema.validate(result)
    return {
        "core": "0.7",
        "binding": "02",
        "signedEvents": len(events),
        "transportPaths": list(transports),
        "signedArtifactRoundTrips": len(events) * len(transports),
        "verifiers": ["core", "api", "agent-sdk", "blackbox"],
        "bindingReferenceChecks": len(data["events"]) * len(transports),
        "malformedIdentityResultSchema": True,
        "scope": "signed artifact transport, baseline cryptography and hashes, Binding/02 structural/reference checks; domain policy and external truth not evaluated",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=ROOT.parent)
    args = parser.parse_args()
    print(json.dumps(run(args.workspace.resolve()), indent=2))
