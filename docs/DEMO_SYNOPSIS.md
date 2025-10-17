# Demo Synopsis (Narrative & Script)
**Story**: Business user uploads PaySim CSV; pipeline ingests, enriches with OFAC/PEP, scores risk, and publishes a high-risk list with an AI summary. Approver signs off; view is granted to consumers.

## Flow at a glance
1. Upload file (via Streamlit app or Volumes) → **DLT** ingests & validates.
2. Enrichment (OFAC SDN, OpenSanctions PEP) → **features** computed.
3. Rule-based **risk scoring** → **LOW/MED/HIGH** with MLflow metrics.
4. **Lakeview / SQL views** present high-risk entities; optional AI **narrative**.
5. **Approval & publish** (conditional step) → grant to `kyc_consumers`.

## Personas
- **Analyst (business)**: Uploads file, clicks “Run”, asks questions in natural language.
- **Approver (compliance)**: Reviews summary, approves publish.
- **Engineer (you)**: One-time setup (UC, Volumes, Pipeline, App).

## Success metrics
- < 5 minutes to refresh small dataset.
- Zero code for analyst (app + params).
- DQ gates enforced; lineage visible; low cost.

## On-stage script (10–12 min)
1. **Intro (1 min)**: “AI-powered KYC Reporting Factory, Databricks-native.”
2. **Upload (1–2 min)**: Use app to upload `paysim_small.csv`; preview a few rows.
3. **Run pipeline (2 min)**: Click “Run job”; show DLT UI → Expectations & lineage.
4. **Scoring & metrics (2 min)**: Open MLflow run; show band distribution, thresholds.
5. **Reporting (2–3 min)**: Open Lakeview / query view; filter on country/band; read AI summary.
6. **Approval (1–2 min)**: Show Slack/Teams (optional); re-run with `approve=true`; show consumer access.
