import os.path
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


path = "/Users/juliana.gonzalez/ownCloud/Juli-Javi/"
net_path = os.path.join(path, "net_metric")

# get metadata
metadata = pd.read_csv(path + "Ts65Dn_npx_a5IA_metadata_updated.csv")
genot = metadata["genot"].unique()
subjects = {genot[0]: list(metadata.loc[metadata["genot"] == genot[0], "id_mouse"]),
            genot[1]: list(metadata.loc[metadata["genot"] == genot[1], "id_mouse"])}

# add states to metadata
states = ["ctr", "a5ia"]
metadata = pd.concat([metadata] * len(states), ignore_index=True)
metadata["state"] = states * int(len(metadata) / len(states))

# add regions to metadata
regions = ['M2', 'AC', 'PrL', 'IL', 'DP']
metadata = pd.concat([metadata] * len(regions), ignore_index=True)
metadata["region"] = regions * int(len(metadata) / len(regions))

# Load data from Xnet for each subject and build data frame
net_list = []
subs = []
subs_state = []
for sub, sub_state in zip(metadata["id_mouse"],
                          states * int(len(np.unique(metadata["id_mouse"])))):
    # Load data
    file_name = os.path.join(net_path, f"net_metric_{sub}_{sub_state}.pkl")
    with open(file_name, 'rb') as pickle_file:
        Xnet = pickle.load(pickle_file)
        net_list.append(Xnet)
        subs.append(sub)
        subs_state.append(sub_state)
net_data = pd.DataFrame(net_list)
net_data = net_data.fillna(0)
net_metrics = np.unique(['_'.join(metric.split('_')[1:]) for metric in net_data.columns])
net_data["id_mouse"] = subs
net_data["state"] = subs_state

# Initialize metrics column with None values
metadata.update({metric: [None] * len(metadata) for metric in net_metrics})

# Fill metrics columns
for index, row in metadata.iterrows():
    sub = row['id_mouse']
    state = row['state']
    region = row['region']
    for metric in net_metrics:
        value = net_data.loc[(net_data['id_mouse'] == sub) & (net_data['state'] == state), '_'.join([region, metric])]
        # Set the new value for the 'metric' column
        metadata.loc[index, metric] = value.values[0]

# Create a boxplot using Seaborn
state = "ctr"
for metric in net_metrics:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=metadata[metadata['state'] == state], x='region', y=metric, hue='genot', palette='Set3')
    # sns.boxplot(data=metadata, x='region', y='strength_inter', hue='state', palette='Set3', width=0.5)

    # Add labels and legend
    plt.xlabel('')
    plt.ylabel('')
    plt.title(metric, fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    min_limit = 0 if metadata[metric].min() > 0 else metadata[metric].min()
    plt.ylim(min_limit - 0.1, 1.1)
    nodes_file = os.path.join(path, "plots", f"{metric}_{state}.png")
    plt.savefig(nodes_file, dpi=300, bbox_inches='tight', transparent=True)
    plt.show()