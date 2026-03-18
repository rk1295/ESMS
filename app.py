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

# Select required columns
df = df[[
    "TEAM NAME",
    "DATE AND TIME OF SIZED",
    "AMOUNT (IN Rupees)"
]].copy()

# Rename
df.columns = ["team", "datetime", "amount"]

# Convert datetime → date only
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["date"] = df["datetime"].dt.date

# Clean amount
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

# Clean team
df["team"] = df["team"].astype(str).str.upper()

# Split teams
df_sst = df[df["team"] == "SST"]
df_fst = df[df["team"] == "FST"]

st.title("📊 Seizure Summary (Date-wise)")

# -------- FUNCTION --------
def show_table(data, title):
    st.subheader(f"🚓 {title}")

    if data.empty:
        st.warning(f"No data for {title}")
        return

    # Date-wise total
    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    # Cumulative total
    daily["cumulative"] = daily["amount"].cumsum()

    # Total
    total = int(daily["amount"].sum())
    st.metric(f"{title} Total (₹)", total)

    # Table display
    st.dataframe(daily, use_container_width=True)


# -------- DISPLAY --------
col1, col2 = st.columns(2)

with col1:
    show_table(df_sst, "SST")

with col2:
    show_table(df_fst, "FST")
# -------- TEAM-WISE + GRAND TOTAL --------
st.subheader("📌 Summary")

team_total = df.groupby("team")["amount"].sum().reset_index()
team_total.columns = ["Team", "Total Amount (₹)"]

# Display table
st.dataframe(team_total, use_container_width=True)

# Extract values
sst_total = team_total[team_total["Team"] == "SST"]["Total Amount (₹)"].sum()
fst_total = team_total[team_total["Team"] == "FST"]["Total Amount (₹)"].sum()
grand_total = int(df["amount"].sum())

# Display metrics
col1, col2, col3 = st.columns(3)

col1.metric("🚓 SST Total (₹)", int(sst_total))
col2.metric("🚓 FST Total (₹)", int(fst_total))
col3.metric("💰 Grand Total (₹)", grand_total)
