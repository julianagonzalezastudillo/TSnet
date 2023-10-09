import os.path
from scipy import io
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tools import order_by_region


path = '/Users/juliana.gonzalez/ownCloud/Juli-Javi/'
fc_path = path + 'fc_matrix/'
plot_path = path + 'plots/'

# get metadata
metadata = pd.read_csv(path + 'Ts65Dn_npx_a5IA_metadata_updated.csv')
genot = metadata["genot"].unique()
subjects = {genot[0]: list(metadata.loc[metadata['genot'] == genot[0], 'id_mouse']),
            genot[1]: list(metadata.loc[metadata['genot'] == genot[1], 'id_mouse'])}

order = ['M2', 'AC', 'PrL', 'IL', 'DP']
states = ['ctr', 'a5ia']

cmap = matplotlib.colors.ListedColormap([(0., 0., 1.), [1., .8, 0.], [1., .4, 0.], (1., 0., 0.), ('#C700FF')])
for sub_type in subjects.keys():
    print(sub_type)
    width_ratios = [i/min(metadata['num_nodes']) for i in metadata.loc[metadata['genot'] == sub_type, 'num_nodes']]
    size_x = sum(width_ratios)

    for sub_state in states:
        fig = plt.figure(figsize=(size_x + 1, 5), dpi=600)
        gs1 = gridspec.GridSpec(1, len(width_ratios), figure=fig, width_ratios=width_ratios)
        gs1.update(wspace=0.3, hspace=0.05)  # set the spacing between axes.

        for sub, i in zip(subjects[sub_type], range(len(subjects[sub_type]))):
            # load graph object from file
            net_file_ctr = fc_path + '{0}_{1}_net'.format(sub, sub_state)
            G = pickle.load(open('{0}.pickle'.format(net_file_ctr), 'rb'))
            region = nx.get_node_attributes(G, "region")

            # order by region clusters
            G = order_by_region(G)  # reorder

            ax = plt.subplot(gs1[i])
            bounds = [-np.max(G) * 1/4, 0, np.max(G) * 1/4, np.max(G) * 2/4, np.max(G) * 3/4, np.max(G)]
            norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
            cmap.set_bad(color='k', alpha=1.)  # --> nan
            G[G == 0] = np.nan
            im = ax.imshow(G, cmap=cmap, norm=norm)
            ax.set_title('Sub{0}'.format(str(sub).zfill(3)), fontsize=10, color='white')

            # count nodes per region
            region_count = Counter(region.values())
            print(region_count)

            # thick line between regions
            r_sum = [0]
            for r, s in zip(order, range(len(order))):
                r_sum = np.append(r_sum, r_sum[s] + region_count[r])

            for s in np.arange(1, len(r_sum)-1):
                ax.axvline(r_sum[s], color='white', lw=0.4, clip_on=False, linestyle='--')
                ax.axhline(r_sum[s], color='white', lw=0.4, clip_on=False, linestyle='--')

            # set xticks according to modules
            # xticklabels = [None] * (len(r_sum) + len(order))
            # xticklabels[::2] = r_sum
            # xticklabels[1::2] = order
            # xticks = xticklabels.copy()
            # xticks[1::2] = (np.array(xticklabels[::2]) / 2)[1:]
            ax.set_xticks(r_sum)
            ax.set_xticklabels(r_sum, fontsize=6, color='white')
            ax.set_yticks(r_sum)
            ax.set_yticklabels(r_sum, fontsize=6, color='white')
            [ax.spines[side].set_color('white') for side in ax.spines.keys()]

            # colorbar
            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            cbar = fig.colorbar(im, cax=cax, orientation='vertical')
            cbar_ticks = cbar.ax.get_yticks()
            cbar.ax.set_yticklabels(['{:.3f}'.format(x) for x in cbar_ticks], fontsize=6, color='white')
            cbar.outline.set_linewidth(0.6)

        # borders
        fig.subplots_adjust(bottom=0.05)
        fig.subplots_adjust(top=0.95)
        fig.subplots_adjust(right=0.95)
        fig.subplots_adjust(left=0.05)

        # save
        fig.suptitle([sub_type, sub_state])
        plt.savefig(plot_path + 'connectivity_matrices_{0}_{1}_'.format(sub_type, sub_state), transparent=True)
        # plt.show()
