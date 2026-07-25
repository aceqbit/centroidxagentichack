"""
Agent 2 — Patch Synthesizer (real LLM call)

Person A imports this at Hour 14 as:
    from graph.agent2_synthesizer import synthesize_policy

DO NOT add MCP decorators here — internal logic only.
MCP wrapper: orchestrator/mcp_server.py (Person A, Hour 14).
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path

# Ensure orchestrator/ is on sys.path
_orchestrator_dir = Path(__file__).resolve().parent.parent
if str(_orchestrator_dir) not in sys.path:
    sys.path.insert(0, str(_orchestrator_dir))

from dotenv import load_dotenv
load_dotenv(dotenv_path=_orchestrator_dir / ".env")

from db import repo


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = textwrap.dedent("""\
    You are a bias-mitigation policy synthesizer for an automated fairness auditing system.

    You will be given a list of bias findings — each contains a combo_key (a proxy
    field and value that showed disparate impact), statistical measures, and context.

    Your job: derive a mitigation policy in JSON. Be precise and honest.

    LANGUAGE RULES (mandatory):
    - Never say "0% bias", "fully compliant", "bias-free", or "guaranteed fair".
    - Use language like: "DIR restored above the four-fifths threshold (0.80)",
      "no longer statistically distinguishable from sampling noise at alpha=0.05",
      "redacting these fields is expected to reduce proxy-based disparate impact".
    - Rationale must be factual and calibrated — this output may appear in a
      compliance report reviewed by humans.

    OUTPUT FORMAT: Return ONLY a valid JSON object. No prose, no markdown fences.
    Schema:
    {
      "redact_fields": ["field1", "field2", ...],
      "neutral_value": "REDACTED",
      "group_adjustments": {},
      "rationale": "..."
    }

    - redact_fields: list of proxy field names implicated (extract from combo_key,
      e.g. "zip_code=90210" -> "zip_code"). Deduplicate. Sort alphabetically.
    - neutral_value: always "REDACTED" for now.
    - group_adjustments: always {} for now (real logic at Hour 9-12).
    - rationale: Must follow this exact template string:
      "Redacting [fields] - flagged in [N] finding(s): [combo_keys]. Expected to restore DIR above the 0.80 threshold."
      Fill in [fields], [N], and [combo_keys] accurately. Do not alter the surrounding template text.
""")


def _build_user_message(findings: list[dict]) -> str:
    lines = [f"Open findings to address ({len(findings)} total):"]
    for f in findings:
        lines.append(
            f"  - combo_key={f.get('combo_key')!r}  "
            f"dir_value={f.get('dir_value')}  "
            f"p_value={f.get('p_value')}  "
            f"fdr_adjusted_p={f.get('fdr_adjusted_p')}"
        )
    lines.append("\nReturn ONLY the JSON object. No other text.")
    return "\n".join(lines)


def _call_llm(findings: list[dict], *, retry: bool = False) -> dict:
    """
    Call LLM (Groq or Anthropic) at temperature=0 to synthesize policy.
    Supports GROQ_API_KEY (model: llama-3.3-70b-versatile) and ANTHROPIC_API_KEY.
    Raises RuntimeError if neither key is set.
    """
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()

    if not groq_key and not anthropic_key:
        raise RuntimeError(
            "Neither GROQ_API_KEY nor ANTHROPIC_API_KEY is set in orchestrator/.env.\n"
            "Add GROQ_API_KEY=gsk_... or ANTHROPIC_API_KEY=sk-ant-... to orchestrator/.env."
        )

    user_msg = _build_user_message(findings)
    if retry:
        user_msg += (
            "\n\nCRITICAL: Your previous response was not valid JSON. "
            "Return ONLY a valid JSON object. Absolutely no markdown, "
            "no explanation, no text before or after the JSON."
        )

    print(f"[agent2] Sending {len(findings)} finding(s) to LLM...")
    print("[agent2] PATH: LIVE_LLM_CALL")

    if groq_key:
        import httpx

        model_name = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
        print(f"[agent2] Using Groq API ({model_name})...")

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Groq API error ({resp.status_code}): {resp.text}")

        raw = resp.json()["choices"][0]["message"]["content"].strip()
    else:
        import anthropic

        model_name = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        print(f"[agent2] Using Anthropic API ({model_name})...")
        client = anthropic.Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model=model_name,
            max_tokens=512,
            temperature=0,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()

    print(f"[agent2] Raw LLM response:\n{raw}\n")

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        if retry:
            raise ValueError(
                f"LLM returned invalid JSON after retry. Parse error: {e}\n"
                f"Raw response was:\n{raw}"
            ) from e
        print(f"[agent2] JSON parse failed ({e}), retrying once...")
        return _call_llm(findings, retry=True)


# ---------------------------------------------------------------------------
# Public API — signature locked for Person A's Hour 14 mcp_server.py import
# ---------------------------------------------------------------------------

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
            "findings_addressed": list[str]
        }

    Raises:
        RuntimeError: if ANTHROPIC_API_KEY is not set in orchestrator/.env.
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

    # ── Step 2: LLM call to derive policy fields ───────────────────────
    # TODO(Hour 6-9): LLM call is wired. Determinism pass at Hour 12.5:
    #   run 3x and assert identical output. Key params:
    #   - model="claude-sonnet-4-5", temperature=0, fixed system prompt
    #   - No randomness in prompt construction (findings sorted by id)
    #   The LLM reasoning replaces the naive combo_key string-split from skeleton.
    llm_out = _call_llm(sorted(open_findings, key=lambda f: f["id"]))

    redact_fields = sorted(set(llm_out.get("redact_fields", [])))
    neutral_value = llm_out.get("neutral_value", "REDACTED")
    group_adjustments = llm_out.get("group_adjustments", {})
    rationale = llm_out.get("rationale", "")

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
