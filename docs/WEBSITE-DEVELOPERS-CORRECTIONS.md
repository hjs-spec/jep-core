# Developers page publication correction

Target: https://www.judgmentevent.org/developers

This publication patch aligns explanatory copy with frozen Core -07. It does
not change protocol requirements. Apply in the existing website source/project.

| Location | Existing text | Replacement |
| --- | --- | --- |
| `who` description | Subject declared by the event. The field alone does not prove real-world identity. | Actor declared by the event. The field alone does not prove real-world identity. |
| `when` description | Time declared by the subject. | Event time declared by the actor. |
| Event sketch `who` value | `<declared subject>` | `<declared actor>` |
| `sig` description | Signature container. Covers the exact signed artifact identified by Event Hash. | Signature container. The signing payload is the JCS-canonicalized unsigned event with `sig` omitted; the declared signature class defines its signature input. Event Hash identifies the full signed event, including `sig`. |

After deployment, check both rendered desktop/mobile copy and the event sketch.
Confirm no remaining copy equates Event Hash with the signing input. Retain the
published source revision and deployment URL as evidence.

References: Core -07 sections “Signing Input and Event Hash” and field definitions;
[implementer guide](IMPLEMENTER-GUIDE.md). Publication remains pending until the
existing JEP website project is available; this file is not a deployment claim.
