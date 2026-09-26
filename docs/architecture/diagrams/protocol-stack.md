# Protocol responsibilities

```mermaid
flowchart TB
    App["Application and SDK"]
    JEP["JEP: signed atomic J/D/T/V"]
    HJS["HJS: archives, privacy, receipts"]
    JAC["JAC: declared dependencies"]
    Policy["Application policy and identity"]
    App -->|create and verify| JEP
    App -->|enforce separately| Policy
    JEP -->|archive evidence| HJS
    JEP -->|declare relationships| JAC
    HJS -->|reference evidence| JAC
```

JEP means Judgment Event Protocol. HJS and JAC add distinct contracts; they do not replace Core canonicalization or automatically authorize tool execution. These arrows show possible integration relationships, not a mandatory processing sequence.
