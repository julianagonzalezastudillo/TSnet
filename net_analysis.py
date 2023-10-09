import os.path
import pickle
import numpy as np
import pandas as pd
from tools import order_by_region


path = "/Users/juliana.gonzalez/ownCloud/Juli-Javi/"
fc_path = os.path.join(path, "fc_matrix")
net_path = os.path.join(path, "net_metric")

# get metadata
metadata = pd.read_csv(path + "Ts65Dn_npx_a5IA_metadata_updated.csv")
genot = metadata["genot"].unique()
subjects = {genot[0]: list(metadata.loc[metadata["genot"] == genot[0], "id_mouse"]),
            genot[1]: list(metadata.loc[metadata["genot"] == genot[1], "id_mouse"])}

states = ["ctr", "a5ia"]

for sub_type in subjects.keys():
    for sub_state in states:
        for sub in subjects[sub_type]:
            # load graph object from file
            net_file = os.path.join(fc_path, f"{sub}_{sub_state}_net")
            G = pickle.load(open("{0}.pickle".format(net_file), "rb"))

            # network metrics
            Xnet = {}
            strength_in = np.array([v for k, v in G.in_degree(weight="weight")])
            strength_out = np.array([v for k, v in G.out_degree(weight="weight")])
            strength_out_in_balance = (strength_out - strength_in) / (strength_out + strength_in)

            # Add to net metrics dict
            Xnet["strength_in"] = strength_in
            Xnet["strength_out"] = strength_out
            Xnet["strength_out_in_balance"] = strength_out_in_balance

            # Per module ["M2", "AC", "PrL", "IL", "DP"]
            X, order_idx, order_node_name, order_region = order_by_region(G)
            for region in np.unique(order_region):
                idx_intra = [idx for idx, r in zip(order_idx, order_region) if r == region]
                idx_inter = [idx for idx, r in zip(order_idx, order_region) if r not in region]

                strength_intra = np.sum(X[idx_intra][:, idx_intra])
                strength_inter = np.sum(X[idx_intra][:, idx_inter])

                strength_inter_intra_balance = (strength_inter - strength_intra) / (strength_inter + strength_intra)

                # Add to net metrics dict
                Xnet[f"{region}_strength_intra"] = strength_intra
                Xnet[f"{region}_strength_inter"] = strength_inter
                Xnet[f"{region}_strength_balance"] = strength_inter_intra_balance
            
            # Save the dictionary to a pickle file
            file_name = os.path.join(net_path, f"net_metric_{sub}_{sub_state}.pkl")
            with open(file_name, "wb") as pickle_file:
                pickle.dump(Xnet, pickle_file)

