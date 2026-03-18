import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Page config (mobile friendly)
st.set_page_config(layout="wide", page_title="Seizure Dashboard")

# Auto refresh
st_autorefresh(interval=30000, key="refresh")

# Simple styling
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

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
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# Clean team
df["team"] = df["team"].astype(str).str.upper()

# REMOVE EMPTY ROWS (IMPORTANT FIX)
df = df.dropna(subset=["date", "amount"])

# Split teams
df_sst = df[df["team"] == "SST"]
df_fst = df[df["team"] == "FST"]

# ---------- HEADER ----------
st.markdown("<h3 style='text-align:center;'>📊 Seizure Summary</h3>", unsafe_allow_html=True)

# -------- FUNCTION --------
def show_table(data, title):
    st.markdown(f"<div class='big-font'>🚓 {title}</div>", unsafe_allow_html=True)

    if data.empty:
        st.warning(f"No data for {title}")
        return

    # Extra safety
    data = data.dropna(subset=["date"])

    # Date-wise total
    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    # Remove zero rows
    daily = daily[daily["amount"] > 0]

    # Cumulative
    daily["cumulative"] = daily["amount"].cumsum()

    # Total
    total = int(daily["amount"].sum())
    st.metric(f"{title} Total (₹)", f"{total:,}")

    # Format numbers
    daily["amount"] = daily["amount"].astype(int)
    daily["cumulative"] = daily["cumulative"].astype(int)

    # Table
    st.dataframe(daily, use_container_width=True)

    st.markdown("---")


# -------- DISPLAY --------
show_table(df_sst, "SST")
show_table(df_fst, "FST")

# -------- SUMMARY --------
st.markdown("<div class='big-font'>📌 Summary</div>", unsafe_allow_html=True)

team_total = df.groupby("team")["amount"].sum().reset_index()
team_total.columns = ["Team", "Total Amount (₹)"]

# Format numbers
team_total["Total Amount (₹)"] = team_total["Total Amount (₹)"].astype(int)

st.dataframe(team_total, use_container_width=True)

# Extract values
sst_total = team_total[team_total["Team"] == "SST"]["Total Amount (₹)"].sum()
fst_total = team_total[team_total["Team"] == "FST"]["Total Amount (₹)"].sum()
grand_total = int(df["amount"].sum())

# Metrics (stacked for mobile)
st.metric("🚓 SST Total (₹)", f"{int(sst_total):,}")
st.metric("🚓 FST Total (₹)", f"{int(fst_total):,}")
st.metric("💰 Grand Total (₹)", f"{grand_total:,}")