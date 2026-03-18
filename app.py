import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto refresh every 30 sec
st_autorefresh(interval=30000, key="refresh")

st.set_page_config(layout="wide")

# Google Sheet CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1sd6JLZt3PTx7qBtwYjFSuxna6eYKXGJyHqmMw-KCZBk/export?format=csv&gid=1516321852"

# Load data
df = pd.read_csv(sheet_url)

# Clean column names
df.columns = df.columns.str.strip()

# Select only required columns
df = df[[
    "TEAM NAME",
    "DATE AND TIME OF SIZED",
    "AMOUNT (IN Rupees)"
]].copy()

# Rename for simplicity
df.columns = ["team", "datetime", "amount"]

# Convert datetime → DATE only
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["date"] = df["datetime"].dt.date

# Clean amount
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

# Clean team
df["team"] = df["team"].astype(str).str.upper()

# Split SST and FST
df_sst = df[df["team"] == "SST"]
df_fst = df[df["team"] == "FST"]

st.title("📊 Seizure Dashboard (SST vs FST)")

# -------- FUNCTION --------
def process(data, title):
    st.subheader(f"🚓 {title}")

    if data.empty:
        st.warning(f"No data for {title}")
        return

    # Date-wise total
    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    # Cumulative
    daily["cumulative"] = daily["amount"].cumsum()

    # KPI
    total = int(daily["amount"].sum())
    st.metric(f"{title} Total (₹)", total)

    # Table
    st.dataframe(daily)

    # Charts
    st.line_chart(daily.set_index("date")[["amount", "cumulative"]])


# -------- DISPLAY --------
col1, col2 = st.columns(2)

with col1:
    process(df_sst, "SST")

with col2:
    process(df_fst, "FST")