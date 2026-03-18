import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Page config
st.set_page_config(layout="wide", page_title="Seizure Dashboard")

# Auto refresh
st_autorefresh(interval=30000, key="refresh")

# ---------- INDIAN NUMBER FORMAT ----------
def format_indian(n):
    n = int(n)
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    rest = ",".join([rest[max(i-2,0):i] for i in range(len(rest), 0, -2)][::-1])
    return rest + "," + last3

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

# Convert datetime → date
df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["date"] = df["datetime"].dt.date

# Clean amount
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

# Clean team
df["team"] = df["team"].astype(str).str.upper()

# Remove empty rows
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

    data = data.dropna(subset=["date"])

    # Date-wise total
    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    # Format date → MM-DD-YYYY
    daily["date"] = pd.to_datetime(daily["date"]).dt.strftime("%m-%d-%Y")

    # Remove zero rows
    daily = daily[daily["amount"] > 0]

    # Cumulative
    daily["cumulative"] = daily["amount"].cumsum()

    # Total
    total = int(daily["amount"].sum())
    st.metric(f"{title} Total (₹)", format_indian(total))

    # Format numbers
    daily["amount"] = daily["amount"].astype(int).apply(format_indian)
    daily["cumulative"] = daily["cumulative"].astype(int).apply(format_indian)

    # Table
    st.dataframe(daily, use_container_width=True)

    st.markdown("---")


# -------- DISPLAY --------
show_table(df_sst, "SST")
show_table(df_fst, "FST")

# -------- GRAND TOTAL --------
grand_total = int(df["amount"].sum())

st.markdown("<div class='big-font'>💰 Grand Total</div>", unsafe_allow_html=True)
st.metric("Total Seized (₹)", format_indian(grand_total))