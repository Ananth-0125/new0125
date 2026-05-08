import os
import runpy
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR / "customer_query_analyzer"

sys.path.insert(0, str(APP_DIR))
os.chdir(APP_DIR)

runpy.run_path(str(APP_DIR / "app.py"), run_name="__main__")
