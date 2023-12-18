"""
=================================
            TSNET
=================================
Configuration file with path, file names and constant values.
"""
import os.path
from pathlib import Path

# File paths or directories
DATA_DIR = Path("/Users/juliana.gonzalez/ownCloud/Juli-Javi/")

# FC_DIR = "fc_matrix"  # net_path
FC_DIR = Path(os.getcwd(), *["../data"])

NET_DIR = DATA_DIR / "net_metric"  # net_path
NET_DIR.mkdir(parents=True, exist_ok=True)

PLOT_DIR = Path(os.getcwd(), *["../plots"])
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# Constants
STATES = ["ctr", "a5ia"]
GENOT = ["eu", "ts"]
REGION_ORDER = ["M2", "AC", "PrL", "IL", "DP"]
MODULS_ORDER = [-1, 0, 1]
BINARIZE = True

# Define type of clusters (regions or moduls)
ATTRIBUTE = "region"

# Files
METADATA = DATA_DIR / "Ts65Dn_npx_a5IA_metadata.csv"
