# Day 5 — Evaluation & governance checklist (Milestone 4)

| Area | Check | Evidence |
|---|---|---|
| Functionality | Capstone query returns prediction, history, cited evidence, compliance status, draft work order | `lab5_4_capstone.py` PASS lines |
| Grounding | Every claim cited; "not found" when evidence is missing | `lab4_3_rag_chain.py` |
| Grounding | ML numbers in the report equal the model output (the LLM only explains) | `lab5_4` check "ML numbers unchanged" |
| Safety | Never certifies airworthiness; refusal enforced in code | `safety.py`, `lab2_2` checklist |
| Security | Injection defended, PII masked | `lab4_5_security.py` |
| Security | Technician cannot approve; inspector approval required | `lab5_5_security.py` |
| Security | Tool allowlist; safe mode drafts nothing | `lab5_5_security.py` |
| Security | MCP server rejects a wrong token | `lab5_3_mcp.py` |
| Accountability | Audit log: plan, every tool call, draft, approval/rejection with approver | `GET /agent/audit` |
| Explainability | Report shows sensor drivers and the documents used | Agent tab, citations |
| Performance | Tracing on; latency p50/p95 and cost per query measured; one optimisation shown | `lab5_6_loadtest.py`, `GET /metrics` |
| Deployment | `docker compose up --build` runs API + UI; capstone query works in the containers | Lab 5.7 |
| Data | Only synthetic / public data; no secrets in Git (`.env` ignored) | `.gitignore` |

Accountability rule for aviation: AeroGuard is advisory. A certificated person makes and signs every
airworthiness decision; the audit log records who approved what, and when.
