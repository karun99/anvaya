# Architecture

Anvaya is a researcher-controlled memory layer for AI-assisted research. It
stores what the researcher has read, asked and preferred, then uses that context
to rank retrieval and ground generated answers.

## Layers

| Layer | Path | Responsibility |
|---|---|---|
| Web app | `apps/web` | React + TypeScript + Vite interface |
| API app | `apps/api` | Application service for the web client |
| FastAPI service | `api/index.py` | Public HTTP API: health, ingest, retrieve, chat |
| Memory core | `core/memory` | Persistent researcher context |
| Retrieval | `core/retrieval`, `core/ranking` | Candidate recall and personalised ranking |
| Events | `core/events` | Append-only activity stream used to update memory |
| Policies | `core/policies` | Retention, consent and access rules |
| AI gateway | `ai/gateway` | Multi-provider model routing |
| Embeddings | `ai/embeddings` | Vector generation and storage |
| Integrations | `integrations/` | MCP, OCR and agent-reach bridges |
| Skills | `skills/` | Reusable research workflows |

## Request flow

1. A document is ingested through the FastAPI service and split into passages.
2. Passages are embedded through `ai/embeddings` and stored in PostgreSQL with
   the `pgvector` extension.
3. A query triggers recall in `core/retrieval`; `core/ranking` re-orders the
   candidates using the researcher's stored context.
4. `ai/gateway` answers from the ranked passages only. Every reply carries the
   source passages that support it, so an unsupported claim is visible rather
   than hidden.
5. `core/events` records the interaction and updates memory according to the
   retention policy in `core/policies`.

## Trust boundaries

- The researcher owns the memory. Policies decide what is retained, and the
  memory can be exported or deleted through the API.
- Provider credentials live server-side; the browser never receives them.
- Retrieved passages are attached to the answer, so grounding can be audited.

## Verification

```bash
PYTHONPATH=api python -m unittest discover -s api/tests -v
```

The suite covers the cognitive-robotics validation module used by the
adversarial stress harness. CI runs the same command on every push.
