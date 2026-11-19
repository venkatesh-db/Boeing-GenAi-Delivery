# OWASP Top 10 for LLM Applications (2025) — where AeroGuard addresses each risk

| # | Risk | AeroGuard defence | Where |
|---|---|---|---|
| LLM01 | Prompt injection (direct and indirect) | Injection screening, chunks sanitised, sources wrapped as data, output checks | `rag/guardrails.py`, `rag/chain.py`, Lab 4.5 |
| LLM02 | Sensitive information disclosure | PII redaction on questions, sources and answers; role-based document access | `guardrails.redact_pii`, `rag/store.py` (`access`), Lab 4.5 |
| LLM03 | Supply chain | Pinned `requirements.txt`; `mcp<2` pin; local FAISS, no third-party vector DB | `requirements.txt` |
| LLM04 | Data and model poisoning | Upload type/size limits, injection warnings on upload, trusted `data/docs` only | `routers/rag.py` |
| LLM05 | Improper output handling | Pydantic validation of every JSON output; airworthiness guard on every answer | `llm.chat_json`, `safety.py` |
| LLM06 | Excessive agency | Tool allowlist, read-only tools, human approval before a work order, safe mode | `security.py`, `agent/graph.py` (Day 5) |
| LLM07 | System prompt leakage | No secrets in prompts; "reveal your instructions" screened | `prompts.py`, `guardrails.py` |
| LLM08 | Vector and embedding weaknesses | Access label on every chunk, filtered at retrieval time | `rag/store.py`, Lab 4.5 step 4 |
| LLM09 | Misinformation | Mandatory citations; no-answer policy ("no answer beats a wrong answer") | `rag/qa.py`, Lab 4.3 |
| LLM10 | Unbounded consumption | Request/upload size limits, step limit for the agent, caching, cost table | `app.py`, `graph.py` `MAX_STEPS`, `/metrics` (Day 5) |

Discussion: ITAR/EAR export control and data residency are handled as data labels plus hosting policy;
the policy itself belongs to the company's own security and trade-compliance teams.
