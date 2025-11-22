
import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

class InventoryOptimizer:
    def __init__(self, safety_stock_multiplier: float = 1.5, lead_time_weeks: int = 2):
        self.safety_stock_multiplier = safety_stock_multiplier
        self.lead_time_weeks = lead_time_weeks

    def load_data(self):
        weekly_path = os.path.join(DATA_DIR, "aggregated_weekly_sales.csv")
        forecast_path = os.path.join(DATA_DIR, "sales_forecasts_12weeks.csv")

        if not os.path.exists(weekly_path):
            raise FileNotFoundError("aggregated_weekly_sales.csv not found. Run preprocessing first.")
        if not os.path.exists(forecast_path):
            raise FileNotFoundError("sales_forecasts_12weeks.csv not found. Run forecasting first.")

        self.weekly_df = pd.read_csv(weekly_path, parse_dates=["WeekStartDate"])
        self.forecast_df = pd.read_csv(forecast_path, parse_dates=["ds"])

    def compute_inventory_plan(self):
        # Historical demand stats
        hist_stats = (
            self.weekly_df.groupby(["Product", "Region"])
            .agg(
                avg_weekly_demand=("Weekly_Sales", "mean"),
                std_weekly_demand=("Weekly_Sales", "std"),
                current_stock=("Stock_Level", "last"),
            )
            .reset_index()
        )

        hist_stats["std_weekly_demand"].fillna(0, inplace=True)

        # Lead time demand
        hist_stats["lead_time_demand"] = hist_stats["avg_weekly_demand"] * self.lead_time_weeks

        # Safety stock based on demand variability
        hist_stats["safety_stock"] = (
            self.safety_stock_multiplier
            * hist_stats["std_weekly_demand"]
            * np.sqrt(self.lead_time_weeks)
        )

        # Reorder point
        hist_stats["reorder_point"] = hist_stats["lead_time_demand"] + hist_stats["safety_stock"]

        # Classify stock status
        def classify_status(row):
            stock = row["current_stock"]
            safety = row["safety_stock"]
            reorder = row["reorder_point"]
            if stock < safety:
                return "CRITICAL"
            elif stock < reorder:
                return "LOW"
            elif stock > reorder * 1.5:
                return "EXCESS"
            else:
                return "OPTIMAL"

        hist_stats["Stock_Status"] = hist_stats.apply(classify_status, axis=1)

        # Stockout risk
        def risk_level(status):
            if status == "CRITICAL":
                return "HIGH"
            elif status == "LOW":
                return "MEDIUM"
            else:
                return "LOW"

        hist_stats["Stockout_Risk"] = hist_stats["Stock_Status"].apply(risk_level)

        # Recommended order quantity using a simple EOQ-like heuristic
        # Here EOQ is approximated as 2 * lead_time_demand when stock is below reorder point
        def recommended_order(row):
            if row["Stock_Status"] in ["CRITICAL", "LOW"]:
                target_stock = row["reorder_point"] + row["lead_time_demand"]
                return max(0, target_stock - row["current_stock"])
            return 0

        hist_stats["Recommended_Order_Qty"] = hist_stats.apply(recommended_order, axis=1)

        # Priority
        priority_map = {"CRITICAL": 1, "LOW": 2, "OPTIMAL": 3, "EXCESS": 4}
        hist_stats["Priority"] = hist_stats["Stock_Status"].map(priority_map)

        # Rename columns for clarity
        hist_stats = hist_stats.rename(columns={
            "avg_weekly_demand": "Avg_Weekly_Demand",
            "std_weekly_demand": "Std_Weekly_Demand",
            "current_stock": "Current_Stock"
        })

        self.inventory_plan = hist_stats

    def save_outputs(self):
        inv_out = os.path.join(DATA_DIR, "inventory_recommendations.csv")

        # Power BI dataset
        powerbi_df = self.inventory_plan.copy()
        powerbi_out = os.path.join(DATA_DIR, "powerbi_dashboard_data.csv")

        self.inventory_plan.to_csv(inv_out, index=False)
        powerbi_df.to_csv(powerbi_out, index=False)

        print(f"Saved inventory recommendations to {inv_out}")
        print(f"Saved Power BI dataset to {powerbi_out}")

def main():
    optimizer = InventoryOptimizer(safety_stock_multiplier=1.5, lead_time_weeks=2)
    optimizer.load_data()
    optimizer.compute_inventory_plan()
    optimizer.save_outputs()

if __name__ == "__main__":
    main()
