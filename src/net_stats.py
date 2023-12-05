"""
=================================
            TSNET
=================================
This module is design to perform a Student t-test for independent samples between
"""
import itertools

import pandas as pd
import scipy.stats as stats

from config import GENOT, REGION_ORDER
from tools import load_net_metrics

# get netdata
netdata, net_metrics = load_net_metrics()

# Perform paired t-test
results = []
for genot, region, metric in itertools.product(GENOT, REGION_ORDER, net_metrics):
    ctr = netdata.loc[
        (netdata["genot"] == genot)
        & (netdata["state"] == "ctr")
        & (netdata["region"] == region),
        metric,
    ]
    a5ia = netdata.loc[
        (netdata["genot"] == genot)
        & (netdata["state"] == "a5ia")
        & (netdata["region"] == region),
        metric,
    ]

    # Performing paired t-test
    t_val, p_val = stats.ttest_rel(ctr, a5ia)

    # Append results to the list
    results.append([genot, region, metric, t_val, p_val])

# Convert the list of results into a DataFrame
columns = ["genot", "region", "metric", "t_val", "p_val"]
result_df = pd.DataFrame(results, columns=columns)
result_df.to_csv("result_data.csv", index=False)
