"""
=================================
            1.TSNET
=================================
This module is designed to transform data from .csv into networks.
"""

import pickle

import networkx as nx
import numpy as np
import pandas as pd

from config import FC_DIR, METADATA, STATES, BINARIZE


def build_matrix(df_edges, n):
    matrix = np.zeros((n, n), dtype=float)  # matrix (n,n)
    for i, j, w in df_edges[["pre.1", "post", "sp_trans_p"]].values:
        if BINARIZE:
            matrix[int(i)][int(j)] = 1
        else:
            matrix[int(i)][int(j)] = w
    return matrix


def df_to_array(df_edges, nodes):
    n = np.max(nodes) + 1
    matrix = build_matrix(df_edges, n)

    # Find rows with all elements equal zero
    n_zero = np.where(~matrix.any(axis=1))[0]

    # Check not to delete non-zero nodes in other state (ctr/a5ia)
    contained = [n in nodes for n in n_zero]
    n_zero = n_zero[~np.array(contained)]

    # Delete zero rows and columns
    matrix = np.delete(matrix, n_zero, axis=0)
    matrix = np.delete(matrix, n_zero, axis=1)
    return matrix


# build/complete metadata
metadata = pd.read_csv(METADATA)

num_nodes = []
for sub in metadata["id_mouse"]:
    # Load subject edges
    edges_file = FC_DIR / f"{sub}_edges.csv"
    nodes_file = FC_DIR / f"{sub}_node_attributes.csv"

    edges = pd.read_csv(edges_file)
    edges = edges.drop(edges.columns[1], axis=1)

    # nodes to keep that at least have one connection in one of the states
    keep_nodes = np.sort(np.unique([edges["pre.1"], edges["post"]]))

    num_nodes = np.append(num_nodes, len(keep_nodes))

    for sub_state in STATES:
        edges_state = edges[edges["treatment"] == sub_state]
        G_ = df_to_array(edges_state, keep_nodes)  # create array from csv

        # convert to networkx graph object
        G = nx.from_numpy_array(G_, create_using=nx.DiGraph)
        mapping = dict(zip(G, keep_nodes))
        G = nx.relabel_nodes(G, mapping)

        # Load node attributes
        nodes_attributes = pd.read_csv(nodes_file)

        # Add node attributes: regions and mode
        region = nodes_attributes.set_index("node_id")["region"].to_dict()
        nx.set_node_attributes(G, region, "region")
        mode = nodes_attributes.set_index("node_id")["mode"].to_dict()
        nx.set_node_attributes(G, region, "mode")

        # save graph object to file
        net_file = FC_DIR / f"{sub}_{sub_state}_net"
        print(net_file)
        pickle.dump(G, open(f"{net_file}.pickle", "wb"))

metadata["num_nodes"] = num_nodes

# save completed metadata
metadata.to_csv(METADATA, index=False)

# to check with plot (not organized data)
import matplotlib.pyplot as plt

fig = plt.figure(figsize=(5, 5), dpi=600)
ax = plt.subplot()
im = ax.imshow(G_)
fig.suptitle(sub)
plt.show()

fig = plt.figure(figsize=(5, 5), dpi=600)
ax = plt.subplot()
im = ax.imshow(nx.to_numpy_array(G))
fig.suptitle(sub)
plt.show()
