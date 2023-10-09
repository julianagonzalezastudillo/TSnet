import numpy as np
import networkx as nx


def order_by_region(G):
    # order by region clusters
    order = ['M2', 'AC', 'PrL', 'IL', 'DP']

    region = nx.get_node_attributes(G, "region")
    order_sort = sorted(zip(np.arange(0, G.number_of_nodes()), G.nodes(), region.values()),
                        key=lambda node: [order.index(node[2])])
    order_by_region = [n[0] for n in order_sort]

    G = nx.to_numpy_array(G)  # transform to matrix
    G = G[:, order_by_region][order_by_region]  # reorder
    return G