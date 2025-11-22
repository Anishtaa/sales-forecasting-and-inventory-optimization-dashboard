
import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class SalesPreprocessor:
    def __init__(self, input_file: str):
        self.input_path = os.path.join(DATA_DIR, input_file)
        self.df = None
        self.df_clean = None
        self.weekly_df = None

    def load_data(self):
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Input file not found: {self.input_path}")
        self.df = pd.read_csv(self.input_path)
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df.sort_values(["Product", "Region", "Date"], inplace=True)

    def clean_data(self):
        df = self.df.copy()
        # Basic cleaning
        df = df.dropna(subset=["Date", "Product", "Region", "Quantity_Sold"])
        df["Quantity_Sold"] = df["Quantity_Sold"].clip(lower=0)
        if "Stock_Level" in df.columns:
            df["Stock_Level"] = df["Stock_Level"].clip(lower=0)

        # Remove obvious outliers using IQR on quantity
        def remove_outliers(group):
            q1 = group["Quantity_Sold"].quantile(0.25)
            q3 = group["Quantity_Sold"].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            return group[(group["Quantity_Sold"] >= lower) & (group["Quantity_Sold"] <= upper)]

        df = df.groupby(["Product", "Region"], group_keys=False).apply(remove_outliers)
        self.df_clean = df.reset_index(drop=True)

    def add_time_features(self):
        df = self.df_clean
        df["day_of_week"] = df["Date"].dt.dayofweek
        df["week_of_year"] = df["Date"].dt.isocalendar().week.astype(int)
        df["month"] = df["Date"].dt.month
        df["year"] = df["Date"].dt.year
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # Cyclical encoding
        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        # Lag features per product-region
        df = df.sort_values(["Product", "Region", "Date"])
        for lag in [1, 7, 30]:
            df[f"lag_{lag}"] = df.groupby(["Product", "Region"])["Quantity_Sold"].shift(lag)

        # Rolling stats
        for window in [7, 30]:
            df[f"roll_mean_{window}"] = (
                df.groupby(["Product", "Region"])["Quantity_Sold"]
                  .rolling(window, min_periods=3)
                  .mean()
                  .reset_index(level=[0, 1], drop=True)
            )
            df[f"roll_std_{window}"] = (
                df.groupby(["Product", "Region"])["Quantity_Sold"]
                  .rolling(window, min_periods=3)
                  .std()
                  .reset_index(level=[0, 1], drop=True)
            )
        self.df_clean = df

    def aggregate_weekly(self):
        df = self.df_clean.copy()
        df["WeekStartDate"] = df["Date"] - pd.to_timedelta(df["Date"].dt.dayofweek, unit="D")
        weekly = (
            df.groupby(["Product", "Region", "WeekStartDate"], as_index=False)
            .agg({
                "Quantity_Sold": "sum",
                "Stock_Level": "last",
                "roll_mean_7": "mean",
                "roll_std_7": "mean",
                "roll_mean_30": "mean",
                "roll_std_30": "mean"
            })
            .rename(columns={"Quantity_Sold": "Weekly_Sales"})
        )
        self.weekly_df = weekly

    def save_outputs(self):
        processed_path = os.path.join(DATA_DIR, "processed_sales_data.csv")
        weekly_path = os.path.join(DATA_DIR, "aggregated_weekly_sales.csv")
        self.df_clean.to_csv(processed_path, index=False)
        self.weekly_df.to_csv(weekly_path, index=False)
        print(f"Saved processed data to {processed_path}")
        print(f"Saved weekly aggregated data to {weekly_path}")

def main():
    preprocessor = SalesPreprocessor(input_file="historical_sales_data.csv")
    preprocessor.load_data()
    preprocessor.clean_data()
    preprocessor.add_time_features()
    preprocessor.aggregate_weekly()
    preprocessor.save_outputs()

if __name__ == "__main__":
    main()
