# Core 0.7 interoperability reports

Use the [BYOI path](BYOI-CONFORMANCE.md) to generate a report. Its JSON shape is
specified in [jep-byoi-report.schema.json](../schemas/jep-byoi-report.schema.json)
and is an executable implementation of scoped reporting under
[Conformance -02 section 12](https://datatracker.ietf.org/doc/html/draft-wang-jep-conformance-02#section-12).
The report format is not a new JEP wire format or Core requirement.

## What a report says

- Implementation name, version, source/revision, reused components and claimed independence.
- Core version, conformance draft, signature class, selected roles and profiles.
- Exact suite version/digest, runner digest and producer cross-check oracle digest.
- Each assertion's normative source, observed output, result and failure reason.
- For acceptance: the declared synthetic effect and separately observed effect counts.
- Passed, failed, unsupported and not-selected counts, plus partial/uncovered areas.

`pass` means the selected assertions passed. `incomplete` means a selected
operation was unsupported. `fail` includes assertion failures, malformed adapter
output and execution failures. A role not selected is not claimed as tested.
A reference-wrapper result is not an independent implementation result.

The bundled v1 suite has 25 verifier assertions, four producer checks and eight
acceptance scenarios. It is deliberately labeled partial coverage. In particular,
it does not claim reference resolution, trust establishment, freshness/audience
profiles, profile composition, chain/policy verification, power-loss durability
or multi-host correctness. These need separate evidence under the applicable
profile and deployment. Counts alone do not establish full conformance.

## Submit and reproduce

1. Preserve the exported suite, disclosure JSON and exact adapter/probe revision.
2. Run the documented command and keep the generated report, including failures.
3. Check that it contains only synthetic fixtures and no secrets or private paths
   you do not intend to publish. Command arguments are recorded; never put tokens
   or credentials in those arguments. Do not hand-edit failures into passes.
4. Attach the report or link a stable artifact in the
   [interop issue form](https://github.com/hjs-spec/jep-core/issues/new?template=interoperability-result.yml).
   State the exact reproduction command and known limitations.

Maintainers can review the evidence, request clarification and record whether
results were independently reproduced. Publication is not certification,
endorsement, a production-security assessment, or proof of external business facts.
Do not execute submitted code automatically from a public issue or PR.
