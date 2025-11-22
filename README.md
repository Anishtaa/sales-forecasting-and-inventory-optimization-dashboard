
# Sales Forecasting and Inventory Dashboard

This project provides an end-to-end pipeline for:
- Cleaning and enriching historical sales data
- Training Prophet time series models per product & region
- Generating 12-week sales forecasts
- Computing inventory KPIs and recommendations
- Exporting a clean dataset for Power BI dashboards

## Project Structure

- `data/`
  - `historical_sales_data.csv` — sample synthetic dataset (2 years, 5 products, 3 regions)
  - Pipeline output files (processed data, weekly aggregation, forecasts, inventory plan)
- `scripts/`
  - `01_data_preprocessing.py`
  - `02_prophet_forecasting.py`
  - `03_inventory_optimization.py`
- `run_pipeline.py` — orchestrates the full workflow
- `powerbi/PowerBI_Setup_Guide.md` — instructions to build the dashboard
- `requirements.txt` — Python dependencies

## Quick Start

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

# Run the full pipeline
python run_pipeline.py
```

Outputs will be written to the `data/` folder:

- `processed_sales_data.csv`
- `aggregated_weekly_sales.csv`
- `sales_forecasts_12weeks.csv`
- `model_evaluation_metrics.csv`
- `model_metrics.json`
- `inventory_recommendations.csv`
- `powerbi_dashboard_data.csv`

## Power BI

1. Open Power BI Desktop.
2. Load `data/powerbi_dashboard_data.csv` as a dataset.
3. Follow `powerbi/PowerBI_Setup_Guide.md` to create pages and visuals.
