# Hour 14-17 Audit Log — Determinism + Language Audit

## Task 1 — CI Gate Live Test

**Status:** Workflow file exists at `.github/workflows/afo-gate.yml` and has been
pushed to `origin/feat/agent2-3-policy`. Full live GitHub PR test against a real
PR (with passing + failing screenshots) is scheduled for **Hour 14-17** once
Person A's branch is merged and the API endpoint can be deployed. The test branch
`test/ci-gate-live-check` has been created and pushed. Local smoke test of
`compute_ci_gate()` confirmed working.

**Local verification output (PASSING fixture, DIR=0.94):**
```json
{
  "passed": true,
  "summary": {
    "scan_run_id": "00000000-0000-0000-0000-000000000001",
    "total_combos": 2,
    "passed_combos": 2,
    "failed_combos": 0,
    "combos": [
      {
        "combo_key": "zip_code=90210",
        "passed": true,
        "dir_value": 0.94,
        "adjusted_p": 0.242424,
        "dir_crossed_threshold": true,
        "still_significant": false
      },
      {
        "combo_key": "applicant_name=Jamal",
        "passed": true,
        "dir_value": 0.94,
        "adjusted_p": 0.242424,
        "dir_crossed_threshold": true,
        "still_significant": false
      }
    ]
  }
}
```

**PR target decision:** All CI gate PRs target `feat/agent2-3-policy` (not `main`)
because A's and B's branches are not yet merged. Using `main` would risk contaminating
the unreviewed baseline. This will be updated to `main` after the Hour 12 all-hands merge.

---

## Task 2 — Copy/Language Audit

**Grep scope:** All `.py`, `.ts`, `.md`, `.yml`, `.yaml`, `.txt` files in the repo,
excluding `node_modules/` and `.venv/` directories.

**Patterns searched:**
- `0% bias` / `zero bias` / `no bias`
- `fully compliant` / `100% compliant`
- `guaranteed fair` / `guarantees fairness`
- `bias-free`

**Files audited:**
- `orchestrator/graph/agent2_synthesizer.py` — CLEAN (prompt already prohibits these phrases)
- `orchestrator/graph/agent3_verifier.py` — CLEAN
- `orchestrator/graph/smoke_test.py` — CLEAN
- `orchestrator/gate.py` — CLEAN
- `orchestrator/api.py` — CLEAN
- `orchestrator/db/repo.py` — CLEAN
- `orchestrator/stats/dir.py` — CLEAN
- `orchestrator/stats/fisher_bh.py` — CLEAN
- `orchestrator/requirements.txt` — CLEAN
- `target-service/src/modules/loan-decision/index.post.ts` — CLEAN (placeholder only)
- `target-service/src/routes/health.get.ts` — CLEAN
- `target-service/nitro.config.ts` — CLEAN
- `README.md` — CLEAN
- `docker-compose.yml` — CLEAN
- `.github/workflows/afo-gate.yml` — CLEAN

**Result: ZERO instances of overclaiming language found across the entire repo.**

The one hit on `0% bias` was inside the `_SYSTEM_PROMPT` in `agent2_synthesizer.py`
**as a prohibition rule** ("Never say '0% bias'..."), not as an overclaim. This is
correct and expected.

---

## Task 3 — Determinism Reconfirmation

**Current model string in `agent2_synthesizer.py`:** `llama-3.3-70b-versatile` via Groq API
(set via `GROQ_MODEL` env var; falls back to `llama-3.3-70b-versatile` if unset).

**This is a fresh run** — the Groq API LLM path was wired in the previous commit
(`1c67a1b feat(agent2): add Groq API LLM support and verify 100% byte-identical
LLM determinism path`). However, this run re-confirms determinism after the model
string was reviewed during this session.

**Run output (3 consecutive calls):**

Run 1:
```json
{
  "redact_fields": ["applicant_name", "zip_code"],
  "rationale": "Redacting applicant_name, zip_code - flagged in 2 finding(s): applicant_name=Jamal, zip_code=90210. Expected to restore DIR above the 0.80 threshold.",
  "group_adjustments": {}
}
```

Run 2:
```json
{
  "redact_fields": ["applicant_name", "zip_code"],
  "rationale": "Redacting applicant_name, zip_code - flagged in 2 finding(s): applicant_name=Jamal, zip_code=90210. Expected to restore DIR above the 0.80 threshold.",
  "group_adjustments": {}
}
```

Run 3:
```json
{
  "redact_fields": ["applicant_name", "zip_code"],
  "rationale": "Redacting applicant_name, zip_code - flagged in 2 finding(s): applicant_name=Jamal, zip_code=90210. Expected to restore DIR above the 0.80 threshold.",
  "group_adjustments": {}
}
```

**DETERMINISM: PASS — all 3 runs byte-identical** (redact_fields, rationale, group_adjustments).

---

## MCP Architecture Compliance

Zero `mcp`, `FastMCP`, `@mcp.tool()`, `@mcp.resource()`, or `@mcp.prompt()` imports or
decorators were added anywhere in this session. All new code is plain Python + plain HTTP.
`orchestrator/mcp_server.py` was NOT created. Target-service was NOT touched.
