# MarketLens — E-Commerce Sales Analytics

MarketLens is a Streamlit analytics dashboard for exploring a fictional e-commerce business. It combines sales KPIs, customer RFM analysis, product and fulfillment views, a price sensitivity scenario, and basic data quality checks.

## Run in VS Code

Open this folder in VS Code, then run these commands in its terminal:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Dashboard views

- **Overview:** net sales, gross profit, orders, units, margin, average order value, monthly trend, category and regional contribution, and channel mix.
- **Customer intelligence:** recency, frequency, and monetary value scoring; customer groups; repeat-purchase share; customer value scatter plot.
- **Product & operations:** product sales versus margin, fulfillment status, average delivery, discount rate, and a product scorecard.
- **Scenario lab:** compare current product sales and profit with a price-change scenario, including the units needed to preserve current gross profit.
- **Data quality:** checks for duplicate order IDs, required-field gaps, invalid quantities, negative prices/costs, out-of-range discounts, and out-of-window dates.

All dashboard views use the global sidebar date, region, category, channel, and fulfillment filters. The price scenario holds sales volume and cost constant; it is a sensitivity calculation, not a forecast of customer demand. RFM groups are calculated from the filtered data and are illustrative.

## Dataset and calculations

`data/ecommerce_sales_synthetic.csv` contains 1,800 fictional orders covering 17 May through 15 November 2026. The columns include customer segment, product, category, city, region, sales channel, payment method, fulfillment status, quantity, list price, discount, selling price, unit cost, and shipping days. Regenerate the deterministic dataset with:

```powershell
python generate_data.py
```

Net sales = quantity × selling price. Gross profit = quantity × (selling price − unit cost). Average order value = net sales ÷ distinct orders. The data is synthetic and does not describe any real retailer, customer, or market. Present its trends as a demonstration of the analysis workflow, not as real-world findings.

## Scope

This project is a single-machine CSV analytics dashboard. It demonstrates interactive analysis and data-quality logic, but it does not use Hadoop, HDFS, or distributed MapReduce. The public GitHub project used as a topic reference describes a larger processing pipeline with input validation, HDFS staging, and Java MapReduce jobs for aggregation, ranking, and product joins. Describe MarketLens as a smaller independent implementation with synthetic data.
