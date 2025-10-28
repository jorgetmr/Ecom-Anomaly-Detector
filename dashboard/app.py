import requests, pandas as pd, streamlit as stl

stl.set_page_config(page_title="E-commerce Anomalies", layout="wide")
stl.title("📈 E-commerce Anomaly Monitor")

try:
    response = requests.get("http://localhost:8000/anomalies/latest", timeout=5)
    response.raise_for_status()
    rows = response.json()

    df = pd.DataFrame(rows)

    if not df.empty:

        if "ts" in df.columns:
            df["ts"] = pd.to_datetime(df["ts"])
            df = df.sort_values("ts", ascending=False)
        
        def color_severity(val):
            if val == "critical":
                return "background-color: #ff4d4d; color: white;"   # red
            elif val == "warn":
                return "background-color: #ffd633; color: black;"   # yellow
            elif val == "info":
                return "background-color: #85e085; color: black;"   # green
            else:
                return ""
        
        coloured_df = df.style.applymap(color_severity, subset=["severity"])

        stl.subheader("Recent Anomalies")
        stl.dataframe(coloured_df, use_container_width=True)


        stl.subheader("📊 Anomaly Score Trend")
        if "ts" in df.columns and "score" in df.columns:
            df_chart = df.sort_values("ts")
            
            stl.line_chart(
                df_chart,
                x="ts",
                y="score",
                color="#ff4d4d",  # red line for anomalies
                use_container_width=True
            )
        else:
            stl.info("No score or timestamp data available for plotting.")
    else:
        stl.info("No anomalies found yet.")

except Exception as e:
    stl.warning(f"⚠️ API not reachable or invalid response: {e}")
