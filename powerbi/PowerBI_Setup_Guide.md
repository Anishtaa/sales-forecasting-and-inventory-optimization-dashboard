
# Power BI Setup Guide

This guide explains how to connect the exported CSV data from the pipeline
and build a simple dashboard with a few core visuals. You can extend it
further based on your needs.

## 1. Connect to Data

1. Open **Power BI Desktop**.
2. Click **Get Data -> Text/CSV**.
3. Select `data/powerbi_dashboard_data.csv` from this project.
4. Click **Load**.

## 2. Suggested Pages

Create the following report pages:

1. **Executive Summary**
   - KPIs: Total Sales, Average Weekly Demand, Number of Critical SKUs.
   - Cards and a simple matrix by Product & Region.

2. **Sales Forecast Analysis**
   - Line chart: Weekly Sales vs Forecast (use `aggregated_weekly_sales.csv` and `sales_forecasts_12weeks.csv` if you import them).
   - Slicer: Product, Region.

3. **Inventory Management**
   - Table / Matrix with: Product, Region, Current_Stock, Reorder_Point, Stock_Status, Stockout_Risk, Recommended_Order_Qty.
   - Conditional formatting on `Stock_Status` and `Stockout_Risk`.

4. **Action & Recommendations**
   - Table filtered to `Stock_Status` = CRITICAL or LOW with Recommended_Order_Qty.
   - Use a slicer to prioritize by `Priority`.

5. **Model Performance**
   - Import `model_evaluation_metrics.csv` and show MAE, RMSE, MAPE per Product & Region.
   - Bar or clustered column chart.

## 3. Basic DAX Examples

These are simple examples you can adapt:

```DAX
Total Sales = SUM(data[Avg_Weekly_Demand])

Critical SKUs = CALCULATE(
    DISTINCTCOUNT(data[Product]),
    data[Stock_Status] = "CRITICAL"
)
```

## 4. Refresh

After you rerun `python run_pipeline.py` with updated data:

1. Overwrite `data/*.csv` files.
2. In Power BI, click **Refresh** to load the new numbers.
