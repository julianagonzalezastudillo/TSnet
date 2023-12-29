"""
=================================
            3.TSNET
=================================
This module is design to perform a Student t-test for independent samples between
"""
import glob
import itertools

import pandas as pd
import scipy.stats as stats

from config import (
    RES_DIR,
    STATS_DIR,
    GENOT,
    STATES,
    REGION_ORDER,
    MODULS_ORDER,
    ATTRIBUTE,
    BINARIZE,
)
from tools import load_net_metrics


def perform_t_test(data, genot, state, metric, ATTR, attr=None):
    """
    Perform a statistical t-test across genotypes (eu, ts) or states (ctr, a5ia; paired t-test).

    :param scale: str, optional
        The scale of the analysis, either "local" or "global". Defaults to "local".
    :param data: pd.DataFrame
        DataFrame containing network data.
    :param genot: list of str
        List with two possible genotypes ["eu", "ts"] or ["eu", "eu"] or ["ts", "ts"].
    :param state: list of str
        List with two possible states ["ctr", "a5ia"] or ["ctr", "ctr"] or ["a5ia", "a5ia"].
    :param attr: str
        Selected attribute for filtering.
    :param ATTR: str
        Type of attribute for filtering, either "region" or "modulus".
    :param metric: str
        Selected metric for the t-test.
    :return: list
        A list containing the results of the t-test:
        - state_or_genot: str
            The state or genotype under analysis.
        - attr: str
            The selected attribute.
        - metric: str
            The selected metric.
        - t_val: float
            The calculated t-value.
        - p_val: float
            The calculated p-value.
    """

    # Common conditions for both 'local' and 'global' scales
    common_conditions1 = (data["genot"] == genot[0]) & (data["state"] == state[0])
    common_conditions2 = (data["genot"] == genot[1]) & (data["state"] == state[1])

    if attr:
        # Additional condition for 'local' scale
        common_conditions1 &= data[ATTR] == attr
        common_conditions2 &= data[ATTR] == attr

    # Use the common conditions to filter the data for both group1 and group2
    group1_data = data.loc[common_conditions1, metric]
    group2_data = data.loc[common_conditions2, metric]

    if genot[0] == genot[1]:
        # Paired t-test
        t_val, p_val = stats.ttest_rel(group1_data, group2_data)
        state_or_genot = genot[0]
    else:
        t_val, p_val = stats.ttest_ind(group1_data, group2_data, equal_var=False)
        state_or_genot = state[0]

    return [state_or_genot, attr, metric, t_val, p_val]


# Use a dictionary to map ATTRIBUTE to its corresponding order
ATT_ORDER = {"region": REGION_ORDER, "moduls": MODULS_ORDER}[ATTRIBUTE]
binarize = "bin" if BINARIZE else "nonbin"

for scale in ["local", "global"]:
    # get netdata
    netdata, net_metrics = load_net_metrics(
        scale=scale, binarize=binarize, attribute=ATTRIBUTE
    )
    att_order = ATT_ORDER if scale == "local" else [None]

    # Perform paired t-test across genotypes
    results_genot = [
        perform_t_test(
            netdata, [genot, genot], ["ctr", "a5ia"], metric, ATTRIBUTE, attr=attribute
        )
        for genot, attribute, metric in itertools.product(GENOT, att_order, net_metrics)
    ]

    # Convert the list of results into a DataFrame
    columns = ["genot", ATTRIBUTE, "metric", "t_val", "p_val"]
    result_df_genot = pd.DataFrame(results_genot, columns=columns)

    # Add binarize column
    result_df_genot["binarize"] = binarize
    result_df_genot.to_csv(
        STATS_DIR / f"Ts65Dn_stats_state_{binarize}_{ATTRIBUTE}_{scale}.csv",
        index=False,
    )

    # Perform paired t-test across states
    results_state = [
        perform_t_test(
            netdata, ["eu", "ts"], [state, state], metric, ATTRIBUTE, attr=attribute
        )
        for state, attribute, metric in itertools.product(
            STATES, att_order, net_metrics
        )
    ]

    # Convert the list of results into a DataFrame
    columns = ["state", ATTRIBUTE, "metric", "t_val", "p_val"]
    result_df_state = pd.DataFrame(results_state, columns=columns)

    # Add binarize column
    result_df_state["binarize"] = binarize
    result_df_state.to_csv(
        STATS_DIR / f"Ts65Dn_stats_genot_{binarize}_{ATTRIBUTE}_{scale}.csv",
        index=False,
    )

# Put all stats together in one file
csv_files = glob.glob(str(STATS_DIR / "*.csv"))

if len(csv_files) == 16:
    # Loop through each CSV file and load it into a DataFrame
    dfs = []
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        dfs.append(df)

    # Concatenate the list of DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)

    # Reorganize colomns and save
    desired_order = [
        "genot",
        "state",
        "binarize",
        "region",
        "moduls",
        "metric",
        "t_val",
        "p_val",
    ]
    result_df = pd.DataFrame(combined_df, columns=desired_order)

    # Fill nan with corresponding values
    result_df["genot"].fillna("eu-ts", inplace=True)
    result_df["state"].fillna("ctr-a5ia", inplace=True)
    result_df["moduls"].fillna("-", inplace=True)
    result_df["region"].fillna("-", inplace=True)

    result_df.to_csv(RES_DIR / f"Ts65Dn_stats_genot.csv", index=False)
