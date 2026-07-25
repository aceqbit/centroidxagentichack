import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "target-service" / "config" / "proxy_fields.json"
LOCAL_SEED_PATH = Path(__file__).resolve().parent / "seed_proxy_fields.json"


def load_proxy_fields(path: Path | None = None) -> dict:
    """Load proxy field definitions from target-service config or local seed fallback.

    Resolution order:
    1. Explicitly supplied path (for testing)
    2. target-service/config/proxy_fields.json (the real source after Hour 3)
    3. orchestrator/track_a/seed_proxy_fields.json (local seed until Hour 3)

    Raises FileNotFoundError if neither file exists — that's intentional; it
    surfaces a missing dependency early rather than silently using wrong fields.
    """
    target_path = path or (DEFAULT_PATH if DEFAULT_PATH.exists() else LOCAL_SEED_PATH)
    if not target_path.exists():
        raise FileNotFoundError(
            f"No proxy_fields.json found at {target_path}. Before Hour 3, create "
            "orchestrator/track_a/seed_proxy_fields.json matching A's contract shape. "
            "After Hour 3, pull feat/target-agent so the real file exists."
        )
    with open(target_path) as f:
        return json.load(f)
