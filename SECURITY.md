# Security reporting

Report security-sensitive findings privately to the document author at
**signal@humanjudgment.org** (the contact in the published companion drafts).
Use a subject such as `JEP security report: <short description>`.
Do not put exploit details or secrets in a public issue or pull request.

Include the affected repository/package version or commit, the relevant draft
and profile, a minimal reproduction with synthetic data, the expected and
observed behavior, and impact. Distinguish signature verification, actor/key
binding, acceptance effects and application policy. Do not test a live service
without its operator's authorization.

Core 0.7 and the current implementation path are the active maintenance target.
Core 0.6 assets are retained for explicit historical verification; identify the
legacy mode when reporting one. Dependency and tooling issues are also welcome.

The maintainer and reporter can coordinate validation, remediation and public
disclosure. No response-time or bounty commitment is implied. This file provides
an email route; it does not assume GitHub private vulnerability reporting is
enabled. Never send production private keys or unnecessary personal data.
