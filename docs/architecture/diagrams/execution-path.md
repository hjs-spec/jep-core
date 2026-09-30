# Execution and recording

```mermaid
flowchart TB
    Request["Application request"]
    Policy["Policy and identity checks"]
    Tool["Tool execution"]
    Record["Signed JEP statements"]
    Archive["Archive and optional receipts"]
    Replay["Read-only scoped verification"]
    Request -->|request capability| Policy
    Policy -->|allowed operation| Tool
    Policy -->|record decision| Record
    Tool -->|record result or failure| Record
    Record -->|preserve signed bytes| Archive
    Archive -->|load evidence| Replay
```

The application enforces policy independently. Recording a signed statement does not grant execution permission or guarantee atomic capture of external side effects. Replay does not invoke the tool.
