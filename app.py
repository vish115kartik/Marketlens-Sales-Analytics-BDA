from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="MarketLens | E-Commerce Analytics",
    page_icon=":material/monitoring:",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "data" / "ecommerce_sales_synthetic.csv"
PERIOD_DAYS = {"Past week": 6, "Past month": 29, "Past 3 months": 90, "Past 6 months": 182}
VIEWS = ["Overview", "Customer intelligence", "Product & operations", "Scenario lab", "Data quality"]


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
    data["gross_sales"] = data["quantity"] * data["list_unit_price"]
    data["revenue"] = data["quantity"] * data["unit_price"]
    data["discount_amount"] = data["gross_sales"] - data["revenue"]
    data["profit"] = data["quantity"] * (data["unit_price"] - data["unit_cost"])
    data["month"] = data["order_date"].dt.to_period("M").dt.to_timestamp()
    data["week_start"] = data["order_date"].dt.to_period("W").dt.start_time
    return data


def money(value: float) -> str:
    return f"₹{value:,.0f}"


def chart_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        margin=dict(l=12, r=12, t=56, b=12),
        title_font_size=17,
        legend_title_text="",
        hoverlabel=dict(font_size=13),
    )
    return fig


df = load_data()
min_date = df.order_date.min().date()
max_date = df.order_date.max().date()

st.title("MarketLens")
st.caption("E-commerce performance, customer behavior, and pricing analytics")
st.info(
    f"Demo workspace · Synthetic sample data · {min_date:%d %b %Y} — {max_date:%d %b %Y}",
    icon=":material/info:",
)

with st.sidebar:
    st.subheader("Analysis controls")
    date_window = st.selectbox("Date window", [*PERIOD_DAYS, "Custom range"], index=3)
    if date_window == "Custom range":
        selected_dates = st.date_input("Order dates", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            start_date, end_date = min_date, max_date
    else:
        end_date = max_date
        start_date = max(min_date, end_date - pd.Timedelta(days=PERIOD_DAYS[date_window]))
    selected_regions = st.multiselect("Region", sorted(df.region.unique()), default=sorted(df.region.unique()))
    selected_categories = st.multiselect("Category", sorted(df.category.unique()), default=sorted(df.category.unique()))
    selected_channels = st.multiselect("Sales channel", sorted(df.sales_channel.unique()), default=sorted(df.sales_channel.unique()))
    selected_statuses = st.multiselect("Fulfillment status", sorted(df.fulfillment_status.unique()), default=sorted(df.fulfillment_status.unique()))
    st.divider()
    st.caption("All records are fictional and generated for demonstration.")

filtered = df[
    df.order_date.dt.date.between(start_date, end_date)
    & df.region.isin(selected_regions)
    & df.category.isin(selected_categories)
    & df.sales_channel.isin(selected_channels)
    & df.fulfillment_status.isin(selected_statuses)
].copy()

if filtered.empty:
    st.warning("No orders match the selected filters. Adjust the controls in the sidebar.", icon=":material/filter_alt_off:")
    st.stop()

with st.container(horizontal=True, horizontal_alignment="distribute"):
    st.metric("Analysis view", f"{len(filtered):,} order records")
    st.metric("Selected window", f"{start_date:%d %b} — {end_date:%d %b %Y}")
    st.metric("Distinct customers", f"{filtered.customer_id.nunique():,}")

view = st.segmented_control("Choose an analysis", VIEWS, default="Overview", key="analysis_view", width="stretch")

if view == "Overview":
    st.subheader("Executive overview")
    revenue = filtered.revenue.sum()
    profit = filtered.profit.sum()
    orders = filtered.order_id.nunique()
    units = filtered.quantity.sum()
    margin = profit / revenue if revenue else 0
    avg_order_value = revenue / orders if orders else 0
    with st.grid(3, gap="small"):
        st.metric("Net sales", money(revenue), border=True)
        st.metric("Gross profit", money(profit), border=True)
        st.metric("Orders", f"{orders:,}", border=True)
        st.metric("Units sold", f"{units:,}", border=True)
        st.metric("Profit margin", f"{margin:.1%}", border=True)
        st.metric("Average order value", money(avg_order_value), border=True)

    trend = filtered.groupby("month", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    category = filtered.groupby("category", as_index=False).agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
    left, right = st.columns(2)
    with left:
        fig = px.line(trend, x="month", y=["revenue", "profit"], markers=True,
                      title="Sales and profit trend", labels={"month": "Month", "value": "₹", "variable": "Metric"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Monthly sales and gross profit over the selected period")
    with right:
        fig = px.bar(category.sort_values("revenue", ascending=False), x="category", y="revenue", color="profit",
                     title="Category contribution", color_continuous_scale="Tealgrn",
                     labels={"category": "Category", "revenue": "Net sales (₹)", "profit": "Gross profit (₹)"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Net sales by category, shaded by gross profit")

    region = filtered.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
    channel = filtered.groupby("sales_channel", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
    left, right = st.columns(2)
    with left:
        fig = px.bar(region.sort_values("revenue"), x="revenue", y="region", orientation="h", color="revenue",
                     title="Regional performance", labels={"revenue": "Net sales (₹)", "region": "Region"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Net sales by region")
    with right:
        fig = px.pie(channel, names="sales_channel", values="revenue", hole=0.58, title="Sales channel mix")
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Share of net sales by sales channel")

    top_category = category.sort_values("revenue", ascending=False).iloc[0]
    top_region = region.sort_values("revenue", ascending=False).iloc[0]
    st.success(
        f"{top_category['category']} is the leading category with {money(top_category['revenue'])} in sales. "
        f"{top_region['region']} leads regional sales with {money(top_region['revenue'])}.",
        icon=":material/insights:",
    )

elif view == "Customer intelligence":
    st.subheader("Customer intelligence")
    st.caption("RFM groups customers by recency, order frequency, and sales value within the selected date window.")
    customers = filtered.groupby("customer_id", as_index=False).agg(
        last_order=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum"),
        units=("quantity", "sum"),
        segment=("customer_segment", "last"),
    )
    customers["recency_days"] = (filtered.order_date.max() - customers.last_order).dt.days
    customers["recency_score"] = 1 - customers.recency_days.rank(pct=True)
    customers["frequency_score"] = customers.frequency.rank(pct=True)
    customers["monetary_score"] = customers.monetary.rank(pct=True)
    customers["rfm_score"] = 0.4 * customers.recency_score + 0.3 * customers.frequency_score + 0.3 * customers.monetary_score
    customers["rfm_group"] = pd.cut(
        customers.rfm_score.rank(method="first", pct=True),
        bins=[0, 0.25, 0.5, 0.75, 1],
        labels=["Needs attention", "At risk", "Growing", "Top customers"],
        include_lowest=True,
    )
    repeat_share = (customers.frequency.gt(1).mean() * 100) if len(customers) else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Customers", f"{len(customers):,}", border=True)
    c2.metric("Repeat customer share", f"{repeat_share:.1f}%", border=True)
    c3.metric("Sales per customer", money(customers.monetary.mean()), border=True)

    groups = customers.groupby("rfm_group", observed=False, as_index=False).agg(
        customers=("customer_id", "count"), sales=("monetary", "sum")
    )
    left, right = st.columns(2)
    with left:
        fig = px.bar(groups, x="rfm_group", y="customers", color="rfm_group", title="RFM customer groups",
                     labels={"rfm_group": "Customer group", "customers": "Customers"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Number of customers in each RFM group")
    with right:
        fig = px.scatter(customers, x="frequency", y="monetary", size="units", color="rfm_group",
                         hover_data=["customer_id", "recency_days"], title="Customer value and order frequency",
                         labels={"frequency": "Orders", "monetary": "Net sales (₹)", "rfm_group": "RFM group"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Customer order frequency versus sales value, grouped by RFM score")

    st.markdown("**Highest value customers in this filtered sample**")
    st.dataframe(customers.sort_values("monetary", ascending=False).head(15)[
        ["customer_id", "segment", "frequency", "recency_days", "monetary", "rfm_group"]
    ], width="stretch", hide_index=True, column_config={"monetary": st.column_config.NumberColumn("Net sales", format="₹%.2f")})
    st.caption("RFM labels are calculated from this filtered synthetic sample; they are illustrative segments, not validated marketing predictions.")

elif view == "Product & operations":
    st.subheader("Product & operations")
    product = filtered.groupby(["product_id", "product_name", "category"], as_index=False).agg(
        revenue=("revenue", "sum"), profit=("profit", "sum"), units=("quantity", "sum"),
        discount=("discount_pct", "mean"),
    )
    product["margin_pct"] = product.profit.div(product.revenue.where(product.revenue.ne(0))).fillna(0) * 100
    delivered = filtered[filtered.fulfillment_status == "Delivered"]
    o1, o2, o3 = st.columns(3)
    o1.metric("Delivered order share", f"{filtered.fulfillment_status.eq('Delivered').mean():.1%}", border=True)
    o2.metric("Average delivery time", f"{delivered.shipping_days.mean():.1f} days" if not delivered.empty else "—", border=True)
    o3.metric("Average discount", f"{filtered.discount_pct.mean():.1f}%", border=True)

    left, right = st.columns(2)
    with left:
        fig = px.scatter(product, x="revenue", y="margin_pct", size="units", color="category",
                         hover_name="product_name", title="Product sales and margin",
                         labels={"revenue": "Net sales (₹)", "margin_pct": "Profit margin (%)", "category": "Category"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Product sales versus profit margin, sized by units sold")
    with right:
        status = filtered.groupby("fulfillment_status", as_index=False).agg(orders=("order_id", "nunique"))
        fig = px.funnel(status.sort_values("orders", ascending=False), x="orders", y="fulfillment_status",
                        title="Fulfillment status mix", labels={"orders": "Orders", "fulfillment_status": "Status"})
        st.plotly_chart(chart_layout(fig), width="stretch", alt="Order count by fulfillment status")

    st.markdown("**Product scorecard**")
    st.dataframe(product.sort_values("revenue", ascending=False), width="stretch", hide_index=True,
                 column_config={"revenue": st.column_config.NumberColumn("Net sales", format="₹%.2f"),
                                "profit": st.column_config.NumberColumn("Gross profit", format="₹%.2f"),
                                "margin_pct": st.column_config.NumberColumn("Margin", format="%.1f%%"),
                                "discount": st.column_config.NumberColumn("Avg. discount", format="%.1f%%")})

elif view == "Scenario lab":
    st.subheader("Pricing scenario lab")
    st.caption("Estimate a price change for one product. This is a sensitivity calculation, not a demand forecast.")
    product_list = sorted(filtered.product_name.unique())
    selected_product = st.selectbox("Product", product_list)
    change = st.slider("Price change", min_value=-20, max_value=20, value=5, step=1, format="%d%%")
    item = filtered[filtered.product_name == selected_product]
    units = int(item.quantity.sum())
    baseline_sales = float(item.revenue.sum())
    baseline_profit = float(item.profit.sum())
    avg_price = baseline_sales / units if units else 0
    avg_cost = float((item.unit_cost * item.quantity).sum() / units) if units else 0
    scenario_price = avg_price * (1 + change / 100)
    scenario_sales = scenario_price * units
    scenario_profit = (scenario_price - avg_cost) * units
    profit_delta = scenario_profit - baseline_profit
    break_even_units = (baseline_profit / (scenario_price - avg_cost)) if scenario_price > avg_cost else None

    a, b, c = st.columns(3)
    a.metric("Current sales", money(baseline_sales), border=True)
    b.metric("Scenario sales", money(scenario_sales), f"{change:+d}% price", border=True)
    c.metric("Scenario gross profit", money(scenario_profit), f"{money(profit_delta)} vs current", border=True)
    st.plotly_chart(
        chart_layout(go.Figure(data=[
            go.Bar(name="Current", x=["Sales", "Gross profit"], y=[baseline_sales, baseline_profit]),
            go.Bar(name="Scenario", x=["Sales", "Gross profit"], y=[scenario_sales, scenario_profit]),
        ]).update_layout(barmode="group", title="Current versus scenario")),
        width="stretch", alt="Current and scenario sales and gross profit for the selected product",
    )
    st.info(
        f"At this scenario price, approximately {break_even_units:,.0f} units would be needed to match current gross profit. "
        "The model holds unit volume and costs constant, so it does not account for customer demand changes.",
        icon=":material/science:",
    )

else:
    st.subheader("Data quality & lineage")
    st.caption("Basic validation checks run against the selected rows before interpreting the metrics.")
    checks = [
        ("Order IDs are unique", int(filtered.order_id.duplicated().sum()), "Duplicate order identifiers"),
        ("Required fields are present", int(filtered[["order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "region"]].isna().any(axis=1).sum()), "Rows missing required fields"),
        ("Quantity is positive", int(filtered.quantity.le(0).sum()), "Rows with non-positive quantity"),
        ("Prices and costs are non-negative", int((filtered[["unit_price", "unit_cost", "list_unit_price"]] < 0).any(axis=1).sum()), "Rows with a negative amount"),
        ("Discount is within 0–100%", int((~filtered.discount_pct.between(0, 100)).sum()), "Rows with invalid discount"),
        ("Order dates are in dataset window", int((~filtered.order_date.dt.date.between(min_date, max_date)).sum()), "Rows outside dataset period"),
    ]
    quality = pd.DataFrame(checks, columns=["Validation", "Issue count", "Issue type"])
    quality["Result"] = quality["Issue count"].map(lambda count: "Pass" if count == 0 else "Review")
    valid_rows = (
        ~filtered.order_id.duplicated(keep=False)
        & filtered[["order_id", "order_date", "customer_id", "product_id", "quantity", "unit_price", "region"]].notna().all(axis=1)
        & filtered.quantity.gt(0)
        & filtered[["unit_price", "unit_cost", "list_unit_price"]].ge(0).all(axis=1)
        & filtered.discount_pct.between(0, 100)
        & filtered.order_date.dt.date.between(min_date, max_date)
    ).sum()
    score = (valid_rows / len(filtered) * 100) if len(filtered) else 0
    q1, q2, q3 = st.columns(3)
    q1.metric("Rows reviewed", f"{len(filtered):,}", border=True)
    q2.metric("Quality checks passed", f"{(quality.Result == 'Pass').sum()} / {len(quality)}", border=True)
    q3.metric("Completeness / validity score", f"{score:.1f}%", border=True)
    st.dataframe(quality, width="stretch", hide_index=True)
    st.markdown("**Metric definitions**")
    st.markdown(
        "- Net sales = quantity × discounted unit price\n"
        "- Gross profit = quantity × (discounted unit price − unit cost)\n"
        "- Profit margin = gross profit ÷ net sales\n"
        "- Average order value = net sales ÷ distinct orders"
    )
    st.caption("The quality score is a simple demo metric based on the listed checks; it is not an audited data-quality certification.")

st.divider()
st.caption("MarketLens · E-Commerce Sales Analytics · Synthetic data for educational demonstration")
