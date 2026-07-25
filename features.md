Ultimate core n Additional features:
# AFO — Final Combined Feature List (Bias-Only, 24-Hour Build)

## 🎯 Core Features (Must-Haves — build AND verify)

### 1. Adaptive Bias Auditor (Agent 1)
- **Counterfactual Perturbation Sweep** — toggles sensitive-attribute proxies (zip, name, age signal) while holding legit factors (skills, experience, credit score) constant.
- **Bandit-Scheduled Probing (UCB1)** — prioritizes probe budget toward high-drift combos instead of brute-force sweeping.
- **Statistical Scoring** — Disparate Impact Ratio → Fisher's exact test → Benjamini-Hochberg FDR correction across combos. Flags `DIR < 0.80` **and** statistically significant.
- ✅ **Seeded bias must be a *direct* proxy-field dependency** (decision logic literally branches on zip/name) — not learned/inferred, not probabilistic. This is a design decision made at hour 0, not discovered later.
- ✅ **Seed the perturbation sweep's sampling** with a fixed seed so DIR is identical across every run.
- ✅ **Timed 3x independently** — must have a real, repeated number, not a single lucky run.

### 2. Dynamic Guardrail Patch Synthesizer (Agent 2)
- **Policy Synthesis** — one structured LLM call converts Agent 1's findings into a mitigation policy (`redact_fields`, `group_adjustments`).
- **Live Hot-Swap** — writes to Postgres (Redis-cached); already-running Pipe + Interceptor picks it up on the next call, zero redeploy.
- ✅ **Pin the LLM call** (`temperature=0`, fixed seed) — the synthesized policy must be byte-identical every rehearsal and on stage.
- ✅ **Hardcode the proxy-field list** for the demo target instead of live-classifying it — you control the schema, no need to infer it live. Keep the LLM classifier as a "here's how it generalizes" talking point only.
- ✅ **Validated by hour 8-10**: seed bias → measure DIR (~0.55-0.60) → apply redact-only patch → re-measure DIR → confirm it crosses 0.80. Logged/screenshotted as proof, and as your Q&A answer for "why input-only patching is sufficient."

### 3. Automated Regression Verifier (Agent 3)
- **Targeted Re-Test** — re-runs *only* the specific failing combinations, not the full sweep.
- **Verification Gate** — confirms DIR crosses back above 0.80, and checks the aggregate decision rate across all groups wasn't degraded to "fix" the ratio.
- ✅ **Must read the same seeded data path as Agent 1's original sweep** — zero drift between first-pass and re-verify sampling.
- ✅ **Reliably under 45s, timed 3x.** If it's not, cut N (calls per combo) — don't let it run long live.
- ✅ **Visible progress indicator** (SSE-streamed logs) during re-verify so it doesn't read as the demo hanging.

### 4. Interactive Governance Ledger Widget (Agent 4)
- **Before/After Diff Viewer** — original policy vs. patched policy, **only the changed fields highlighted**, no raw JSON dump.
- **Live Compliance Scorecard** — DIR before → after, four-fifths threshold line drawn and labeled, one big pass/fail headline number. NitroStack `@Tool` + `@Widget`, callable from any MCP client.
- ✅ Judge should get "below the line = bad" in 2 seconds, no narration needed.

### 5. Full-Loop Reliability (cross-cutting, non-negotiable)
- ✅ **End-to-end loop (attack → patch → verify) reliably under 90s**, timed 3x back-to-back, not once when warm.
- ✅ **Fallback video recorded early** (hour 10-11) once the core loop works, **re-recorded at hour 14-15** with final polish so it isn't visibly older/uglier than the live build.
- ✅ **No "0%," "fully compliant," or "guaranteed fair" language** anywhere in UI, slides, or spoken script — audited line by line.

---

## 🗣️ Core Delivery Requirements (not code, but mandatory)

- **Rehearsed verbal Q&A**, unscripted, from every team member: why Fisher's not chi-square, why BH-FDR not Bonferroni, why input-only patching is sufficient for this bias class, why Track B/C were cut (stated as an engineering decision, not an apology).
- **Demo script rehearsed against a clock, 2x minimum**, on the actual live system — not a mental walkthrough.
- **Split roles**: one person narrates, one person drives — never the same person doing both.
- **Risk register as one slide**, ready if asked "what would you build next": timing, nondeterminism, wifi.
- **CI/CD gate, if kept, must fail a real PR live** — not a screenshot of a past run.

---

## 🚀 Additional / Stretch Features (only after everything above is verified, not just built)

### 1. Human-in-the-Loop Approval Widget
- "Approve / Reject Patch" button before Agent 2's hot-patch goes live — judge/compliance-officer sign-off, on stage.

### 2. Sensitivity Boundary Slider
- Interactive slider to tune the DIR threshold (0.80 → 0.90) live, watch pass/fail status update in real time.

### 3. Audit Log Export & Provenance
- MCP tool packaging findings + patch + verification result into a JSON compliance report.

### 4. Self-Hosting as an MCP Server
- Demo the governance widget live inside NitroStudio or Claude Desktop, not just your own frontend.

---

**Build order, if you need to cut:** Core 1-5 → Delivery Requirements → Stretch 1 → 2 → 3 → 4. Never trade a Core or Delivery item for a Stretch item — the checklist above *is* the difference between a working demo and a score-losing one; the stretch list is only ever upside.
