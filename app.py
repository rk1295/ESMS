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

# Keep only required columns
df = df[[
    "DATE AND TIME OF SIZED",
    "AMOUNT (IN Rupees)",
    "NAME OF THE DESIGNATION OF THE AUTHORITY TO WHOME SIZED CASH/ITEMS IS HANDED OVER"
]].copy()

# Rename for simplicity
df.columns = ["datetime", "amount", "team"]

# Convert data
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["date"] = df["datetime"].dt.date
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
df["team"] = df["team"].astype(str).str.upper()

# Split teams
df_sst = df[df["team"].str.contains("SST", na=False)]
df_fst = df[df["team"].str.contains("FST", na=False)]

st.title("📊 Seizure Summary (SST vs FST)")

# -------- FUNCTION --------
def show_table(data, title):
    st.subheader(f"🚓 {title}")

    if data.empty:
        st.warning(f"No data for {title}")
        return

    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    daily["cumulative"] = daily["amount"].cumsum()

    # KPI
    st.metric(f"{title} Total (₹)", int(daily["amount"].sum()))

    # Table
    st.dataframe(daily)

    # Charts
    st.line_chart(daily.set_index("date")[["amount", "cumulative"]])


# -------- DISPLAY --------
col1, col2 = st.columns(2)

with col1:
    show_table(df_sst, "SST")

with col2:
    show_table(df_fst, "FST")