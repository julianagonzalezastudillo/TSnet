"""
=================================
            TSNET
=================================
This module is design to load data.
"""
import pickle

import networkx as nx
import numpy as np
import pandas as pd

from config import NET_DIR, METADATA, REGION_ORDER, STATES


# Function to load data
def load_metadata():
    metadata = pd.read_csv(METADATA)
    genot = metadata["genot"].unique()
    subjects = {
        genot[0]: list(metadata.loc[metadata["genot"] == genot[0], "id_mouse"]),
        genot[1]: list(metadata.loc[metadata["genot"] == genot[1], "id_mouse"]),
    }
    return metadata, subjects


def order_by_region(G):
    # order by region clusters
    order = ["M2", "AC", "PrL", "IL", "DP"]

    region = nx.get_node_attributes(G, "region")

    # (node_idx, node_name, cluster)
    order_sort = sorted(
        zip(np.arange(0, G.number_of_nodes()), G.nodes(), region.values()),
        key=lambda node: [order.index(node[2])],
    )
    order_idx = [n[0] for n in order_sort]
    order_node_name = [n[1] for n in order_sort]
    order_region = [n[2] for n in order_sort]

    G = nx.to_numpy_array(G)  # transform to matrix
    G = G[:, order_idx][order_idx]  # reorder

    return G, order_idx, order_node_name, order_region


def load_net_metrics(scale="local"):
    """
    Load local metrics computed in net_analysis.py and rearrange them in a dataframe
    :return:
        netdata: dataframe with metadata + local network metrics.
        net_metrics: network metrics names.
    """
    scale = "local"
    # get metadata
    netdata, subjects = load_metadata()

    # add states to netdata
    netdata = pd.concat([netdata] * len(STATES), ignore_index=True)
    netdata["state"] = STATES * int(len(netdata) / len(STATES))

    # add regions to netdata
    if scale == "local":
        netdata = pd.concat([netdata] * len(REGION_ORDER), ignore_index=True)
        netdata["region"] = REGION_ORDER * int(len(netdata) / len(REGION_ORDER))

    # Load data from Xnet for each subject and build data frame
    net_list = []
    subs = []
    subs_state = []
    for sub, sub_state in zip(
        netdata["id_mouse"], STATES * int(len(np.unique(netdata["id_mouse"])))
    ):
        # Load data
        file_name = NET_DIR / f"net_metric_{sub}_{sub_state}.pkl"
        with open(file_name, "rb") as pickle_file:
            Xnet = pickle.load(pickle_file)
            net_list.append(Xnet)
            subs.append(sub)
            subs_state.append(sub_state)

    # Get net metrics names for regions analysis
    net_data = pd.DataFrame(net_list).fillna(0)

    if scale == "local":
        filtered_columns = net_data.columns[
            net_data.columns.str.startswith(tuple(REGION_ORDER))
        ]
        net_metrics = np.unique(
            ["_".join(metric.split("_")[1:]) for metric in filtered_columns]
        )
    elif scale == "global":
        net_metrics = np.array(
            net_data.columns[~net_data.columns.str.startswith(tuple(REGION_ORDER))]
        )

    net_data["id_mouse"] = subs
    net_data["state"] = subs_state

    # Initialize metrics column with None values
    netdata.update({metric: [None] * len(netdata) for metric in net_metrics})

    # Fill metrics columns
    for index, row in netdata.iterrows():
        for metric in net_metrics:
            if scale == "local":
                value = net_data.loc[
                    (net_data["id_mouse"] == row["id_mouse"])
                    & (net_data["state"] == row["state"]),
                    "_".join([row["region"], metric]),
                ]
            else:
                value = net_data.loc[
                    (net_data["id_mouse"] == row["id_mouse"])
                    & (net_data["state"] == row["state"]),
                    metric,
                ]
            # Set the new value for the 'metric' column
            netdata.loc[index, metric] = value.values[0]

    return netdata, net_metrics
