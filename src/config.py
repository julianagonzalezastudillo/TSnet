"""
=================================
            TSNET
=================================
Configuration file with path, file names and constant values.
"""
import os.path
from pathlib import Path

# File paths or directories
DATA_DIR = Path(os.getcwd(), *["../data"])

RES_DIR = Path(os.getcwd(), *["../results"])
RES_DIR.mkdir(parents=True, exist_ok=True)

# FC_DIR = "fc_matrix"  # net_path
FC_DIR = RES_DIR / "fc_matrix"
FC_DIR.mkdir(parents=True, exist_ok=True)

NET_DIR = RES_DIR / "net_metric"
NET_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path(os.getcwd(), *["../plots"])
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Constants
STATES = ["ctr", "a5ia"]
GENOT = ["eu", "ts"]
REGION_ORDER = ["M2", "AC", "PrL", "IL", "DP"]
MODULS_ORDER = ["-1", "0", "1"]
BINARIZE = True

# Define type of clusters (regions or moduls)
ATTRIBUTE = "moduls"  # "moduls" or "region"

# Files
METADATA = DATA_DIR / "info/Ts65Dn_npx_a5IA_metadata.csv"
