"""
=================================
            3.TSNET
=================================
This module is design to perform a Student t-test for independent samples between
"""
import itertools

import pandas as pd
import scipy.stats as stats

from config import RES_DIR, GENOT, STATES, REGION_ORDER, MODULS_ORDER, ATTRIBUTE
from tools import load_net_metrics


def perform_t_test(data, genot, state, attr, ATTR, metric, scale="local"):
    """
    Perform statistical test across genotypes (eu, ts) or states (ctr, a5ia).

    :param scale:
    :param data: data frame with netdata
    :param genot: list with two possible genotypes ["eu", "ts"] or ["eu", "eu"] or ["ts", "ts"]
    :param state: list with two possible states ["ctr", "a5ia"] or ["ctr", "ctr"] or ["a5ia", "a5ia"]
    :param attr: select attribute
    :param ATTR:
    :param metric: selected metric
    :return: [state_or_genot, attr, metric, t_val, p_val]

    """

    # Common conditions for both 'local' and 'global' scales
    common_conditions1 = (data["genot"] == genot[0]) & (data["state"] == state[0])
    common_conditions2 = (data["genot"] == genot[1]) & (data["state"] == state[1])

    if scale == "local":
        # Additional condition for 'local' scale
        common_conditions1 &= data[ATTR] == attr
        common_conditions2 &= data[ATTR] == attr

    # Use the common conditions to filter the data for both group1 and group2
    group1_data = data.loc[common_conditions1, metric]
    group2_data = data.loc[common_conditions2, metric]

    if genot[0] == genot[1]:
        t_val, p_val = stats.ttest_rel(group1_data, group2_data)
        state_or_genot = genot[0]
    else:
        t_val, p_val = stats.ttest_ind(group1_data, group2_data, equal_var=False)
        state_or_genot = state[0]

    return [state_or_genot, attr, metric, t_val, p_val]


# Use a dictionary to map ATTRIBUTE to its corresponding order
ATT_ORDER = {"region": REGION_ORDER, "moduls": MODULS_ORDER}[ATTRIBUTE]
SCALE = "local"

# get netdata
netdata, net_metrics = load_net_metrics(scale=SCALE, attribute=ATTRIBUTE)

# Perform paired t-test across genotypes
results_genot = [
    perform_t_test(
        netdata,
        [genot, genot],
        ["ctr", "a5ia"],
        attribute,
        ATTRIBUTE,
        metric,
        scale=SCALE,
    )
    for genot, attribute, metric in itertools.product(GENOT, ATT_ORDER, net_metrics)
]

# Convert the list of results into a DataFrame
columns = ["genot", ATTRIBUTE, "metric", "t_val", "p_val"]
result_df_genot = pd.DataFrame(results_genot, columns=columns)
result_df_genot.to_csv(
    RES_DIR / f"Ts65Dn_stats_state_{ATTRIBUTE}_{SCALE}.csv", index=False
)


# Perform paired t-test across states
results_state = [
    perform_t_test(
        netdata,
        ["eu", "ts"],
        [state, state],
        attribute,
        ATTRIBUTE,
        metric,
        scale=SCALE,
    )
    for state, attribute, metric in itertools.product(STATES, ATT_ORDER, net_metrics)
]

# Convert the list of results into a DataFrame
columns = ["state", ATTRIBUTE, "metric", "t_val", "p_val"]
result_df_state = pd.DataFrame(results_state, columns=columns)
result_df_state.to_csv(
    RES_DIR / f"Ts65Dn_stats_genot_{ATTRIBUTE}_{SCALE}.csv", index=False
)
