# Schema entry points

Current generic filenames describe Core 0.7. Schemas check structure; use the
[validator](../reference-validator/README.md) for signatures and the applicable
profile for trust and acceptance requirements.

| File | Purpose |
| --- | --- |
| `jep-event.schema.json` | Full Core event structure |
| `jep-ref.schema.json` | Core event references |
| `jep-signature.schema.json` | Same signature container constraints as the event schema |
| `jep-extension.schema.json` | Same extension container constraints as the event schema |
| `jep-profile.schema.json` | Profile description |
| `jep-validation-result.schema.json` | Validation results |
| `jep-byoi-report.schema.json` | BYOI report format 1, separate from the Core wire version |

The previous 0.6 signature/extension helpers are preserved under
[legacy/0.6](legacy/0.6/README.md). The active generic helpers now use 0.7 identifiers.
The [published specifications](../docs/SPECIFICATION-SOURCES.md) control requirements.
