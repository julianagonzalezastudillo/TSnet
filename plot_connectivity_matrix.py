import os.path
from scipy import io
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.colors import DivergingNorm
import matplotlib.colors
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable


path = '/Users/juliana.gonzalez/ownCloud/Juli-Javi/'
fc_path = path + 'fc_matrix/'
net_path = path + 'net_metric/'
plot_path = path + 'plots/'
if not os.path.exists(net_path):
    os.makedirs(net_path)

# get metadata
metadata = pd.read_csv(path + 'Ts65Dn_npx_a5IA_metadata_updated.csv')
genot = metadata["genot"].unique()
subjects = {genot[0]: list(metadata.loc[metadata['genot'] == genot[0], 'id_mouse']),
            genot[1]: list(metadata.loc[metadata['genot'] == genot[1], 'id_mouse'])}
num_nodes = metadata['num_nodes']
G_max = max(list(metadata['G_ctr_max']) + list(metadata['G_a5ia_max']))
G_min = min(list(metadata['G_ctr_min']) + list(metadata['G_a5ia_min']))

order = ['M2', 'AC', 'PrL', 'IL', 'DP']

cmap = matplotlib.colors.ListedColormap([(0., 0., 1.), "white", [1., .8, 0.], [1., .4, 0.], (1., 0., 0.)])
for sub_type in subjects.keys():
    print(sub_type)
    width_ratios = [i/min(metadata['num_nodes']) for i in metadata.loc[metadata['genot'] == sub_type, 'num_nodes']]
    size_x = sum(width_ratios)
    fig = plt.figure(figsize=(size_x + 1, 5), dpi=600)
    gs1 = gridspec.GridSpec(1, len(width_ratios), figure=fig, width_ratios=width_ratios)
    gs1.update(wspace=0.3, hspace=0.05)  # set the spacing between axes.

    for sub, i in zip(subjects[sub_type], range(len(subjects[sub_type]))):
        # load graph object from file
        net_file_ctr = fc_path + '{0}_ctr_net'.format(sub)
        G_ctr = pickle.load(open('{0}.pickle'.format(net_file_ctr), 'rb'))

        # order by region clusters
        region = nx.get_node_attributes(G_ctr, "region")
        order_sort = sorted(zip(np.arange(0, G_ctr.number_of_nodes()), G_ctr.nodes(), region.values()),
                            key = lambda node: [order.index(node[2])])
        order_by_region = [n[0] for n in order_sort]

        G_ctr = nx.to_numpy_array(G_ctr)  # transform to matrix
        G_ctr = G_ctr[:, order_by_region][order_by_region]  # reorder

        # G_a5ia = nx.to_numpy_array(G_a5ia)

        ax = plt.subplot(gs1[i])
        bounds = [-np.max(G_ctr) * 1/4, -1e-16, np.max(G_ctr) * 1/4, np.max(G_ctr) * 2/4, np.max(G_ctr) * 3/4, np.max(G_ctr)]
        norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        im = ax.imshow(G_ctr, cmap=cmap, norm=norm)
        ax.set_title('Sub{0}'.format(str(sub).zfill(3)), fontsize=5)

        # count nodes per region
        region_count = Counter(region.values())
        print(region_count)

        # thick line between regions
        r_sum = [0]
        for r, s in zip(order, range(len(order))):
            r_sum = np.append(r_sum, r_sum[s] + region_count[r])

        for s in np.arange(1, len(r_sum)-1):
            ax.axvline(r_sum[s], color='black', lw=0.4, clip_on=False, linestyle='--')
            ax.axhline(r_sum[s], color='black', lw=0.4, clip_on=False, linestyle='--')

        # set xticks according to modules
        # xticklabels = [None] * (len(r_sum) + len(order))
        # xticklabels[::2] = r_sum
        # xticklabels[1::2] = order
        # xticks = xticklabels.copy()
        # xticks[1::2] = (np.array(xticklabels[::2]) / 2)[1:]
        ax.set_xticks(r_sum)
        ax.set_xticklabels(r_sum, fontsize=6)
        ax.set_yticks(r_sum)
        ax.set_yticklabels(r_sum, fontsize=6)

        # colorbar
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size = '5%', pad = 0.05)
        cbar = fig.colorbar(im, cax=cax, orientation='vertical')
        cbar_ticks = cbar.ax.get_yticks()
        cbar.ax.set_yticklabels(['{:.3f}'.format(x) for x in cbar_ticks], fontsize=6)
        cbar.outline.set_linewidth(0.6)

    # borders
    fig.subplots_adjust(bottom=0.05)
    fig.subplots_adjust(top=0.95)
    fig.subplots_adjust(right=0.95)
    fig.subplots_adjust(left=0.05)

    # save
    plt.savefig(plot_path + 'connectivity_matrices_{0}'.format(sub_type), transparent=True)
    fig.suptitle(sub_type)
    plt.show()
