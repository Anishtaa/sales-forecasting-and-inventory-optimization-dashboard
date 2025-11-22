
import os
import json
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODELS_DIR, exist_ok=True)

FORECAST_HORIZON_WEEKS = 12

def mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    if non_zero.sum() == 0:
        return np.nan
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100

def train_and_forecast(group_key, df_group):
    product, region = group_key
    df = df_group.copy()
    df = df.sort_values("WeekStartDate")
    df_prophet = df.rename(columns={
        "WeekStartDate": "ds",
        "Weekly_Sales": "y"
    })[["ds", "y"]]

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode="additive"
    )
    model.fit(df_prophet)

    future = model.make_future_dataframe(periods=FORECAST_HORIZON_WEEKS, freq="W-MON")
    forecast = model.predict(future)

    # Metrics on history
    hist = forecast.iloc[:len(df_prophet)]
    mae = mean_absolute_error(df_prophet["y"], hist["yhat"])
    mse = mean_squared_error(df_prophet["y"], hist["yhat"])
    rmse = mse ** 0.5
    mape_val = mape(df_prophet["y"], hist["yhat"])

    # Save model
    model_path = os.path.join(MODELS_DIR, f"prophet_model_{product}_{region}.pkl")
    import joblib
    joblib.dump(model, model_path)

    # Prepare forecast output
    fc = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    fc["Product"] = product
    fc["Region"] = region

    metrics = {
        "Product": product,
        "Region": region,
        "MAE": mae,
        "RMSE": rmse,
        "MAPE": mape_val
    }
    return fc, metrics

def main():
    weekly_path = os.path.join(DATA_DIR, "aggregated_weekly_sales.csv")
    if not os.path.exists(weekly_path):
        raise FileNotFoundError(f"Weekly data not found at {weekly_path}. Run 01_data_preprocessing.py first.")

    df = pd.read_csv(weekly_path, parse_dates=["WeekStartDate"])

    all_forecasts = []
    all_metrics = []

    for group_key, df_group in df.groupby(["Product", "Region"]):
        print(f"Training Prophet model for {group_key}...")
        fc, metrics = train_and_forecast(group_key, df_group)
        all_forecasts.append(fc)
        all_metrics.append(metrics)

    forecast_df = pd.concat(all_forecasts, ignore_index=True)
    metrics_df = pd.DataFrame(all_metrics)

    forecast_out = os.path.join(DATA_DIR, "sales_forecasts_12weeks.csv")
    metrics_out_csv = os.path.join(DATA_DIR, "model_evaluation_metrics.csv")
    metrics_out_json = os.path.join(DATA_DIR, "model_metrics.json")

    forecast_df.to_csv(forecast_out, index=False)
    metrics_df.to_csv(metrics_out_csv, index=False)
    metrics_df.to_json(metrics_out_json, orient="records", indent=2)

    print(f"Saved forecasts to {forecast_out}")
    print(f"Saved metrics to {metrics_out_csv} and {metrics_out_json}")

if __name__ == "__main__":
    main()
