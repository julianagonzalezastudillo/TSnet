"""
=================================
            TSNET
=================================
This module is design to perform a Student t-test for independent samples between
"""
import itertools

import pandas as pd
import scipy.stats as stats

from config import DATA_DIR, GENOT, STATES, REGION_ORDER
from tools import load_net_metrics


def perform_t_test(data, genot, state, region, metric):
    group1_data = data.loc[
        (data["genot"] == genot[0])
        & (data["state"] == state[0])
        & (data["region"] == region),
        metric,
    ]

    group2_data = data.loc[
        (data["genot"] == genot[1])
        & (data["state"] == state[1])
        & (data["region"] == region),
        metric,
    ]

    if genot[0] == genot[1]:
        t_val, p_val = stats.ttest_rel(group1_data, group2_data)
        state_or_genot = genot[0]
    else:
        t_val, p_val = stats.ttest_ind(group1_data, group2_data, equal_var=False)
        state_or_genot = state[0]

    return [state_or_genot, region, metric, t_val, p_val]


# get netdata
netdata, net_metrics = load_net_metrics()

# Perform paired t-test across genotypes
results_genot = [
    perform_t_test(netdata, [genot, genot], ["ctr", "a5ia"], region, metric)
    for genot, region, metric in itertools.product(GENOT, REGION_ORDER, net_metrics)
]

# Convert the list of results into a DataFrame
columns = ["genot", "region", "metric", "t_val", "p_val"]
result_df_genot = pd.DataFrame(results_genot, columns=columns)
result_df_genot.to_csv(DATA_DIR / "Ts65Dn_stats_state.csv", index=False)


# Perform paired t-test across states
results_state = [
    perform_t_test(netdata, ["eu", "ts"], [state, state], region, metric)
    for state, region, metric in itertools.product(STATES, REGION_ORDER, net_metrics)
]

# Convert the list of results into a DataFrame
columns = ["state", "region", "metric", "t_val", "p_val"]
result_df_state = pd.DataFrame(results_state, columns=columns)
result_df_state.to_csv(DATA_DIR / "Ts65Dn_stats_genot.csv", index=False)
