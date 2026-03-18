import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Auto refresh every 30 seconds
st_autorefresh(interval=30000, key="refresh")

st.set_page_config(layout="wide")

# Google Sheet CSV URL
sheet_url = "https://docs.google.com/spreadsheets/d/1sd6JLZt3PTx7qBtwYjFSuxna6eYKXGJyHqmMw-KCZBk/export?format=csv&gid=1516321852"

# Load data
df = pd.read_csv(sheet_url)

# Clean columns
df.columns = df.columns.str.strip()

# Convert timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df["Date"] = df["Timestamp"].dt.date

# Clean amount
df["AMOUNT (IN Rupees)"] = pd.to_numeric(df["AMOUNT (IN Rupees)"], errors="coerce").fillna(0)

st.title("📡 Live Seizure Monitoring Dashboard")

# Team filter
team_option = st.selectbox("Select Team", ["BOTH", "FST", "SST"])

if team_option != "BOTH":
    df = df[df["TEAM NAME"].str.contains(team_option, na=False)]

# Aggregate data
daily = df.groupby("Date")["AMOUNT (IN Rupees)"].sum().reset_index()
daily = daily.sort_values("Date")

# Cumulative calculation
daily["Cumulative Amount"] = daily["AMOUNT (IN Rupees)"].cumsum()

# KPIs
st.metric("💰 Total Seized (₹)", int(daily["AMOUNT (IN Rupees)"].sum()))

today = pd.to_datetime("today").date()
today_total = daily[daily["Date"] == today]["AMOUNT (IN Rupees)"].sum()
st.metric("🔥 Today's Seizure (₹)", int(today_total))

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Daily Seizure")
    st.line_chart(daily.set_index("Date")["AMOUNT (IN Rupees)"])

with col2:
    st.subheader("📊 Cumulative Seizure")
    st.line_chart(daily.set_index("Date")["Cumulative Amount"])

# Table
st.subheader("📄 Data Table")
st.dataframe(daily)
