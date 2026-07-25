"""
Agent 2 — Patch Synthesizer (skeleton)

Turns open findings for a scan_run_id into a mitigation_policy and
writes it live to Postgres.

Person A imports this at Hour 14 as:
    from graph.agent2_synthesizer import synthesize_policy

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


def synthesize_policy(scan_run_id: str) -> dict:
    """
    Agent 2: turn open findings for scan_run_id into a mitigation_policy
    and write it live to Postgres.

    Returns:
        {
            "policy_id": str,
            "redact_fields": list[str],
            "group_adjustments": dict,
            "rationale": str,
            "findings_addressed": list[str]  # finding IDs
        }
    """
    # ── Step 1: Read open findings ─────────────────────────────────────
    all_findings = repo.get_findings(scan_run_id)
    open_findings = [f for f in all_findings if f["status"] == "open"]

    if not open_findings:
        return {
            "policy_id": None,
            "redact_fields": [],
            "group_adjustments": {},
            "rationale": "No open findings to address.",
            "findings_addressed": [],
        }

    # ── Step 2: Derive redact_fields from combo_keys ───────────────────
    # TODO(Hour 6-9): replace hardcoded derivation with real LLM call,
    #   temp=0, fixed seed, per build plan Section 5.3/6.6.2.
    #   The LLM should receive the list of open findings and generate:
    #     - redact_fields (which fields to redact)
    #     - neutral_value (what to replace with)
    #     - group_adjustments (per-group score adjustments)
    #     - rationale (human-readable explanation)
    #   For now, we derive these deterministically from combo_keys.
    redact_fields = sorted(set(
        f["combo_key"].split("=")[0]
        for f in open_findings
        if f.get("combo_key") and "=" in f["combo_key"]
    ))

    # Hardcoded skeleton values — replaced by LLM output at Hour 6-9
    neutral_value = "REDACTED"
    group_adjustments: dict = {}

    combo_keys = [f["combo_key"] for f in open_findings]
    rationale = (
        f"Redacting {redact_fields} — flagged in {len(open_findings)} "
        f"finding(s): {combo_keys}"
    )

    # ── Step 3: Write policy to Postgres ───────────────────────────────
    policy = repo.insert_mitigation_policy(
        scan_run_id=scan_run_id,
        redact_fields=redact_fields,
        neutral_value=neutral_value,
        group_adjustments=group_adjustments,
        rationale=rationale,
    )

    # ── Step 4: Mark findings as resolved ──────────────────────────────
    finding_ids = [f["id"] for f in open_findings]
    for fid in finding_ids:
        repo.update_finding_status(fid, "resolved")

    return {
        "policy_id": policy["id"],
        "redact_fields": redact_fields,
        "group_adjustments": group_adjustments,
        "rationale": rationale,
        "findings_addressed": finding_ids,
    }
