import numpy as np
import networkx as nx


def order_by_region(G):
    # order by region clusters
    order = ['M2', 'AC', 'PrL', 'IL', 'DP']

    region = nx.get_node_attributes(G, "region")

    # (node_idx, node_name, cluster)
    order_sort = sorted(zip(np.arange(0, G.number_of_nodes()), G.nodes(), region.values()),
                        key=lambda node: [order.index(node[2])])
    order_idx = [n[0] for n in order_sort]
    order_node_name = [n[1] for n in order_sort]
    order_region = [n[2] for n in order_sort]

    G = nx.to_numpy_array(G)  # transform to matrix
    G = G[:, order_idx][order_idx]  # reorder

    return G, order_idx, order_node_name, order_region
