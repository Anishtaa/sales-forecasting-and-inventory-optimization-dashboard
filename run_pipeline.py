
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

STEPS = [
    ("Data preprocessing", os.path.join(SCRIPTS_DIR, "01_data_preprocessing.py")),
    ("Prophet forecasting", os.path.join(SCRIPTS_DIR, "02_prophet_forecasting.py")),
    ("Inventory optimization", os.path.join(SCRIPTS_DIR, "03_inventory_optimization.py")),
]

def run_step(name, script_path):
    print(f"\n=== Step: {name} ===")
    if not os.path.exists(script_path):
        raise FileNotFoundError(f"Script not found: {script_path}")
    result = subprocess.run([sys.executable, script_path], cwd=BASE_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"Step '{name}' failed with exit code {result.returncode}")
    print(f"Completed: {name}")

def main():
    print("Starting Sales Forecasting & Inventory Optimization pipeline...")
    for name, script in STEPS:
        run_step(name, script)
    print("\nPipeline completed successfully. Check the 'data' folder for outputs.")

if __name__ == "__main__":
    main()
