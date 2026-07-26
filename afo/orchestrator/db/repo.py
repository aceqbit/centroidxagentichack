def get_findings(scan_run_id: str) -> dict:
    return {"status": "mocked", "scan_run_id": scan_run_id, "findings": []}

def get_active_policy() -> dict:
    return {"status": "mocked", "policy": "active"}

def get_policy_history() -> dict:
    return {"status": "mocked", "history": []}

def get_ci_gate_result(scan_run_id: str) -> dict:
    return {"status": "mocked", "scan_run_id": scan_run_id, "gate_passed": True}