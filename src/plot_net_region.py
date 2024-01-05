"""
=================================
            2.1.TSNET
=================================
This module is designed to plot network properties: strength in/out and strength intra/inter
"""

import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    PLOT_DIR,
    GENOT,
    STATES,
    REGION_ORDER,
    MODULS_ORDER,
    ATTRIBUTE,
    BINARIZE,
)
from tools import load_net_metrics

# Use a dictionary to map ATTRIBUTE to its corresponding order
ATT_ORDER = {"region": REGION_ORDER, "moduls": MODULS_ORDER}[ATTRIBUTE]
binarize = "bin" if BINARIZE else "nonbin"
palette = {"state": "Set1", "genot": "Set2"}

# get netdata
netdata, net_metrics = load_net_metrics(
    scale="local", binarize=binarize, attribute=ATTRIBUTE
)

# Create a boxplot using Seaborn
genot_state = {"genot": GENOT, "state": STATES}
for key, values in genot_state.items():
    for value in values:
        for metric in net_metrics:
            plt.figure(figsize=(10, 6))
            hue = "state" if key == "genot" else "genot"
            sns.boxplot(
                data=netdata[netdata[key] == value],
                x=ATTRIBUTE,
                y=metric,
                hue=hue,
                palette=palette[key],
                order=ATT_ORDER,
            )
            # sns.boxplot(data=metadata, x='region', y='strength_inter', hue='state', palette='Set3', width=0.5)

            # Add labels and legend
            plt.xlabel("")
            plt.ylabel("")
            plt.title(f"{binarize} {value} {metric}", fontsize=16)
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            plt.legend(fontsize=14)

            if not BINARIZE:
                min_limit = 0 if netdata[metric].min() > 0 else netdata[metric].min()
                plt.ylim(min_limit - 0.1, 1.1)
            plot_file = PLOT_DIR / f"{ATTRIBUTE}_{value}_{binarize}_{metric}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches="tight", transparent=False)
            # plt.show()
