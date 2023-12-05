"""
=================================
            2.TSNET
=================================
This module is designed to plot network properties: strength in/out and strength intra/inter
"""

import matplotlib.pyplot as plt
import seaborn as sns

from config import PLOT_DIR, GENOT, REGION_ORDER, BINARIZE
from tools import load_net_metrics

# get netdata
netdata, net_metrics = load_net_metrics()

# Create a boxplot using Seaborn
for genot in GENOT:
    for metric in net_metrics:
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=netdata[netdata["genot"] == genot],
            x="region",
            y=metric,
            hue="state",
            palette="Set1",
            order=REGION_ORDER,
        )
        # sns.boxplot(data=metadata, x='region', y='strength_inter', hue='state', palette='Set3', width=0.5)

        # Add labels and legend
        plt.xlabel("")
        plt.ylabel("")
        plt.title(f"{genot} {metric}", fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)

        if not BINARIZE:
            min_limit = 0 if netdata[metric].min() > 0 else netdata[metric].min()
            plt.ylim(min_limit - 0.1, 1.1)
        nodes_file = PLOT_DIR / f"{metric}_{genot}.png"
        plt.savefig(nodes_file, dpi=300, bbox_inches="tight", transparent=True)
        plt.show()
