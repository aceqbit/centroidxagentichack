# Agent 2 & Agent 3 — Person A Hour 14 Handoff Reference

## 1. Verbatim Function Signatures
```python
synthesize_policy(scan_run_id: str) -> dict
verify_fix(scan_run_id: str) -> dict
```

## 2. Import Paths for `mcp_server.py`
```python
from graph.agent2_synthesizer import synthesize_policy
from graph.agent3_verifier import verify_fix
```

## 3. Function Behavior & Internal Pipeline

### `synthesize_policy(scan_run_id: str) -> dict`
Reads open findings for `scan_run_id` from Postgres (`finding` table), sends them to an LLM at `temperature=0` with a calibrated prompt, and inserts the generated policy into Postgres (`mitigation_policy` and `mitigation_edges` tables). It marks processed findings as resolved and returns the policy summary dict.

### `verify_fix(scan_run_id: str) -> dict`
Fetches the active policy and associated findings for `scan_run_id`, runs post-patch statistical checks (Disparate Impact Ratio and Fisher's exact test with Benjamini-Hochberg FDR correction across combos), and returns per-combo pass/fail results. As a side-effect, it streams live per-combo progress events to Redis channel `agent3:progress`.

## 4. Exact Returned Dict Shapes (Real Empirical Output)

### `synthesize_policy` Return Value
```json
{
  "policy_id": "69c83866-8fa4-4956-a09a-824e03b612f7",
  "redact_fields": [
    "applicant_name",
    "zip_code"
  ],
  "group_adjustments": {},
  "rationale": "Redacting applicant_name, zip_code - flagged in 2 finding(s): applicant_name=Jamal, zip_code=90210. Expected to restore DIR above the 0.80 threshold.",
  "findings_addressed": [
    "00000000-0000-0000-0000-000000000101",
    "00000000-0000-0000-0000-000000000102"
  ]
}
```

### `verify_fix` Return Value
```json
{
  "scan_run_id": "00000000-0000-0000-0000-000000000001",
  "policy_id": "69c83866-8fa4-4956-a09a-824e03b612f7",
  "results": [
    {
      "combo_key": "zip_code=90210",
      "passed": true,
      "dir_value": 0.94,
      "p_value": 0.242424,
      "adjusted_p": 0.242424,
      "dir_crossed_threshold": true,
      "counts": {
        "unpriv_approved": 47,
        "unpriv_total": 50,
        "priv_approved": 50,
        "priv_total": 50
      }
    },
    {
      "combo_key": "applicant_name=Jamal",
      "passed": true,
      "dir_value": 0.94,
      "p_value": 0.242424,
      "adjusted_p": 0.242424,
      "dir_crossed_threshold": true,
      "counts": {
        "unpriv_approved": 47,
        "unpriv_total": 50,
        "priv_approved": 50,
        "priv_total": 50
      }
    }
  ]
}
```

## 5. Architectural Confirmation (Zero MCP Contamination)
`synthesize_policy` and `verify_fix` are **100% plain, framework-agnostic Python functions**. They contain **zero** `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`, or `mcp`/`FastMCP` imports. Person A can wrap them directly in `@mcp.tool()` decorators in `orchestrator/mcp_server.py` with zero adapter code.

## 6. Redis Side-Effect Channel
`verify_fix()` publishes per-combo progress events to Redis channel `agent3:progress` (consumed by Person D's live widget). Format:
```json
{
  "scan_run_id": "00000000-0000-0000-0000-000000000001",
  "combo_key": "zip_code=90210",
  "status": "passed",
  "dir_value": 0.94,
  "p_value": 0.242424,
  "adj_p_value": 0.242424,
  "ts": 1785013698.553584
}
```
If Redis is down, it logs a warning and continues without failing.

## 7. Current Known Limitations
1. **Fixture Data:** Currently using synthetic findings fixture (`fixtures/seed_fake_data.py`) pending Person B's Agent 1 Auditor branch merge.
2. **CI Gate Runner:** `compute_ci_gate()` is verified locally and executed via `ci_gate_runner.py` inside Postgres service container.
