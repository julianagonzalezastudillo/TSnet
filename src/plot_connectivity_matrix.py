"""
=================================
            1.1.TSNET
=================================
This module is designed to plot connectivity matrices for both group of subjects (eu, ts) and in both states (ctr, a5ia)
"""
import pickle
import numpy as np
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tools import load_metadata, order_by_region
from config import FC_DIR, PLOT_DIR, STATES, REGION_ORDER


# get metadata
metadata, subjects = load_metadata()

cmap = matplotlib.colors.ListedColormap(
    [(0.0, 0.0, 1.0), [1.0, 0.8, 0.0], [1.0, 0.4, 0.0], (1.0, 0.0, 0.0), ("#C700FF")]
)
for sub_type in subjects.keys():
    print(sub_type)
    width_ratios = [
        i / min(metadata["num_nodes"])
        for i in metadata.loc[metadata["genot"] == sub_type, "num_nodes"]
    ]
    size_x = sum(width_ratios)

    for sub_state in STATES:
        fig = plt.figure(figsize=(size_x + 1, 5), dpi=100)
        gs1 = gridspec.GridSpec(
            1, len(width_ratios), figure=fig, width_ratios=width_ratios
        )
        gs1.update(wspace=0.3, hspace=0.05)  # set the spacing between axes.

        for sub, i in zip(subjects[sub_type], range(len(subjects[sub_type]))):
            # load graph object from file
            net_file = FC_DIR / f"{sub}_{sub_state}_net"
            G = pickle.load(open(f"{net_file}.pickle", "rb"))
            region = nx.get_node_attributes(G, "region")

            # order by region clusters
            G, _, _, _ = order_by_region(G)  # reorder

            ax = plt.subplot(gs1[i])
            bounds = [
                -np.max(G) * 1 / 4,
                0,
                np.max(G) * 1 / 4,
                np.max(G) * 2 / 4,
                np.max(G) * 3 / 4,
                np.max(G),
            ]
            norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
            cmap.set_bad(color="k", alpha=1.0)  # --> nan
            G[G == 0] = np.nan
            im = ax.imshow(G, cmap=cmap, norm=norm)
            ax.set_title("Sub{0}".format(str(sub).zfill(3)), fontsize=10, color="white")

            # count nodes per region
            region_count = Counter(region.values())
            print(region_count)

            # thick line between regions
            r_sum = [0]
            for r, s in zip(REGION_ORDER, range(len(REGION_ORDER))):
                r_sum = np.append(r_sum, r_sum[s] + region_count[r])

            for s in np.arange(1, len(r_sum) - 1):
                ax.axvline(
                    r_sum[s], color="white", lw=0.4, clip_on=False, linestyle="--"
                )
                ax.axhline(
                    r_sum[s], color="white", lw=0.4, clip_on=False, linestyle="--"
                )

            # set xticks according to modules
            # xticklabels = [None] * (len(r_sum) + len(order))
            # xticklabels[::2] = r_sum
            # xticklabels[1::2] = order
            # xticks = xticklabels.copy()
            # xticks[1::2] = (np.array(xticklabels[::2]) / 2)[1:]
            ax.set_xticks(r_sum)
            ax.set_xticklabels(r_sum, fontsize=6, color="white")
            ax.set_yticks(r_sum)
            ax.set_yticklabels(r_sum, fontsize=6, color="white")
            [ax.spines[side].set_color("white") for side in ax.spines.keys()]

            # colorbar
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            cbar = fig.colorbar(im, cax=cax, orientation="vertical")
            cbar_ticks = cbar.ax.get_yticks()
            cbar.ax.set_yticklabels(
                ["{:.3f}".format(x) for x in cbar_ticks], fontsize=6, color="white"
            )
            cbar.outline.set_linewidth(0.6)

        # borders
        fig.subplots_adjust(bottom=0.05)
        fig.subplots_adjust(top=0.95)
        fig.subplots_adjust(right=0.95)
        fig.subplots_adjust(left=0.05)

        # save
        fig.suptitle([sub_type, sub_state])
        plt.savefig(
            PLOT_DIR / f"connectivity_matrices_{sub_type}_{sub_state}",
            transparent=True,
        )
        plt.show()
