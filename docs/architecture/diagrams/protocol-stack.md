# Recording and verification

```mermaid
flowchart TB
    App["Application"]
    Local["Local Agent SDK"]
    HTTP["HTTP API and clients"]
    Event["Signed Core 0.7 event"]
    Verifier["Core verifier"]
    App -->|record locally| Local
    App -->|request a service| HTTP
    Local -->|sign and export| Event
    HTTP -->|sign and export| Event
    Event -->|check with public keys| Verifier
```

Choose local recording when the application owns its key, or HTTP when a service
owns signing and acceptance state. Both paths export signed events that can be
checked with the Core verifier. Applications configure key trust and authorization.
