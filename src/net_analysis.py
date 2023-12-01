"""
=================================
            2.TSNET
=================================
This module is designed to extract network properties from FC matrices: strength in/out and strength intra/inter
"""
import pickle

import numpy as np

from config import FC_DIR, NET_DIR, STATES
from tools import load_metadata, order_by_region

# get metadata
metadata, subjects = load_metadata()

for sub_type in subjects.keys():
    for sub_state in STATES:
        for sub in subjects[sub_type]:
            # load graph object from file
            net_file = FC_DIR / f"{sub}_{sub_state}_net"
            G = pickle.load(open(f"{net_file}.pickle", "rb"))

            # Per module ["M2", "AC", "PrL", "IL", "DP"]
            Xnet = {}
            X, order_idx, order_node_name, order_region = order_by_region(G)
            for region in np.unique(order_region):
                # strength intra and inter clusters
                idx_intra = [
                    idx for idx, r in zip(order_idx, order_region) if r == region
                ]
                idx_inter = [
                    idx for idx, r in zip(order_idx, order_region) if r not in region
                ]

                # strength in and out regions
                strength_in = np.sum(
                    X[idx_inter][:, idx_intra]  # in_degree = column sum of X by regions
                )
                strength_out = np.sum(
                    X[idx_intra][:, idx_inter]  # out_degree = row sum of X by regions
                )
                strength_out_in_balance = (strength_out - strength_in) / (
                    strength_out + strength_in
                )

                # strength intra and inter regions
                strength_intra = np.sum(X[idx_intra][:, idx_intra])
                strength_inter = strength_in + strength_out
                strength_inter_intra_balance = (strength_inter - strength_intra) / (
                    strength_inter + strength_intra
                )

                # Add to net metrics dict
                Xnet[f"{region}_strength_intra"] = np.nan_to_num(
                    strength_intra, nan=0.0
                )
                Xnet[f"{region}_strength_inter"] = np.nan_to_num(
                    strength_inter, nan=0.0
                )
                Xnet[f"{region}_strength_inter_intra_balance"] = np.nan_to_num(
                    strength_inter_intra_balance, nan=0.0
                )
                Xnet[f"{region}_strength_in"] = np.nan_to_num(strength_in, nan=0.0)
                Xnet[f"{region}_strength_out"] = np.nan_to_num(strength_out, nan=0.0)
                Xnet[f"{region}_strength_out_in_balance"] = np.nan_to_num(
                    strength_out_in_balance, nan=0.0
                )

            # Number of connections
            n_edges = len(X[X != 0])
            Xnet["n_edges"] = n_edges

            # Save the dictionary to a pickle file
            file_name = NET_DIR / f"net_metric_{sub}_{sub_state}.pkl"
            with open(file_name, "wb") as pickle_file:
                pickle.dump(Xnet, pickle_file)
