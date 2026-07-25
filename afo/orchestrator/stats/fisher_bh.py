"""
stats/fisher_bh.py — Fisher's exact test + Benjamini-Hochberg FDR correction.

Why Fisher's and NOT chi-square?
- Fisher's exact test is exact (no large-sample approximation needed).
- For small cell counts (which occur often in sub-group combo sweeps), 
  chi-square's chi^2 approximation breaks down. Fisher's is always valid.

Why BH-FDR and NOT Bonferroni?
- Bonferroni controls Family-Wise Error Rate (FWER) — the probability of
  ANY false positive. It is very conservative, especially with many combos.
- For a large combination lattice (zip x name x age x ...), Bonferroni is
  far too strict — it would miss real bias signals.
- Benjamini-Hochberg controls False Discovery Rate (expected proportion of
  false discoveries among rejections) — the right tradeoff for exploratory
  bias scanning where a few false positives are acceptable but false 
  negatives are not.

MERGE-TIME WARNING: B's branch (feat/agent1-auditor) may contain duplicate
implementations. Whoever merges second must delete this copy and re-point
imports to the single source of truth. Run smoke_test.py to verify.
"""

from __future__ import annotations

from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests


def test_combo(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """
    Fisher's exact test on a 2x2 contingency table.

    Table layout:
        [[unpriv_approved (a),  unpriv_denied (b)],
         [priv_approved   (c),  priv_denied   (d)]]

    Args:
        a: Unprivileged group, approved count.
        b: Unprivileged group, denied count.
        c: Privileged group, approved count.
        d: Privileged group, denied count.

    Returns:
        (odds_ratio, p_value) — p_value is two-tailed.
    """
    table = [[a, b], [c, d]]
    odds_ratio, p_value = fisher_exact(table, alternative="two-sided")
    return float(odds_ratio), float(p_value)


def correct_pvalues(
    p_values: list[float],
    alpha: float = 0.05,
) -> tuple[list[bool], list[float]]:
    """
    Benjamini-Hochberg FDR correction across multiple combo p-values.

    Uses BH (not Bonferroni — too conservative for large combination lattices,
    per AFO build plan). Controls the expected proportion of false discoveries
    among all rejected null hypotheses.

    Args:
        p_values: List of raw p-values, one per combo.
        alpha:    Desired FDR level (default 0.05 = 5% false discoveries allowed).

    Returns:
        (reject_array, adjusted_p_values) where:
          - reject_array[i] is True if combo i is statistically significant 
            after FDR correction.
          - adjusted_p_values[i] is the BH-adjusted p-value for combo i.
    """
    if not p_values:
        return [], []

    reject, p_adj, _, _ = multipletests(p_values, alpha=alpha, method="fdr_bh")
    return list(reject), list(p_adj)


# ---------------------------------------------------------------------------
# Standalone verification test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("--- Fisher's Exact Test Verification ---")

    # Known example: strong bias signal
    # Unprivileged: 10 approved / 50 total (20% approval)
    # Privileged:   30 approved / 50 total (60% approval)
    # Expected: very small p-value (highly significant)
    a, b = 10, 40   # unpriv: approved=10, denied=40
    c, d = 30, 20   # priv:   approved=30, denied=20

    odds_ratio, p_val = test_combo(a, b, c, d)
    print(f"  Contingency table: [[{a},{b}],[{c},{d}]]")
    print(f"  Odds ratio:        {odds_ratio:.4f}")
    print(f"  p-value:           {p_val:.6f}")
    print(f"  Significant (<0.05): {p_val < 0.05}")

    print()
    print("--- BH-FDR Correction Verification ---")
    # Three combos: one clearly significant, two noise
    raw_pvals = [p_val, 0.42, 0.87]
    reject, adj_p = correct_pvalues(raw_pvals)
    for i, (r, raw, adj) in enumerate(zip(reject, raw_pvals, adj_p)):
        status = "REJECT (significant)" if r else "keep (not significant)"
        print(f"  Combo {i}: raw_p={raw:.4f}  adj_p={adj:.4f}  -> {status}")

    print()
    print("--- DIR Sanity Check ---")
    from dir import compute_dir

    # Pre-patch: 29/50 vs 50/50 -> DIR ~0.58
    dir_pre = compute_dir(29, 50, 50, 50)
    print(f"  Pre-patch DIR (29/50 vs 50/50):  {dir_pre:.4f} (expect ~0.58)")

    # Post-patch: 47/50 vs 50/50 -> DIR ~0.94
    dir_post = compute_dir(47, 50, 50, 50)
    print(f"  Post-patch DIR (47/50 vs 50/50): {dir_post:.4f} (expect ~0.94)")
    print(f"  DIR crossed 0.80 threshold: {dir_post >= 0.80}")
