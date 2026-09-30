# Validation evidence

Generate current results with `jep-byoi demo --report byoi-reference-report.json`
or the [external implementation path](../docs/BYOI-CONFORMANCE.md). Reports name
the actual implementation, suite digest and tested roles.

Current CI evidence is attached to the [conformance workflow](https://github.com/hjs-spec/jep-core/actions/workflows/conformance.yml)
and [published-install workflow](https://github.com/hjs-spec/jep-core/actions/workflows/release.yml).
Select a run for the version/commit being evaluated; an earlier pass is not a new test.

The old `local-validation-report.json` described Core 0.6 and contained unrelated
environment startup failures. Its unmodified original remains in
[the v0.7.6 snapshot](https://github.com/hjs-spec/jep-core/blob/v0.7.6/reports/local-validation-report.json).
It is historical evidence, not a current validation report. It is removed from the
active tree rather than copied with irrelevant logs into new distributions.
