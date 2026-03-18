import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Page config (important for mobile)
st.set_page_config(layout="wide", page_title="Seizure Dashboard")

# Auto refresh
st_autorefresh(interval=30000, key="refresh")

# Custom CSS (mobile-friendly)
st.markdown("""
<style>
.big-font {
    font-size:22px !important;
    font-weight:600;
}
.metric-big {
    font-size:26px !important;
}
</style>
""", unsafe_allow_html=True)

# Google Sheet CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1sd6JLZt3PTx7qBtwYjFSuxna6eYKXGJyHqmMw-KCZBk/export?format=csv&gid=1516321852"

# Load data
df = pd.read_csv(sheet_url)

df.columns = df.columns.str.strip()

df = df[[
    "TEAM NAME",
    "DATE AND TIME OF SIZED",
    "AMOUNT (IN Rupees)"
]].copy()

df.columns = ["team", "datetime", "amount"]

df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
df["date"] = df["datetime"].dt.date

df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
df["team"] = df["team"].astype(str).str.upper()

df_sst = df[df["team"] == "SST"]
df_fst = df[df["team"] == "FST"]

# ---------- HEADER ----------
st.markdown("<h2 style='text-align:center;'>📊 Seizure Summary</h2>", unsafe_allow_html=True)

# -------- FUNCTION --------
def show_table(data, title):
    st.markdown(f"<div class='big-font'>🚓 {title}</div>", unsafe_allow_html=True)

    if data.empty:
        st.warning(f"No data for {title}")
        return

    daily = data.groupby("date")["amount"].sum().reset_index()
    daily = daily.sort_values("date")

    daily["cumulative"] = daily["amount"].cumsum()

    total = int(daily["amount"].sum())

    # Highlight total
    st.metric(label=f"{title} Total (₹)", value=f"{total:,}")

    # Better table formatting
    daily["amount"] = daily["amount"].astype(int)
    daily["cumulative"] = daily["cumulative"].astype(int)

    st.dataframe(
        daily,
        use_container_width=True,
        height=300
    )

    st.markdown("---")


# -------- MOBILE FRIENDLY STACK (NO SIDE-BY-SIDE) --------
show_table(df_sst, "SST")
show_table(df_fst, "FST")

# -------- SUMMARY --------
st.markdown("<div class='big-font'>📌 Summary</div>", unsafe_allow_html=True)

team_total = df.groupby("team")["amount"].sum().reset_index()
team_total.columns = ["Team", "Total Amount (₹)"]

st.dataframe(team_total, use_container_width=True)

sst_total = team_total[team_total["Team"] == "SST"]["Total Amount (₹)"].sum()
fst_total = team_total[team_total["Team"] == "FST"]["Total Amount (₹)"].sum()
grand_total = int(df["amount"].sum())

# Stack metrics for mobile
st.metric("🚓 SST Total (₹)", f"{int(sst_total):,}")
st.metric("🚓 FST Total (₹)", f"{int(fst_total):,}")
st.metric("💰 Grand Total (₹)", f"{grand_total:,}")