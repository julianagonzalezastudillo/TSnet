import os.path
import pickle
import numpy as np
import pandas as pd
import networkx as nx


path = '/Users/juliana.gonzalez/ownCloud/Juli-Javi/'
fc_path = path + 'fc_matrix/'

# build/complete metadata
metadata = pd.read_csv(path + 'Ts65Dn_npx_a5IA_metadata.csv')

G_ctr_min = []
G_ctr_max = []
G_a5ia_min = []
G_a5ia_max = []
num_nodes = []
for sub in metadata['id_mouse']:
    edges_file = fc_path + '{0}_edges.csv'.format(sub)
    nodes_file = fc_path + '{0}_node_attributes.csv'.format(sub)

    edges = pd.read_csv(edges_file)
    edges = edges.drop(edges.columns[1], axis = 1)
    edges = edges.rename(columns = {"pre": "source", "post": "target", "sp_trans_p": "weight"})

    G_ctr = nx.from_pandas_edgelist(edges[edges['treatment'] == 'ctr'], edge_attr=True, create_using = nx.DiGraph())
    G_a5ia = nx.from_pandas_edgelist(edges[edges['treatment'] == 'a5ia'], edge_attr=True,  create_using = nx.DiGraph())

    # nodes info
    nodes = pd.read_csv(nodes_file)
    nodes = nodes.drop(nodes.columns[0], axis=1)
    # nodes = nodes.set_index('node_id').T.to_dict('tight')

    # add node attributes
    region = nodes.set_index('node_id')['region'].to_dict()
    nx.set_node_attributes(G_ctr, region, "region")
    nx.set_node_attributes(G_a5ia, region, "region")

    # save graph object to file
    net_file_ctr = fc_path + '{0}_ctr_net'.format(sub)
    pickle.dump(G_ctr, open('{0}.pickle'.format(net_file_ctr), 'wb'))
    net_file_a5ia = fc_path + '{0}_a5ia_net'.format(sub)
    pickle.dump(G_a5ia, open('{0}.pickle'.format(net_file_a5ia), 'wb'))

    G_ctr = nx.to_numpy_array(G_ctr)
    G_a5ia = nx.to_numpy_array(G_a5ia)

    # get max, min and number of nodes
    G_ctr_min = np.append(G_ctr_min, np.min(G_ctr))
    G_ctr_max = np.append(G_ctr_max, np.max(G_ctr))
    G_a5ia_min = np.append(G_a5ia_min, np.min(G_a5ia))
    G_a5ia_max = np.append(G_a5ia_max, np.max(G_a5ia))

    num_nodes = np.append(num_nodes, np.shape(G_ctr)[0])

metadata_ = pd.DataFrame()
metadata_['id_mouse'] = metadata['id_mouse']
metadata_['genot'] = metadata['genot']
metadata_['G_ctr_min'] = G_ctr_min
metadata_['G_ctr_max'] = G_ctr_max
metadata_['G_a5ia_min'] = G_a5ia_min
metadata_['G_a5ia_max'] = G_a5ia_max
metadata_['num_nodes'] = num_nodes

# save completed metadata
metadata_.to_csv(path + 'Ts65Dn_npx_a5IA_metadata_updated.csv', index=False)

