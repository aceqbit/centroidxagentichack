"""
Agent 3 — Regression Verifier (skeleton)

Targeted re-verify of only the previously-failing combos after a
mitigation policy was applied.

Person A imports this at Hour 14 as:
    from graph.agent3_verifier import verify_fix

DO NOT add MCP decorators here — this is internal logic only.
The MCP wrapper lives in orchestrator/mcp_server.py (Person A, Hour 14).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure orchestrator/ is on sys.path
_orchestrator_dir = Path(__file__).resolve().parent.parent
if str(_orchestrator_dir) not in sys.path:
    sys.path.insert(0, str(_orchestrator_dir))

from db import repo


def verify_fix(scan_run_id: str) -> dict:
    """
    Agent 3: targeted re-verify of only the previously-failing combos
    after a policy was applied.

    Returns:
        {
            "scan_run_id": str,
            "policy_id": str,
            "results": [
                {
                    "combo_key": str,
                    "passed": bool,
                    "new_dir_value": float,
                }
            ]
        }
    """
    # ── Step 1: Get the active policy ──────────────────────────────────
    policy = repo.get_active_policy(scan_run_id)

    if policy is None:
        return {
            "scan_run_id": scan_run_id,
            "policy_id": None,
            "results": [],
            "error": "No active policy found for this scan_run_id.",
        }

    policy_id = policy["id"]

    # ── Step 2: Get findings addressed by this policy ──────────────────
    findings = repo.get_findings_for_policy(policy_id)

    # ── Step 3: Re-verify each combo ───────────────────────────────────
    # TODO(Hour 9): replace hardcoded pass/fail with a real call to
    #   target-service's evaluate_loan_application tool (A's branch,
    #   merges ~Hour 3-6) re-running only the failing combos, then real
    #   DIR/Fisher recomputation (B's stats/dir.py, stats/fisher_bh.py,
    #   merges ~Hour 6-9).
    #
    #   Pseudocode for real implementation:
    #     for combo in findings:
    #         result = call_target_service(combo["combo_key"], policy)
    #         new_dir = compute_dir(result)
    #         new_p = fisher_exact_test(result)
    #         passed = new_p > 0.05 and new_dir > 0.80
    #         results.append({...})

    # TODO(Hour 9-12): publish SSE progress event per combo to Redis
    #   pub/sub channel 'agent3:progress' here — this is Gap #3
    #   responsibility. Each event should include:
    #     {"combo_key": ..., "status": "verifying"|"passed"|"failed",
    #      "progress": n/total}
    #   Don't build it now, just leave this marker so you don't forget
    #   where it plugs in.

    # SKELETON: fake a "pass" for each combo with hardcoded DIR 0.94
    # (matches build plan demo narrative: DIR 0.58 → 0.94)
    results = []
    for f in findings:
        results.append({
            "combo_key": f.get("combo_key", "unknown"),
            "passed": True,
            "new_dir_value": 0.94,
        })

    return {
        "scan_run_id": scan_run_id,
        "policy_id": policy_id,
        "results": results,
    }
