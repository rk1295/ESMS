import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto refresh
st_autorefresh(interval=30000, key="refresh")

st.set_page_config(layout="wide")

# Google Sheet CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1sd6JLZt3PTx7qBtwYjFSuxna6eYKXGJyHqmMw-KCZBk/export?format=csv&gid=1516321852"

# Load data
try:
    df = pd.read_csv(sheet_url)
except:
    st.error("Error loading Google Sheet. Check sharing settings.")
    st.stop()

# Clean column names (VERY IMPORTANT)
df.columns = df.columns.str.strip()

# Rename for easier handling
df = df.rename(columns={
    "DATE AND TIME OF SIZED": "datetime",
    "AMOUNT (IN Rupees)": "amount",
    "NAME OF THE DESIGNATION OF THE AUTHORITY TO WHOME SIZED CASH/ITEMS IS HANDED OVER": "team_raw"
})

# Convert datetime
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["Date"] = df["datetime"].dt.date

# Clean amount
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

# Identify team type
df["team_raw"] = df["team_raw"].astype(str).str.upper()

df_sst = df[df["team_raw"].str.contains("SST", na=False)]
df_fst = df[df["team_raw"].str.contains("FST", na=False)]

st.title("📡 Live Seizure Monitoring Dashboard")

# -------- FUNCTION --------
def process_data(data, title):
    st.subheader(f"🚓 {title}")

    if data.empty:
        st.warning(f"No data for {title}")
        return

    daily = data.groupby("Date")["amount"].sum().reset_index()
    daily = daily.sort_values("Date")

    daily["Cumulative"] = daily["amount"].cumsum()

    total = int(daily["amount"].sum())

    today = pd.to_datetime("today").date()
    today_total = int(daily[daily["Date"] == today]["amount"].sum())

    col1, col2 = st.columns(2)
    col1.metric(f"{title} Total (₹)", total)
    col2.metric(f"{title} Today (₹)", today_total)

    col3, col4 = st.columns(2)

    with col3:
        st.write("Daily Trend")
        st.line_chart(daily.set_index("Date")["amount"])

    with col4:
        st.write("Cumulative Trend")
        st.line_chart(daily.set_index("Date")["Cumulative"])

    st.dataframe(daily)


# -------- DISPLAY --------
process_data(df_sst, "SST")
process_data(df_fst, "FST")