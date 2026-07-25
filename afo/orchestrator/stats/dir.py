"""
stats/dir.py — Disparate Impact Ratio (DIR) computation.

MERGE-TIME WARNING: B's branch (feat/agent1-auditor) may have a duplicate
implementation of compute_dir(). Whoever merges second must delete the
duplicate and re-point imports. Do not let two versions coexist in main.

Legal/compliance note:
DIR < 0.80 is the EEOC four-fifths rule threshold (29 CFR §1607.4(D)).
This is an industry heuristic for flagging potential disparate impact.
It is NOT a legal compliance certification — bias detection is a signal
for human review, not a legal conclusion.
"""

from __future__ import annotations


def compute_dir(
    unpriv_approved: int,
    unpriv_total: int,
    priv_approved: int,
    priv_total: int,
) -> float:
    """
    Compute Disparate Impact Ratio (DIR):
        DIR = (unpriv_approved / unpriv_total) / (priv_approved / priv_total)

    The EEOC four-fifths rule (29 CFR §1607.4(D)) treats DIR < 0.80 as
    a heuristic indicator of potential disparate impact — a flag for review,
    not a legal compliance determination.

    Args:
        unpriv_approved: Count of approved decisions for unprivileged group.
        unpriv_total:    Total decisions for unprivileged group.
        priv_approved:   Count of approved decisions for privileged group.
        priv_total:      Total decisions for privileged group.

    Returns:
        DIR as a float (e.g. 0.58 means unprivileged group approved at 58%
        the rate of privileged group).

    Raises:
        ValueError: If any total is zero (division by zero) or counts
                    exceed totals (invalid contingency table).
    """
    if unpriv_total <= 0:
        raise ValueError(
            f"unpriv_total must be > 0, got {unpriv_total}. "
            "Cannot compute DIR with an empty unprivileged group."
        )
    if priv_total <= 0:
        raise ValueError(
            f"priv_total must be > 0, got {priv_total}. "
            "Cannot compute DIR with an empty privileged group."
        )
    if unpriv_approved < 0 or unpriv_approved > unpriv_total:
        raise ValueError(
            f"unpriv_approved ({unpriv_approved}) must be in [0, {unpriv_total}]."
        )
    if priv_approved < 0 or priv_approved > priv_total:
        raise ValueError(
            f"priv_approved ({priv_approved}) must be in [0, {priv_total}]."
        )
    if priv_approved == 0:
        raise ValueError(
            f"priv_approved is 0 — cannot compute DIR (division by zero in rate). "
            "This means the privileged group had 0% approval, which makes DIR undefined."
        )

    p_unpriv = unpriv_approved / unpriv_total
    p_priv = priv_approved / priv_total

    return p_unpriv / p_priv
