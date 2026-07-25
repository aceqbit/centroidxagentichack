"""
Fake findings data for development/testing.

Used as seed data so Agent 2 and Agent 3 skeletons can run without
waiting for Agent 1 (Person B's branch) to merge at Hour 6.
"""

FAKE_SCAN_RUN_ID = "00000000-0000-0000-0000-000000000001"

FAKE_FINDINGS = [
    {
        "id": "00000000-0000-0000-0000-000000000101",
        "scan_run_id": FAKE_SCAN_RUN_ID,
        "track": "bias",
        "combo_key": "zip_code=90210",
        "dir_value": 0.58,
        "p_value": 0.001,
        "fdr_adjusted_p": 0.004,
        "status": "open",
    },
    {
        "id": "00000000-0000-0000-0000-000000000102",
        "scan_run_id": FAKE_SCAN_RUN_ID,
        "track": "bias",
        "combo_key": "applicant_name=Jamal",
        "dir_value": 0.62,
        "p_value": 0.003,
        "fdr_adjusted_p": 0.009,
        "status": "open",
    },
]
