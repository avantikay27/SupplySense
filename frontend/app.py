import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="SupplySense | Intelligence Hub",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root { --ink:#eaf0ff; --muted:#9aa9c4; --panel:#111d33; --line:rgba(148,163,184,.16); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp {
  background: radial-gradient(circle at 80% 0%, #172d50 0%, #0a1426 42%, #07101e 100%);
  color:var(--ink);
}
[data-testid="stHeader"] { background:rgba(7,16,30,.75); }
.block-container { padding-top:2rem; padding-bottom:3rem; max-width:1450px; }
section[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#101d33 0%,#0b1527 100%);
  border-right:1px solid var(--line);
}
section[data-testid="stSidebar"] * { color:#dce7fa; }
.brand { font-family:'Space Grotesk'; font-size:1.65rem; font-weight:700; letter-spacing:-.7px; }
.brand span { color:#58c7fa; }
.eyebrow { color:#6fcdf5; font-size:.74rem; font-weight:800; letter-spacing:2px; text-transform:uppercase; }
.hero-title { font-family:'Space Grotesk'; font-size:2.35rem; font-weight:700; letter-spacing:-1.2px; margin:0; color:#f4f7ff; }
.hero-sub { color:#9aabc6; font-size:1rem; margin-top:.35rem; }
.panel {
  background:linear-gradient(145deg,rgba(22,38,64,.94),rgba(15,27,47,.94));
  border:1px solid var(--line); border-radius:18px; padding:20px 22px;
  box-shadow:0 12px 35px rgba(0,0,0,.16);
}
.metric-label { color:#9aabc6; font-size:.78rem; font-weight:700; letter-spacing:.7px; text-transform:uppercase; }
.metric-value { color:#f4f7ff; font-family:'Space Grotesk'; font-size:1.8rem; font-weight:700; margin-top:.45rem; }
.metric-note { color:#6fcdf5; font-size:.78rem; margin-top:.25rem; }
.section-title { color:#f0f5ff; font-family:'Space Grotesk'; font-size:1.2rem; font-weight:700; margin:1.1rem 0 .25rem; }
.small-muted { color:#9aabc6; font-size:.86rem; }
div[data-testid="stMetric"] {
  background:linear-gradient(145deg,#172945,#101d32);
  border:1px solid rgba(148,163,184,.17); border-radius:16px;
  padding:18px 20px; box-shadow:0 10px 25px rgba(0,0,0,.12);
}
div[data-testid="stMetric"] label { color:#9aabc6 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#f4f7ff !important; font-family:'Space Grotesk'; }
.stButton>button {
  background:linear-gradient(90deg,#168bd2,#36b7df); color:white;
  border:0; border-radius:10px; padding:.62rem 1.15rem; font-weight:700;
}
.stButton>button:hover { background:linear-gradient(90deg,#0879bd,#1da4d2); color:white; border:0; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {
  background:#14243d; border-color:rgba(148,163,184,.24); border-radius:10px; color:#edf4ff;
}
.stSelectbox label, .stNumberInput label, .stSlider label { color:#c5d3e9 !important; }
.stDataFrame { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
hr { border-color:var(--line); }
footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- API HELPERS ----------------
@st.cache_data(ttl=90, show_spinner=False)
def api_get(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"_error": str(exc)}

def api_post(endpoint, payload):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        st.error(f"API error ({response.status_code}): {detail}")
    except requests.RequestException as exc:
        st.error(f"Backend connection failed: {exc}")
    return None

def show_api_error(data):
    if isinstance(data, dict) and data.get("_error"):
        st.error(f"Cannot reach SupplySense backend at {API_URL}. Start the FastAPI server and refresh this page.")
        with st.expander("Technical details"):
            st.code(data["_error"])
        return True
    return False

@st.cache_data(ttl=300, show_spinner=False)
def get_products():
    data = api_get("/forecast/products")
    if not data or show_api_error(data):
        return []
    return data.get("products", [])

def make_product_map(products):
    return {
        f"{p.get('Description') or 'Unknown product'}  ·  {p.get('StockCode')}": str(p.get("StockCode"))
        for p in products
    }

def chart_layout(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#c7d5eb"),
        title_font=dict(family="Space Grotesk", size=16, color="#f2f6ff"),
        height=height,
        margin=dict(l=12, r=12, t=55, b=12),
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.12)"),
        yaxis=dict(gridcolor="rgba(148,163,184,.12)", zerolinecolor="rgba(148,163,184,.12)"),
    )
    return fig

def page_header(kicker, title, subtitle):
    st.markdown(f'<div class="eyebrow">{kicker}</div><h1 class="hero-title">{title}</h1><div class="hero-sub">{subtitle}</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown('<div class="brand">📦 Supply<span>Sense</span></div>', unsafe_allow_html=True)
    st.caption("DEMAND INTELLIGENCE PLATFORM")
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Product Explorer", "Demand Forecast", "Inventory Planner"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**SYSTEM STATUS**")
    health = api_get("/analytics/overview")
    if isinstance(health, dict) and not health.get("_error"):
        st.success("Backend connected")
    else:
        st.warning("Backend connection unavailable")
    st.markdown("---")
    st.caption("SUPPLYSENSE  ·  BTECH PROJECT")
    st.caption("Demand forecasting & inventory planning")

# ---------------- OVERVIEW ----------------
if page == "Overview":
    page_header("COMMAND CENTER", "Business overview", "A live snapshot of sales activity, product coverage and customer demand.")
    overview = api_get("/analytics/overview")
    if show_api_error(overview):
        st.stop()
    if overview:
        a, b, c, d = st.columns(4)
        a.metric("Total records", f"{overview.get('total_records', 0):,}")
        b.metric("Total revenue", f"£{overview.get('total_revenue', 0):,.2f}")
        c.metric("Products", f"{overview.get('total_products', 0):,}")
        d.metric("Customers", f"{overview.get('total_customers', 0):,}")
    st.markdown('<div class="section-title">Demand performance</div><div class="small-muted">Daily units sold across the transaction history</div>', unsafe_allow_html=True)
    daily_data = api_get("/analytics/daily-demand")
    if show_api_error(daily_data):
        st.stop()
    if daily_data:
        df = pd.DataFrame(daily_data)
        if {"date", "sales"}.issubset(df.columns):
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df["sales"] = pd.to_numeric(df["sales"], errors="coerce")
            df = df.dropna(subset=["date", "sales"]).sort_values("date")
            fig = px.area(df, x="date", y="sales", title="Daily demand trend")
            fig.update_traces(line_color="#39b8e8", fillcolor="rgba(57,184,232,.13)")
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        else:
            st.info("Daily demand data was returned, but expected date/sales fields were not found.")
    else:
        st.info("No daily demand data available.")

# ---------------- PRODUCT EXPLORER ----------------
elif page == "Product Explorer":
    page_header("CATALOG INTELLIGENCE", "Product explorer", "Inspect product-level demand history and identify sales patterns.")
    products = get_products()
    if not products:
        st.warning("No products are available from the backend.")
        st.stop()
    product_map = make_product_map(products)
    selected = st.selectbox("Select product", list(product_map.keys()), key="explorer_product")
    stock_code = product_map[selected]
    st.markdown(f'<div class="panel"><div class="metric-label">Selected stock code</div><div class="metric-value">{stock_code}</div><div class="metric-note">Historical product performance</div></div>', unsafe_allow_html=True)
    demand_data = api_get(f"/products/{stock_code}/demand")
    if show_api_error(demand_data):
        st.stop()
    if demand_data:
        history = pd.DataFrame(demand_data.get("daily_demand", []))
        if not history.empty:
            date_col = "date" if "date" in history.columns else "Date" if "Date" in history.columns else None
            qty_col = next((col for col in ["Quantity", "sales", "quantity"] if col in history.columns), None)
            if date_col and qty_col:
                history[date_col] = pd.to_datetime(history[date_col], errors="coerce")
                history[qty_col] = pd.to_numeric(history[qty_col], errors="coerce")
                history = history.dropna(subset=[date_col, qty_col]).sort_values(date_col)
                total_units = history[qty_col].sum()
                avg_units = history[qty_col].mean()
                peak_units = history[qty_col].max()
                x, y, z = st.columns(3)
                x.metric("Units sold", f"{total_units:,.0f}")
                y.metric("Average daily demand", f"{avg_units:,.1f}")
                z.metric("Peak daily demand", f"{peak_units:,.0f}")
                fig = px.line(history, x=date_col, y=qty_col, markers=True, title=f"Historical demand · {stock_code}")
                fig.update_traces(line_color="#39b8e8", marker_color="#8be0ff")
                st.plotly_chart(chart_layout(fig), use_container_width=True)
            st.markdown('<div class="section-title">Recent demand records</div>', unsafe_allow_html=True)
            st.dataframe(history.tail(20), use_container_width=True, hide_index=True)
        else:
            st.info("No historical demand data available for this product.")

# ---------------- DEMAND FORECAST ----------------
elif page == "Demand Forecast":
    page_header("PREDICTIVE ANALYTICS", "Demand forecast", "Generate product-wise demand predictions using the connected forecasting model.")
    products = get_products()
    if not products:
        st.warning("No products are available from the backend.")
        st.stop()
    product_map = make_product_map(products)
    selected = st.selectbox("Choose product", list(product_map.keys()), key="forecast_product")
    stock_code = product_map[selected]
    left, right = st.columns([1, 1])
    with left:
        days = st.select_slider("Forecast horizon", options=[7, 14, 30], value=7, format_func=lambda x: f"{x} days")
    with right:
        st.markdown('<div class="panel"><div class="metric-label">Forecast target</div><div class="metric-value">Product-level</div><div class="metric-note">Selected SKU · '+stock_code+'</div></div>', unsafe_allow_html=True)
    if st.button("⚡ Generate forecast", type="primary", use_container_width=False):
        with st.spinner("Running demand prediction..."):
            result = api_post("/forecast/", {"stock_code": stock_code, "days": days})
        if result:
            st.session_state["last_forecast"] = result
            st.session_state["last_forecast_sku"] = stock_code
    result = st.session_state.get("last_forecast") if st.session_state.get("last_forecast_sku") == stock_code else None
    if result:
        st.success("Forecast generated successfully.")
        a, b, c = st.columns(3)
        a.metric("Product", stock_code)
        b.metric("Forecast period", f"{result.get('forecast_days', days)} days")
        c.metric("Predicted demand", f"{result.get('total_predicted_demand', 0):,.2f} units")
        forecast_df = pd.DataFrame(result.get("forecast", []))
        if not forecast_df.empty:
            date_col = "Date" if "Date" in forecast_df.columns else "date" if "date" in forecast_df.columns else None
            demand_col = "Predicted_Demand" if "Predicted_Demand" in forecast_df.columns else "predicted_demand" if "predicted_demand" in forecast_df.columns else None
            if date_col and demand_col:
                forecast_df[date_col] = pd.to_datetime(forecast_df[date_col], errors="coerce")
                forecast_df[demand_col] = pd.to_numeric(forecast_df[demand_col], errors="coerce")
                fig = px.area(forecast_df, x=date_col, y=demand_col, markers=True, title="Predicted product demand")
                fig.update_traces(line_color="#39b8e8", fillcolor="rgba(57,184,232,.13)")
                st.plotly_chart(chart_layout(fig, 390), use_container_width=True)
            st.markdown('<div class="section-title">Forecast details</div>', unsafe_allow_html=True)
            st.dataframe(forecast_df, use_container_width=True, hide_index=True)
            st.download_button("↓ Download forecast CSV", forecast_df.to_csv(index=False), file_name=f"forecast_{stock_code}.csv", mime="text/csv")

# ---------------- INVENTORY PLANNER ----------------
elif page == "Inventory Planner":
    page_header("INVENTORY OPTIMIZATION", "Inventory planner", "Calculate reorder points and suggested order quantities from forecast demand.")
    products = get_products()
    if not products:
        st.warning("No products are available from the backend.")
        st.stop()
    product_map = make_product_map(products)
    selected = st.selectbox("Select product", list(product_map.keys()), key="inventory_product")
    stock_code = product_map[selected]
    st.markdown('<div class="section-title">Stock parameters</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        current_stock = st.number_input("Current stock (units)", min_value=0, value=100, step=10)
    with c2:
        lead_time = st.number_input("Supplier lead time (days)", min_value=1, max_value=30, value=7)
    with c3:
        safety_days = st.number_input("Safety stock (days)", min_value=0, max_value=30, value=3)
    if st.button("Calculate recommendation", type="primary"):
        with st.spinner("Analysing stock requirements..."):
            result = api_post("/inventory/recommendation", {
                "stock_code": stock_code,
                "current_stock": current_stock,
                "lead_time_days": lead_time,
                "safety_stock_days": safety_days,
            })
        if result:
            st.session_state["last_inventory"] = result
            st.session_state["last_inventory_sku"] = stock_code
    result = st.session_state.get("last_inventory") if st.session_state.get("last_inventory_sku") == stock_code else None
    if result:
        st.markdown('<div class="section-title">Recommendation summary</div>', unsafe_allow_html=True)
        a, b, c = st.columns(3)
        a.metric("Current stock", f"{result.get('current_stock', 0):,.0f} units")
        b.metric("Reorder point", f"{result.get('reorder_point', 0):,.2f}")
        c.metric("Recommended order", f"{result.get('recommended_order_quantity', 0):,} units")
        if result.get("inventory_status") == "REORDER":
            st.error("⚠️ Reorder required — current stock is below the calculated reorder point.")
        else:
            st.success("✓ Stock level sufficient — no reorder is currently required.")
        breakdown = pd.DataFrame({
            "Category": ["Lead-time demand", "Safety stock"],
            "Units": [result.get("forecast_lead_time_demand", 0), result.get("calculated_safety_stock", 0)],
        })
        fig = px.bar(breakdown, x="Category", y="Units", text="Units", title="Inventory requirement breakdown")
        fig.update_traces(marker_color="#269fd5", textposition="outside")
        st.plotly_chart(chart_layout(fig, 330), use_container_width=True)
        forecast_df = pd.DataFrame(result.get("forecast", []))
        if not forecast_df.empty:
            st.markdown('<div class="section-title">Forecast used for this recommendation</div>', unsafe_allow_html=True)
            st.dataframe(forecast_df, use_container_width=True, hide_index=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown('<div class="small-muted">SUPPLYSENSE · Smart demand forecasting & inventory planning</div>', unsafe_allow_html=True)
