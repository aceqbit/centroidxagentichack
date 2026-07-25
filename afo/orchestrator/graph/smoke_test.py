"""
Smoke test: end-to-end test of Agent 2 + Agent 3 skeletons.

Proves the full DB round-trip:
  1. Seed fake data (idempotent)
  2. Agent 2: synthesize_policy → writes policy to Postgres
  3. Agent 3: verify_fix → reads policy back, fake-verifies combos
  4. Confirm policy actually persisted by querying Postgres directly

Usage:
    cd orchestrator
    ..\.venv\Scripts\python.exe graph\smoke_test.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure orchestrator/ is on sys.path
_orchestrator_dir = Path(__file__).resolve().parent.parent
if str(_orchestrator_dir) not in sys.path:
    sys.path.insert(0, str(_orchestrator_dir))

# Load .env before any db imports
from dotenv import load_dotenv
load_dotenv(dotenv_path=_orchestrator_dir / ".env")


def _pretty(obj: dict | list) -> str:
    """Pretty-print a dict/list as indented JSON."""
    return json.dumps(obj, indent=2, default=str)


def main() -> None:
    print("=" * 60)
    print("  AFO Agent 2 + Agent 3 Smoke Test")
    print("=" * 60)

    # ── Step 0: Reset finding statuses to 'open' for re-runnability ────
    from db import repo
    from fixtures.fake_findings import FAKE_SCAN_RUN_ID, FAKE_FINDINGS

    # ── Step 1: Seed fake data ─────────────────────────────────────────
    print("\n[1/4] Seeding fake data...")
    from fixtures.seed_fake_data import seed
    seed()

    # Reset findings to 'open' so the test is idempotent on re-runs
    for f in FAKE_FINDINGS:
        repo.update_finding_status(f["id"], "open")
    print("  -> Findings reset to 'open' status for clean test run")

    # ── Step 2: Agent 2 — synthesize_policy ────────────────────────────
    print("\n[2/4] Running Agent 2: synthesize_policy...")
    from graph.agent2_synthesizer import synthesize_policy

    a2_result = synthesize_policy(FAKE_SCAN_RUN_ID)
    print(f"  -> Agent 2 result:\n{_pretty(a2_result)}")

    assert a2_result["policy_id"] is not None, "FAIL: policy_id is None"
    assert len(a2_result["redact_fields"]) > 0, "FAIL: no redact_fields"
    assert len(a2_result["findings_addressed"]) == 2, "FAIL: expected 2 findings"
    print("  [OK] Agent 2 assertions passed")

    # ── Step 3: Agent 3 — verify_fix ───────────────────────────────────
    print("\n[3/4] Running Agent 3: verify_fix...")
    from graph.agent3_verifier import verify_fix

    a3_result = verify_fix(FAKE_SCAN_RUN_ID)
    print(f"  -> Agent 3 result:\n{_pretty(a3_result)}")

    assert a3_result["policy_id"] is not None, "FAIL: policy_id is None"
    assert len(a3_result["results"]) == 2, "FAIL: expected 2 results"
    assert all(r["passed"] for r in a3_result["results"]), "FAIL: not all passed"
    assert all(
        r["new_dir_value"] == 0.94 for r in a3_result["results"]
    ), "FAIL: expected dir_value 0.94"
    print("  [OK] Agent 3 assertions passed")

    # ── Step 4: Verify DB round-trip ───────────────────────────────────
    print("\n[4/4] Verifying DB round-trip (querying Postgres directly)...")

    active_policy = repo.get_active_policy(FAKE_SCAN_RUN_ID)
    print(f"  -> get_active_policy:\n{_pretty(active_policy)}")
    assert active_policy is not None, "FAIL: no active policy in DB"
    assert active_policy["id"] == a2_result["policy_id"], "FAIL: policy_id mismatch"
    assert active_policy["is_active"] is True, "FAIL: policy not active"

    history = repo.get_policy_history(FAKE_SCAN_RUN_ID)
    print(f"  -> get_policy_history: {len(history)} policy/policies total")
    assert len(history) >= 1, "FAIL: no policies in history"

    # Verify findings were marked resolved
    findings_after = repo.get_findings(FAKE_SCAN_RUN_ID)
    resolved_count = sum(1 for f in findings_after if f["status"] == "resolved")
    print(f"  -> Findings status: {resolved_count}/{len(findings_after)} resolved")
    assert resolved_count == 2, "FAIL: expected 2 resolved findings"

    print("  [OK] DB round-trip verified")

    # ── Summary ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  [OK] ALL SMOKE TESTS PASSED")
    print("=" * 60)
    print(f"\n  Policy ID:      {a2_result['policy_id']}")
    print(f"  Redact fields:  {a2_result['redact_fields']}")
    print(f"  Findings fixed: {len(a2_result['findings_addressed'])}")
    print(f"  Verify results: {len(a3_result['results'])} combos, all passed")
    print(f"  DB policy rows: {len(history)}")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"\n[FAIL] SMOKE TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        sys.exit(1)
