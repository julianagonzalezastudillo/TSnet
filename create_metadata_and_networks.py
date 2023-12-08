import os.path
import pickle
import numpy as np
import pandas as pd
import networkx as nx
import os
# import matplotlib.pyplot as plt


def build_matrix(df_edges, n):
    matrix = np.zeros((n, n), dtype=float)  # matrix (n,n)
    for i, j, w in df_edges[['pre', 'post', 'sp_trans_p']].values:
        matrix[int(i)][int(j)] = w
    return matrix


def df_to_array(df_edges, nodes):
    n = np.max(nodes) + 1
    matrix = build_matrix(df_edges, n)
    n_zero = np.where(~matrix.any(axis=1))[0]
    contained = [n in nodes for n in n_zero]
    n_zero = n_zero[~np.array(contained)]
    matrix = np.delete(matrix, n_zero, axis=0)
    matrix = np.delete(matrix, n_zero, axis=1)
    return matrix


path = r'C:\Users\javier.zorrilla\ownCloud\Labo\Experiments\Networks\\'

fc_path = path #+ 'fc_matrix\\'

# build/complete metadata
metadata = pd.read_csv(path + 'Ts65Dn_npx_a5IA_metadata.csv')
metadata_ = pd.DataFrame()
metadata_['id_mouse'] = metadata['id_mouse']
metadata_['genot'] = metadata['genot']
states = ['ctr', 'a5ia']

num_nodes = []
for sub in metadata['id_mouse']:
    edges_file = fc_path + '{0}_edges.csv'.format(sub)
    nodes_file = fc_path + '{0}_node_attributes.csv'.format(sub)

    edges = pd.read_csv(edges_file)
    edges = edges.drop(edges.columns[1], axis = 1)

    # nodes to keep that at least have one connection in one of the states
    keep_nodes = np.sort(np.unique([edges['pre'], edges['post']]))
    num_nodes = np.append(num_nodes, len(keep_nodes))

    for sub_state in states:
        edges_state = edges[edges['treatment'] == sub_state]
        G_ = df_to_array(edges_state, keep_nodes)  # create array from csv

        # convert to networkx graph object
        G = nx.from_numpy_array(G_, create_using = nx.DiGraph)
        mapping = dict(zip(G, keep_nodes))
        G = nx.relabel_nodes(G, mapping)

        # nodes info
        nodes_region = pd.read_csv(nodes_file)
        nodes_region = nodes_region.drop(nodes_region.columns[0], axis=1)
        nodes_region = nodes_region[nodes_region['node_id'].isin(keep_nodes)]  # select keep_nodes

        # add node attributes
        region = nodes_region.set_index('node_id')['region'].to_dict()
        nx.set_node_attributes(G, region, "region")

        # save graph object to file
        net_file = fc_path + '{0}_{1}_net'.format(sub, sub_state)
        pickle.dump(G, open('{0}.pickle'.format(net_file), 'wb'))

metadata_['num_nodes'] = num_nodes

# save completed metadata
metadata_.to_csv(path + 'Ts65Dn_npx_a5IA_metadata_updated.csv', index=False)

# to check with plot
# import matplotlib.pyplot as plt
# fig = plt.figure(figsize = (5, 5), dpi = 600)
# ax = plt.subplot()
# im = ax.imshow(G_)
# fig.suptitle(sub)
# plt.show()

# fig = plt.figure(figsize = (5, 5), dpi = 600)
# ax = plt.subplot()
# im = ax.imshow(nx.to_numpy_array(G))
# fig.suptitle(sub)
# plt.show()
