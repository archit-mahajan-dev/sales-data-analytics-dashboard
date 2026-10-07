"""Sales Data Analytics Dashboard - Streamlit app.
Author: Archit Mahajan
Run with:  streamlit run app.py
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")
CSV_PATH = "Sample - Superstore.csv"


def make_sample_data(seed=42, n=8000):
    rng = np.random.default_rng(seed)
    dates = pd.to_datetime("2022-01-01") + pd.to_timedelta(rng.integers(0, 4 * 365, n), unit="D")
    category = rng.choice(["Furniture", "Office Supplies", "Technology"], n, p=[0.25, 0.55, 0.20])
    base = {"Furniture": 350, "Office Supplies": 90, "Technology": 450}
    margin = {"Furniture": 0.04, "Office Supplies": 0.17, "Technology": 0.16}
    growth = 1 + 0.25 * (dates.year - 2022) + 0.15 * np.isin(dates.month, [11, 12])
    sales = np.array([base[c] for c in category]) * rng.lognormal(0, 0.35, n) * growth
    profit = sales * np.array([margin[c] for c in category]) + rng.normal(0, 8, n)
    return pd.DataFrame({
        "Order Date": dates,
        "Region": rng.choice(["West", "East", "Central", "South"], n, p=[0.32, 0.29, 0.23, 0.16]),
        "Category": category,
        "Sub-Category": rng.choice(["Chairs", "Tables", "Phones", "Binders", "Paper", "Accessories", "Storage"], n),
        "Segment": rng.choice(["Consumer", "Corporate", "Home Office"], n, p=[0.52, 0.30, 0.18]),
        "Sales": sales.round(2),
        "Quantity": rng.integers(1, 10, n),
        "Profit": profit.round(2),
    })


@st.cache_data
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, encoding="latin-1")
        source = "Kaggle Superstore dataset"
    else:
        df = make_sample_data()
        source = "Generated sample data"
    df = df.drop_duplicates()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df = df.dropna(subset=["Order Date", "Sales"])
    df["Year"] = df["Order Date"].dt.year
    return df, source


df, source = load_data()
st.title("Sales Data Analytics Dashboard")
st.caption(f"Data source: {source}")

# ---- Sidebar filters ----
st.sidebar.header("Filters")
years = st.sidebar.multiselect("Year", sorted(df["Year"].unique()), default=sorted(df["Year"].unique()))
regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
cats = st.sidebar.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
f = df[df["Year"].isin(years) & df["Region"].isin(regions) & df["Category"].isin(cats)]

if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ---- KPIs ----
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"{f['Sales'].sum():,.0f}")
c2.metric("Total Profit", f"{f['Profit'].sum():,.0f}")
c3.metric("Profit Margin", f"{f['Profit'].sum() / f['Sales'].sum() * 100:.1f}%")
c4.metric("Records", f"{len(f):,}")

# ---- Charts ----
monthly = f.groupby(f["Order Date"].dt.to_period("M"))["Sales"].sum().reset_index()
monthly["Order Date"] = monthly["Order Date"].dt.to_timestamp()

left, right = st.columns(2)
with left:
    st.subheader("Monthly Sales Trend")
    fig, ax = plt.subplots()
    ax.plot(monthly["Order Date"], monthly["Sales"], marker="o")
    ax.set_xlabel("Month"); ax.set_ylabel("Sales"); ax.grid(True)
    st.pyplot(fig)
with right:
    st.subheader("Sales by Category")
    fig, ax = plt.subplots()
    f.groupby("Category")["Sales"].sum().sort_values().plot(kind="barh", ax=ax, color="#1f77b4")
    ax.set_xlabel("Sales")
    st.pyplot(fig)

left, right = st.columns(2)
with left:
    st.subheader("Sales Share by Region")
    fig, ax = plt.subplots()
    r = f.groupby("Region")["Sales"].sum()
    ax.pie(r, labels=r.index, autopct="%1.1f%%", startangle=90)
    st.pyplot(fig)
with right:
    st.subheader("Top Sub-Categories")
    fig, ax = plt.subplots()
    f.groupby("Sub-Category")["Sales"].sum().sort_values().tail(7).plot(kind="barh", ax=ax, color="#ff7f0e")
    ax.set_xlabel("Sales")
    st.pyplot(fig)

# ---- Forecast ----
st.subheader("Sales Forecast (Linear Regression)")
months_ahead = st.slider("Months to forecast", 1, 12, 6)


def build_features(frame, seasonal):
    X = frame[["t"]].copy()
    if seasonal:
        for m in range(2, 13):
            X[f"m{m}"] = (frame["month_no"] == m).astype(int)
    return X


if len(monthly) < 4:
    st.info("Select more data (at least 4 months) to build a forecast.")
else:
    monthly = monthly.reset_index(drop=True)
    monthly["t"] = np.arange(len(monthly))
    monthly["month_no"] = monthly["Order Date"].dt.month
    seasonal = len(monthly) >= 24          # need at least 2 years to learn seasonality
    model = LinearRegression().fit(build_features(monthly, seasonal), monthly["Sales"])
    future_dates = pd.date_range(monthly["Order Date"].iloc[-1] + pd.offsets.MonthBegin(1),
                                 periods=months_ahead, freq="MS")
    future = pd.DataFrame({"t": np.arange(len(monthly), len(monthly) + months_ahead),
                           "month_no": future_dates.month})
    fc = pd.DataFrame({"Month": future_dates,
                       "Forecast Sales": model.predict(build_features(future, seasonal))})
    st.caption("Model: trend + monthly seasonality" if seasonal else "Model: trend only (less than 24 months selected)")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["Order Date"], monthly["Sales"], label="Actual")
    ax.plot(fc["Month"], fc["Forecast Sales"], "o-", color="#d62728", label="Forecast")
    ax.set_xlabel("Month"); ax.set_ylabel("Sales"); ax.grid(True); ax.legend()
    st.pyplot(fig)
    st.dataframe(fc.round({"Forecast Sales": 2}), use_container_width=True)

with st.expander("View raw data"):
    st.dataframe(f.head(200))
