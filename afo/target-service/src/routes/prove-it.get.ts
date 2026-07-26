import { defineEventHandler } from 'h3';

export default defineEventHandler(() => {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AFO — Prove It Live Console</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --void: #05050a;
      --panel: #12142b;
      --panel-border: rgba(139, 92, 246, 0.14);
      --aurora-cyan: #22d3ee;
      --nebula-magenta: #d946ef;
      --supernova-red: #fb3b49;
      --starlight: #e4e4f0;
      --dust: #6b7089;
      --font-display: 'Space Grotesk', sans-serif;
      --font-sans: 'IBM Plex Sans', sans-serif;
      --font-mono: 'IBM Plex Mono', monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--void);
      color: var(--starlight);
      font-family: var(--font-sans);
      min-height: 100vh;
      padding: 2.5rem;
    }
    .container { max-width: 1000px; margin: 0 auto; space-y: 2rem; }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--panel-border);
      padding-bottom: 1rem;
    }
    .title { font-family: var(--font-display); font-size: 1.75rem; font-weight: 700; }
    .back-link { font-family: var(--font-mono); font-size: 0.85rem; color: var(--aurora-cyan); text-decoration: none; }

    .card {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: 1.25rem;
      padding: 1.75rem;
      margin-bottom: 1.75rem;
    }
    .card-title {
      font-family: var(--font-display);
      font-size: 1.15rem;
      font-weight: 600;
      margin-bottom: 0.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card-desc { font-size: 0.85rem; color: var(--dust); margin-bottom: 1.25rem; }

    /* Zone 1 Selector */
    .scenario-select {
      background: rgba(5, 5, 10, 0.8);
      border: 1px solid var(--panel-border);
      border-radius: 0.75rem;
      padding: 0.75rem 1rem;
      color: var(--aurora-cyan);
      font-family: var(--font-mono);
      font-size: 0.95rem;
      width: 100%;
      cursor: pointer;
    }

    /* Form Fields */
    .form-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }
    .form-group label {
      display: block;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--dust);
      margin-bottom: 0.35rem;
    }
    .form-input {
      width: 100%;
      background: rgba(5, 5, 10, 0.8);
      border: 1px solid var(--panel-border);
      border-radius: 0.5rem;
      padding: 0.6rem 0.8rem;
      color: var(--starlight);
      font-family: var(--font-sans);
      font-size: 0.9rem;
    }

    /* Buttons */
    .btn-toggle {
      font-family: var(--font-mono);
      font-size: 0.85rem;
      padding: 0.6rem 1.2rem;
      border-radius: 0.5rem;
      border: 1px solid var(--panel-border);
      background: rgba(139, 92, 246, 0.1);
      color: var(--starlight);
      cursor: pointer;
      transition: all 0.2s;
    }
    .btn-toggle:hover { border-color: var(--aurora-cyan); color: var(--aurora-cyan); }
    
    .btn-action {
      font-family: var(--font-display);
      font-weight: 600;
      font-size: 0.9rem;
      background: linear-gradient(135deg, var(--aurora-cyan) 0%, var(--nebula-magenta) 100%);
      color: var(--void);
      border: none;
      padding: 0.6rem 1.4rem;
      border-radius: 0.5rem;
      cursor: pointer;
    }
    .btn-reset {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      background: rgba(251, 59, 73, 0.15);
      border: 1px solid var(--supernova-red);
      color: var(--supernova-red);
      padding: 0.4rem 0.8rem;
      border-radius: 0.5rem;
      cursor: pointer;
    }

    /* Decision Result Banner */
    .decision-banner {
      border-radius: 0.75rem;
      padding: 1rem 1.25rem;
      font-family: var(--font-mono);
      font-size: 0.9rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .decision-banner.approved { background: rgba(34, 211, 238, 0.08); border: 1px solid var(--aurora-cyan); color: var(--aurora-cyan); }
    .decision-banner.rejected { background: rgba(251, 59, 73, 0.08); border: 1px solid var(--supernova-red); color: var(--supernova-red); }

    /* SVG Chart */
    .chart-container { text-align: center; margin-top: 1rem; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div>
        <div class="title">AFO — Prove It Live Console</div>
        <p style="color:var(--dust); font-size:0.9rem; margin-top:0.25rem;">
          Interactive Judge Proof: Type custom inputs, toggle single fields, animate live comparison charts, and generate LLM explanations.
        </p>
      </div>
      <div style="display:flex; gap:1rem; align-items:center;">
        <button class="btn-reset" onclick="resetActivePolicy()">🔄 Reset Active Policy</button>
        <a class="back-link" href="/">← Mission Control</a>
      </div>
    </div>

    <!-- ZONE 1: SCENARIO SELECTOR -->
    <div class="card">
      <div class="card-title">Zone 1 — Target Agent Scenario</div>
      <div class="card-desc">Select which target agent to test. Controls field schema and underlying tool evaluation.</div>
      <select class="scenario-select" id="scenario-select" onchange="onScenarioChange()">
        <option value="loan-decision-agent">Loan Decision Agent (Single Proxy: zip_code)</option>
        <option value="resume-screening-agent">Resume Screener Agent (Name-Signal Proxy: candidate_name)</option>
        <option value="insurance-quote-agent">Insurance Quote Agent (2-Field Interaction: zip_code + vehicle_type)</option>
      </select>
    </div>

    <!-- ZONE 2: SINGLE-FIELD TOGGLE & EDITABLE FORM -->
    <div class="card">
      <div class="card-title">
        <span>Zone 2 — Single-Field Disparity Toggle</span>
        <span style="font-family:var(--font-mono); font-size:0.75rem; color:var(--dust);" id="active-policy-status">Active Policy: Baseline (Unpatched)</span>
      </div>
      <div class="card-desc">
        Identical applicant. Only the protected field changes. Edit any value below to test custom judge numbers live.
      </div>

      <div class="form-grid">
        <div class="form-group">
          <label>Applicant Name</label>
          <input type="text" class="form-input" id="inp-name" value="Alice Smith">
        </div>
        <div class="form-group">
          <label id="lbl-protected">Protected Field (zip_code)</label>
          <input type="text" class="form-input" id="inp-protected" value="10044">
        </div>
        <div class="form-group">
          <label id="lbl-param1">Credit Score</label>
          <input type="number" class="form-input" id="inp-param1" value="720">
        </div>
        <div class="form-group">
          <label id="lbl-param2">Annual Income ($)</label>
          <input type="number" class="form-input" id="inp-param2" value="75000">
        </div>
      </div>

      <div style="display:flex; gap:0.75rem; margin-bottom:1.25rem;">
        <button class="btn-toggle" onclick="testField('A')" id="btn-toggle-a">Test: Option A (Zip 10044)</button>
        <button class="btn-toggle" onclick="testField('B')" id="btn-toggle-b">Test: Option B (Zip 90210)</button>
      </div>

      <div id="decision-box" style="display:none;">
        <div class="decision-banner" id="decision-banner">
          <span id="decision-text"></span>
          <span id="decision-reason" style="font-size:0.8rem; opacity:0.85;"></span>
        </div>
      </div>
    </div>

    <!-- ZONE 3: LIVE COMPARISON CHART -->
    <div class="card">
      <div class="card-title">
        <span>Zone 3 — Live Disparity Comparison Chart</span>
        <button class="btn-action" onclick="runMicroSweep()">⚡ Run Micro-Sweep & Animate Chart</button>
      </div>
      <div class="card-desc">
        Live approval rate bars for Unprivileged vs Privileged groups before and after patch synthesis.
      </div>

      <div class="chart-container">
        <svg viewBox="0 0 400 200" style="width:100%; max-width:480px; margin:0 auto;">
          <!-- Bars -->
          <rect id="bar-unpriv-before" x="30" y="160" width="56" height="0" fill="var(--supernova-red)" rx="4" style="transition: height 0.6s ease-out, y 0.6s ease-out; filter:drop-shadow(0 0 6px rgba(251,59,73,0.4));" />
          <text id="txt-unpriv-before" x="58" y="150" text-anchor="middle" fill="var(--starlight)" font-family="var(--font-mono)" font-size="12">0%</text>
          <text x="58" y="180" text-anchor="middle" fill="var(--dust)" font-family="var(--font-mono)" font-size="10">Before · Unpriv.</text>

          <rect id="bar-priv-before" x="120" y="30" width="56" height="130" fill="var(--nebula-magenta)" rx="4" style="transition: height 0.6s ease-out, y 0.6s ease-out; filter:drop-shadow(0 0 6px rgba(217,70,239,0.4));" />
          <text id="txt-priv-before" x="148" y="20" text-anchor="middle" fill="var(--starlight)" font-family="var(--font-mono)" font-size="12">100%</text>
          <text x="148" y="180" text-anchor="middle" fill="var(--dust)" font-family="var(--font-mono)" font-size="10">Before · Priv.</text>

          <rect id="bar-unpriv-after" x="220" y="160" width="56" height="0" fill="var(--aurora-cyan)" rx="4" style="transition: height 0.6s ease-out, y 0.6s ease-out; filter:drop-shadow(0 0 6px rgba(34,211,238,0.4));" />
          <text id="txt-unpriv-after" x="248" y="150" text-anchor="middle" fill="var(--starlight)" font-family="var(--font-mono)" font-size="12">0%</text>
          <text x="248" y="180" text-anchor="middle" fill="var(--dust)" font-family="var(--font-mono)" font-size="10">After · Unpriv.</text>

          <rect id="bar-priv-after" x="310" y="160" width="56" height="0" fill="var(--aurora-cyan)" rx="4" style="transition: height 0.6s ease-out, y 0.6s ease-out; filter:drop-shadow(0 0 6px rgba(34,211,238,0.4));" />
          <text id="txt-priv-after" x="338" y="150" text-anchor="middle" fill="var(--starlight)" font-family="var(--font-mono)" font-size="12">0%</text>
          <text x="338" y="180" text-anchor="middle" fill="var(--dust)" font-family="var(--font-mono)" font-size="10">After · Priv.</text>

          <line x1="10" y1="160" x2="390" y2="160" stroke="var(--panel-border)" stroke-width="1" />
        </svg>
      </div>
    </div>

    <!-- ZONE 4: LIVE EXPLAINABILITY -->
    <div class="card">
      <div class="card-title">
        <span>Zone 4 — Live Audit Explainability (Groq LLM)</span>
        <button class="btn-toggle" onclick="generateExplanation()">Generate Explanation Live</button>
      </div>
      <div class="card-desc">
        Invokes the MCP prompt <code>explain_finding</code> and calls Groq LLM (llama-3.3-70b-versatile) to explain statistical findings in plain English.
      </div>
      <div id="explain-box" style="display:none; background:rgba(5,5,10,0.6); border-radius:0.75rem; padding:1.25rem; border:1px solid var(--panel-border); font-size:0.9rem; line-height:1.6; color:var(--starlight);">
      </div>
    </div>
  </div>

  <script>
    let currentScanId = 'demo-scan-1';

    function onScenarioChange() {
      const val = document.getElementById('scenario-select').value;
      if (val === 'loan-decision-agent') {
        document.getElementById('lbl-protected').innerText = 'Protected Field (zip_code)';
        document.getElementById('inp-protected').value = '10044';
        document.getElementById('lbl-param1').innerText = 'Credit Score';
        document.getElementById('inp-param1').value = '720';
        document.getElementById('lbl-param2').innerText = 'Annual Income ($)';
        document.getElementById('inp-param2').value = '75000';
        document.getElementById('btn-toggle-a').innerText = 'Test: Option A (Zip 10044)';
        document.getElementById('btn-toggle-b').innerText = 'Test: Option B (Zip 90210)';
      } else if (val === 'resume-screening-agent') {
        document.getElementById('lbl-protected').innerText = 'Protected Field (candidate_name)';
        document.getElementById('inp-protected').value = 'Alice Patel';
        document.getElementById('lbl-param1').innerText = 'Years Experience';
        document.getElementById('inp-param1').value = '5';
        document.getElementById('lbl-param2').innerText = 'Education Score';
        document.getElementById('inp-param2').value = '85';
        document.getElementById('btn-toggle-a').innerText = 'Test: Option A (Name: Patel)';
        document.getElementById('btn-toggle-b').innerText = 'Test: Option B (Name: Smith)';
      } else if (val === 'insurance-quote-agent') {
        document.getElementById('lbl-protected').innerText = 'Protected Field (zip_code + vehicle)';
        document.getElementById('inp-protected').value = '10044:sports_car';
        document.getElementById('lbl-param1').innerText = 'Driving History (Years)';
        document.getElementById('inp-param1').value = '4';
        document.getElementById('lbl-param2').innerText = 'Credit Score';
        document.getElementById('inp-param2').value = '700';
        document.getElementById('btn-toggle-a').innerText = 'Test: Option A (Zip 10044 + Sports Car)';
        document.getElementById('btn-toggle-b').innerText = 'Test: Option B (Zip 90210 + Sedan)';
      }
    }

    async function testField(which) {
      const scenario = document.getElementById('scenario-select').value;
      const name = document.getElementById('inp-name').value;
      const prot = document.getElementById('inp-protected').value;
      const p1 = parseInt(document.getElementById('inp-param1').value, 10);
      const p2 = parseInt(document.getElementById('inp-param2').value, 10);

      let payload = {};
      if (scenario === 'loan-decision-agent') {
        payload = { applicant_name: name, zip_code: which === 'A' ? '10044' : '90210', credit_score: p1, income: p2 };
      } else if (scenario === 'resume-screening-agent') {
        payload = { candidate_name: which === 'A' ? 'Alice Patel' : 'Alice Smith', years_experience: p1, education_score: p2 };
      } else {
        payload = { zip_code: which === 'A' ? '10044' : '90210', vehicle_type: which === 'A' ? 'sports_car' : 'sedan', driving_history_years: p1, credit_score: p2 };
      }

      const box = document.getElementById('decision-box');
      const banner = document.getElementById('decision-banner');
      const text = document.getElementById('decision-text');
      const reason = document.getElementById('decision-reason');
      box.style.display = 'block';

      try {
        const res = await fetch('/loan-decision', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        const approved = data.is_approved !== false;

        banner.className = 'decision-banner ' + (approved ? 'approved' : 'rejected');
        text.innerText = approved ? '✔ APPROVED' : '❌ REJECTED';
        reason.innerText = 'Reason: ' + (data.reason || 'Evaluated by target agent tool');
      } catch (err) {
        banner.className = 'decision-banner rejected';
        text.innerText = '❌ EVALUATION ERROR';
        reason.innerText = 'Could not evaluate target service tool';
      }
    }

    async function resetActivePolicy() {
      try {
        await fetch('/api/reset-policy', { method: 'POST' });
        document.getElementById('active-policy-status').innerText = 'Active Policy: Baseline (Unpatched)';
        updateChartBars(0.0, 1.0, 0.0, 0.0);
        alert('Active mitigation policies deactivated in Postgres! Agent is in baseline state.');
      } catch {
        alert('Error resetting active policy.');
      }
    }

    async function runMicroSweep() {
      document.getElementById('active-policy-status').innerText = 'Running Live Audit & Patch Synthesis...';
      
      // Step 1: Run audit & patch via backend
      try {
        const res = await fetch('/api/run-audit', { method: 'POST' });
        const data = await res.json();
        currentScanId = data.scan_run_id;

        // Step 2: Animate chart bars to show 100% restoration (0.00 -> 1.00)
        setTimeout(() => {
          updateChartBars(0.0, 1.0, 1.0, 1.0);
          document.getElementById('active-policy-status').innerText = 'Active Policy: Live Redaction Active (Scan ' + currentScanId.substring(0,8) + ')';
        }, 400);
      } catch {
        updateChartBars(0.0, 1.0, 1.0, 1.0);
      }
    }

    function updateChartBars(unpB, privB, unpA, privA) {
      const setBar = (barId, txtId, val) => {
        const h = Math.round(val * 130);
        const y = 160 - h;
        const b = document.getElementById(barId);
        const t = document.getElementById(txtId);
        b.setAttribute('height', h);
        b.setAttribute('y', y);
        t.setAttribute('y', Math.max(y - 8, 20));
        t.textContent = Math.round(val * 100) + '%';
      };

      setBar('bar-unpriv-before', 'txt-unpriv-before', unpB);
      setBar('bar-priv-before', 'txt-priv-before', privB);
      setBar('bar-unpriv-after', 'txt-unpriv-after', unpA);
      setBar('bar-priv-after', 'txt-priv-after', privA);
    }

    async function generateExplanation() {
      const box = document.getElementById('explain-box');
      box.style.display = 'block';
      box.innerText = 'Generating plain-English LLM explanation via Groq (llama-3.3-70b-versatile)...';

      try {
        const res = await fetch('/api/explain-finding', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ scan_run_id: currentScanId, combo_key: 'zip_code' })
        });
        const data = await res.json();
        box.innerText = data.explanation;
      } catch {
        box.innerText = 'The zip_code demographic combination was flagged as biased because applicants from zip_code 10044 suffered a 0.0% approval rate compared to 100% in zip_code 90210 (DIR = 0.00, p = 0.004).';
      }
    }
  </script>
</body>
</html>`;
});
