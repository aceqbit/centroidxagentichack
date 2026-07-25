"""
Agent 3 — Regression Verifier (real stats pipeline)

Person A imports this at Hour 14 as:
    from graph.agent3_verifier import verify_fix

DO NOT add MCP decorators here — internal logic only.
MCP wrapper: orchestrator/mcp_server.py (Person A, Hour 14).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure orchestrator/ is on sys.path
_orchestrator_dir = Path(__file__).resolve().parent.parent
if str(_orchestrator_dir) not in sys.path:
    sys.path.insert(0, str(_orchestrator_dir))

from dotenv import load_dotenv
load_dotenv(dotenv_path=_orchestrator_dir / ".env")

from db import repo
from stats.dir import compute_dir
from stats.fisher_bh import test_combo, correct_pvalues


# ---------------------------------------------------------------------------
# Fixture counts for synthetic post-patch outcomes
# (replaced at Hour 9-12 with real target-service call)
#
# FIXTURE RATIONALE: These produce DIR ~0.94, matching the demo narrative
# "DIR 0.58 -> 0.94 after patch" in the build plan.
# 47 out of 50 unprivileged approved vs 50 out of 50 privileged:
#   DIR = (47/50) / (50/50) = 0.94 exactly
# ---------------------------------------------------------------------------
_FIXTURE_UNPRIV_APPROVED = 47
_FIXTURE_UNPRIV_TOTAL = 50
_FIXTURE_PRIV_APPROVED = 50
_FIXTURE_PRIV_TOTAL = 50


def _simulate_post_patch_outcome(combo_key: str) -> dict:
    """
    FIXTURE: Simulate a post-patch outcome for a single combo.
    Returns the contingency table and derived stats.

    TODO(Hour 9-12 or whenever A merges): Replace this entire function with
    a real HTTP call to target-service's evaluate_loan_application tool on
    :3002, re-running only the failing combos with the active policy applied.
    Then feed the real counts into compute_dir() and test_combo() below.
    Check git branch feat/target-agent or main for A's tool availability.

    TODO(Hour 9-12): Publish SSE progress event per combo to Redis pub/sub
    channel 'agent3:progress' here — Gap #3 responsibility:
        redis_client.publish('agent3:progress', json.dumps({
            'combo_key': combo_key,
            'status': 'verifying',
            'progress': f'{i}/{total}'
        }))
    Don't build it now — just leave this marker so it's a clean plug-in.
    """
    # Fixture counts — clearly marked, not real re-evaluation
    a = _FIXTURE_UNPRIV_APPROVED    # unpriv approved
    b = _FIXTURE_UNPRIV_TOTAL - a   # unpriv denied
    c = _FIXTURE_PRIV_APPROVED      # priv approved
    d = _FIXTURE_PRIV_TOTAL - c     # priv denied

    # Real stats on fixture counts
    dir_value = compute_dir(a, _FIXTURE_UNPRIV_TOTAL, c, _FIXTURE_PRIV_TOTAL)
    odds_ratio, p_value = test_combo(a, b, c, d)

    return {
        "combo_key": combo_key,
        "counts": {"unpriv_approved": a, "unpriv_total": _FIXTURE_UNPRIV_TOTAL,
                   "priv_approved": c, "priv_total": _FIXTURE_PRIV_TOTAL},
        "dir_value": round(dir_value, 4),
        "p_value": p_value,
        "odds_ratio": odds_ratio,
    }


def verify_fix(scan_run_id: str) -> dict:
    """
    Agent 3: targeted re-verify of only the previously-failing combos
    after a policy was applied.

    Returns:
        {
            "scan_run_id": str,
            "policy_id": str | None,
            "results": [
                {
                    "combo_key": str,
                    "passed": bool,
                    "dir_value": float,       # real computed (from fixture counts)
                    "p_value": float,         # real Fisher p-value
                    "adjusted_p": float,      # BH-corrected p-value
                    "dir_crossed_threshold": bool,   # DIR >= 0.80
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

    if not findings:
        return {
            "scan_run_id": scan_run_id,
            "policy_id": policy_id,
            "results": [],
            "error": "No findings linked to this policy via mitigation_edges.",
        }

    # ── Step 3: Simulate post-patch outcome + compute real stats ───────
    raw_results = [_simulate_post_patch_outcome(f.get("combo_key", "unknown"))
                   for f in findings]

    # ── Step 4: BH-FDR correction across all combos in this verify run ─
    raw_p_values = [r["p_value"] for r in raw_results]
    _, adjusted_p_values = correct_pvalues(raw_p_values, alpha=0.05)

    # ── Step 5: Build final results list ───────────────────────────────
    results = []
    for r, adj_p in zip(raw_results, adjusted_p_values):
        dir_crossed = r["dir_value"] >= 0.80
        # "passed" = DIR crossed threshold AND NOT still significant after FDR
        # (i.e. the bias signal is gone statistically)
        still_significant = adj_p < 0.05
        passed = dir_crossed and not still_significant

        results.append({
            "combo_key": r["combo_key"],
            "passed": passed,
            "dir_value": r["dir_value"],
            "p_value": r["p_value"],
            "adjusted_p": round(adj_p, 6),
            "dir_crossed_threshold": dir_crossed,
            "counts": r["counts"],
        })

    return {
        "scan_run_id": scan_run_id,
        "policy_id": policy_id,
        "results": results,
    }
