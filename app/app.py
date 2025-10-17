import os, io, time
import streamlit as st
import pandas as pd
from databricks import sql
import requests

CATALOG = os.getenv("CATALOG", "kyc_demo")
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID", "")
JOB_ID = os.getenv("JOB_ID", "")
RAW_VOLUME = os.getenv("RAW_VOLUME", "dbfs:/Volumes/kyc_demo/bronze/raw")
HOST = os.getenv("DATABRICKS_HOST", "")
TOKEN = os.getenv("DATABRICKS_TOKEN", "")
HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH", "")

st.set_page_config(page_title="KYC Reporting App", layout="wide")
st.title("🛡️ KYC Reporting Factory (Business App)")

st.header("1) Upload PaySim CSV")
up = st.file_uploader("Drop a PaySim extract (CSV)", type=["csv"])
if up:
    bytes_data = up.getvalue()
    save_path = f"/dbfs{RAW_VOLUME.replace('dbfs:','')}/paysim/{up.name}"
    with open(save_path, "wb") as f:
        f.write(bytes_data)
    st.success(f"Uploaded to {save_path}")
    df_preview = pd.read_csv(io.BytesIO(bytes_data), nrows=200)
    st.dataframe(df_preview, use_container_width=True)

st.header("2) Run pipeline")
if st.button("Run end-to-end job"):
    if not (HOST and TOKEN and JOB_ID):
        st.error("Missing DATABRICKS_HOST, DATABRICKS_TOKEN or JOB_ID")
    else:
        r = requests.post(
            f"{HOST}/api/2.1/jobs/run-now",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"job_id": int(JOB_ID), "job_parameters": {"approve": "false"}}
        )
        if r.ok:
            run_id = r.json()["run_id"]
            st.info(f"Triggered job run: {run_id}. Polling status…")
            while True:
                s = requests.get(f"{HOST}/api/2.1/jobs/runs/get",
                                 headers={"Authorization": f"Bearer {TOKEN}"},
                                 params={"run_id": run_id})
                state = s.json()["state"]["life_cycle_state"]
                st.write(f"Status: {state}")
                if state in ("TERMINATED", "INTERNAL_ERROR", "SKIPPED"):
                    break
                time.sleep(5)
            st.success("Job completed.")
        else:
            st.error(f"Run-now failed: {r.status_code} {r.text}")

st.header("3) Explore high-risk results")
http_path = st.text_input("Warehouse HTTP Path", value=HTTP_PATH)
if st.button("Load table"):
    try:
        with sql.connect(server_hostname=HOST.replace("https://",""),
                         http_path=http_path,
                         access_token=TOKEN) as conn:
            cur = conn.cursor()
            table = f"{CATALOG}.gold.go_report_views_highrisk"
            cur.execute(f"SELECT entity_id, geo_risk, risk_score, band, run_ts FROM {table} ORDER BY risk_score DESC LIMIT 200")
            rows = cur.fetchall()
            import pandas as pd
            pdf = pd.DataFrame(rows, columns=[c[0] for c in cur.description])
            st.dataframe(pdf, use_container_width=True)
    except Exception as e:
        st.error(f"Query failed: {e}")

st.header("4) Ask in natural language")
q = st.text_input("e.g., 'Show high-risk PEPs in India last 30 days'")
if st.button("Generate SQL"):
    st.info("Connect this to your LLM endpoint or use Databricks Assistant in SQL Editor.")
