"""
=================================
            2.TSNET
=================================
This module is designed to plot network properties: strength in/out and strength intra/inter
"""
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tools import load_metadata
from config import NET_DIR, PLOT_DIR, STATES, REGION_ORDER


# get metadata
metadata, subjects = load_metadata()

# add states to metadata
metadata = pd.concat([metadata] * len(STATES), ignore_index=True)
metadata["state"] = STATES * int(len(metadata) / len(STATES))

# add regions to metadata
metadata = pd.concat([metadata] * len(REGION_ORDER), ignore_index=True)
metadata["region"] = REGION_ORDER * int(len(metadata) / len(REGION_ORDER))

# Load data from Xnet for each subject and build data frame
net_list = []
subs = []
subs_state = []
for sub, sub_state in zip(
    metadata["id_mouse"], STATES * int(len(np.unique(metadata["id_mouse"])))
):
    # Load data
    file_name = NET_DIR / f"net_metric_{sub}_{sub_state}.pkl"
    with open(file_name, "rb") as pickle_file:
        Xnet = pickle.load(pickle_file)
        net_list.append(Xnet)
        subs.append(sub)
        subs_state.append(sub_state)
net_data = pd.DataFrame(net_list)
net_data = net_data.fillna(0)
net_metrics = np.unique(
    ["_".join(metric.split("_")[1:]) for metric in net_data.columns]
)
net_data["id_mouse"] = subs
net_data["state"] = subs_state

# Initialize metrics column with None values
metadata.update({metric: [None] * len(metadata) for metric in net_metrics})

# Fill metrics columns
for index, row in metadata.iterrows():
    sub = row["id_mouse"]
    state = row["state"]
    region = row["region"]
    for metric in net_metrics:
        value = net_data.loc[
            (net_data["id_mouse"] == sub) & (net_data["state"] == state),
            "_".join([region, metric]),
        ]
        # Set the new value for the 'metric' column
        metadata.loc[index, metric] = value.values[0]

# Create a boxplot using Seaborn
for state in STATES:
    for metric in net_metrics:
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=metadata[metadata["state"] == state],
            x="region",
            y=metric,
            hue="genot",
            palette="Set3",
            order=REGION_ORDER,
        )
        # sns.boxplot(data=metadata, x='region', y='strength_inter', hue='state', palette='Set3', width=0.5)

        # Add labels and legend
        plt.xlabel("")
        plt.ylabel("")
        plt.title(f"{state} {metric}", fontsize=16)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.legend(fontsize=14)
        min_limit = 0 if metadata[metric].min() > 0 else metadata[metric].min()
        plt.ylim(min_limit - 0.1, 1.1)
        nodes_file = PLOT_DIR / f"{metric}_{state}.png"
        # plt.savefig(nodes_file, dpi=300, bbox_inches='tight', transparent=True)
        plt.show()
