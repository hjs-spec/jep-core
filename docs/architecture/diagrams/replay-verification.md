# Scoped verification result

```mermaid
flowchart TB
    Archive["Archive with explicit format"]
    Core["Core syntax and signature checks"]
    Result["Core 0.7 status + independent checks"]
    Extra["Optional higher-scope validators"]
    Report["Combined report with unresolved checks"]
    Archive -->|preserve signed members| Core
    Core -->|report performed checks| Result
    Result -->|report Core outcome| Report
    Archive -->|supply extra evidence| Extra
    Extra -->|report supported scopes| Report
```

Core canonicalization and signature verification follow JEP rules. The current reference API reports only checks it actually performs. Additional profile, chain or policy checks require corresponding evidence and validators. Preserve the original signed payload during verification.
