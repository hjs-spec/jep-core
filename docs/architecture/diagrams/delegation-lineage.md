# Declared delegation and enforcement

```mermaid
flowchart TB
    Parent["Principal declares delegation"]
    D["Signed D event with scope"]
    Policy["Delegate policy and trust"]
    Tool["Allowed tool operation"]
    Evidence["Outcome evidence and references"]
    Parent -->|declare| D
    D -->|input to evaluation| Policy
    Policy -->|authorize locally| Tool
    Tool -->|record outcome| Evidence
    D -->|declared relationship| Evidence
```

A D statement records a delegation claim. Identity binding, actual permissions and external outcomes require independent evidence. JAC may describe declared dependencies; neither a declaration nor its graph proves real causality or valid authority.
