# Trust responsibilities

```mermaid
flowchart TB
    Caller["Caller intent and credentials"]
    App["Application policy boundary"]
    Signer["Signing service and key trust"]
    Tool["Tool and external system"]
    Archive["Archive and evidence retention"]
    Verifier["Verifier with explicit trust policy"]
    Caller -->|request| App
    App -->|record statement| Signer
    App -->|permitted capability| Tool
    Signer -->|signed event| Archive
    Tool -->|outcome evidence| Archive
    Archive -->|provide evidence| Verifier
    Signer -->|trusted public-key source| Verifier
```

Caller identity, authorization, signing, external execution, storage and verification have distinct trust assumptions. Public-key availability is not sufficient trust by itself: the verifier needs a configured trusted source or key. API Level 1 does not bind who to the signer or approve the underlying action.
