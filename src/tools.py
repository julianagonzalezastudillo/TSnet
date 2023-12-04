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


def load_net_metrics():
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

    # Get net metrics names for regions analysis
    net_data = pd.DataFrame(net_list)
    net_data = net_data.fillna(0)
    filtered_columns = [
        col for col in net_data.columns if col.startswith(tuple(REGION_ORDER))
    ]
    net_metrics = np.unique(
        ["_".join(metric.split("_")[1:]) for metric in filtered_columns]
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

    return metadata
