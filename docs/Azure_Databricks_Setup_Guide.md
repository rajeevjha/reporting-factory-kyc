# Azure Databricks Setup Guide – KYC Reporting Factory Demo

This guide walks you through deploying the **KYC Reporting Factory** demo on **Azure Databricks** with Unity Catalog, Delta Live Tables, MLflow, Lakeview, and a Streamlit App.

---

## 🧱 1. Prerequisites
- Azure subscription with access to a Databricks workspace and ADLS Gen2.
- Unity Catalog enabled and Serverless SQL Warehouse (or Pro tier).
- Download these ZIPs:
  - `finance_demo_large_csvs.zip` – large demo data.
  - `kyc_reporting_factory_notebook_edition.zip` – notebooks + app.

---

## 🏗️ 2. Unity Catalog and Volumes

Run in a SQL notebook or Databricks SQL editor:
```sql
CREATE CATALOG IF NOT EXISTS kyc_demo;
CREATE SCHEMA IF NOT EXISTS kyc_demo.bronze;
CREATE SCHEMA IF NOT EXISTS kyc_demo.silver;
CREATE SCHEMA IF NOT EXISTS kyc_demo.gold;

CREATE VOLUME IF NOT EXISTS kyc_demo.bronze.raw;
CREATE VOLUME IF NOT EXISTS kyc_demo.bronze.ref;
```
---

## 📂 3. Upload Demo Data

Upload files from `finance_demo_large_csvs.zip` to Volumes:

| File | Target Volume Path |
|------|---------------------|
| transactions.csv | /Volumes/kyc_demo/bronze/raw/paysim/ |
| customers.csv | /Volumes/kyc_demo/bronze/raw/customers/ |
| sdn.csv | /Volumes/kyc_demo/bronze/ref/ofac/ |
| pep.csv | /Volumes/kyc_demo/bronze/ref/pep/ |

---

## ⚙️ 4. Import and Configure Notebooks

Import `kyc_reporting_factory_notebook_edition.zip` → your workspace.  
Edit and run **00_README_and_Config.ipynb** with:
```python
CATALOG = "kyc_demo"
SCHEMA_BRONZE = "bronze"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD   = "gold"
VOLUME_URI_RAW = "dbfs:/Volumes/kyc_demo/bronze/raw"
VOLUME_URI_REF = "dbfs:/Volumes/kyc_demo/bronze/ref"
```

---

## 🔄 5. Create Delta Live Tables Pipeline

In **Workflows → Delta Live Tables → Create Pipeline**:
- Source: `10_DLT_Pipeline.ipynb`
- Catalog: `kyc_demo`
- Target: `gold`
- Triggered (batch) mode ✅
- Photon ✅ ON
- Development mode ✅ ON
- Storage: `dbfs:/pipelines/kyc_reporting_factory_demo`

Run once to build Gold tables.

---

## 📊 6. Risk Scoring and SQL Views

**Run in order:**
1. `20_Risk_Scoring.ipynb` → produces `go_risk_scores` with MLflow metrics.
2. `30_SQL_Views.ipynb` → creates business views for Lakeview.

---

## 🧑‍💼 7. Streamlit App (Optional)

1. Open **Workspace → Apps → New App → Streamlit**.
2. Upload `/app/app.py` and `/app/databricks.yml`.
3. Configure environment variables:
   ```
   CATALOG=kyc_demo
   RAW_VOLUME=dbfs:/Volumes/kyc_demo/bronze/raw
   REF_VOLUME=dbfs:/Volumes/kyc_demo/bronze/ref
   JOB_ID=<your-job-id>
   DATABRICKS_HOST=https://<workspace-url>
   DATABRICKS_TOKEN=<personal-access-token>
   ```
4. Run the app → upload PaySim CSV → click “Run pipeline.”

---

## 🔐 8. Optional Workflow Job + Approval

Import `infra_samples/workflows.sample.json` → set IDs:  
- `DLT_PIPELINE_ID`  
- `SQL_WAREHOUSE_ID`  

Run with `approve=false` to test; re-run with `approve=true` to publish.

---

## 💰 9. Cost Optimization

| Component | Setting | Tip |
|------------|----------|-----|
| DLT | Triggered batch | Avoid continuous jobs |
| Cluster | Single node + Photon | ~90% cheaper |
| SQL Warehouse | Starter/Pro | Auto-stop 5–10 min |
| App | Serverless | Scales to zero |
| Data | 200k txns | Sufficient for demo |

Demo runtime cost: **< $5/day** (occasional runs).

---

## 🎬 10. Demo Flow Summary

| Step | What You Show | Persona |
|------|----------------|----------|
| Upload | PaySim CSV via app | Analyst |
| Validate | DLT expectations + lineage | Engineer |
| Score | MLflow metrics, risk bands | Analyst |
| Report | Lakeview dashboard | Business |
| Approve | Slack/Teams summary | Approver |
| Publish | Access grant to `kyc_consumers` | Compliance |

---

✅ You are ready to demo an **AI-assisted, business-user KYC Reporting Factory** on Azure Databricks!
