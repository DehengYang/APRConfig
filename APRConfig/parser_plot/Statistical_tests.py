from scipy.stats import wilcoxon
from bisect import bisect_left
import scipy.stats as ss
import pandas as pd

from utils import Dataframe_util
import Plot_util

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list


def statistical_tests(df_all):
    df_has_patch = df_all[df_all.has_patch == "yes"].copy()
    df_has_patch['repair_time'] = df_has_patch['repair_time'].astype(float) + df_has_patch['fl_time'].astype(float)

    all_apr_df = pd.DataFrame()
    for apr in apr_name_list:
        apr_df = df_has_patch[df_has_patch.apr.str.startswith(apr)].copy()
        for bug in apr_df.bug.values:
            tmp_df = apr_df[apr_df.bug == bug]
            if tmp_df.shape[0]  > 3:
                print(tmp_df.to_string())

            if tmp_df.shape[0] != 3:
                apr_df.drop(tmp_df.index, inplace=True)
        
        # tests
        # 12
        data1 = apr_df[apr_df.apr == f"{apr}_1"]['repair_time'].values.tolist()
        data2 = apr_df[apr_df.apr == f"{apr}_2"]['repair_time'].values.tolist()
        data3 = apr_df[apr_df.apr == f"{apr}_3"]['repair_time'].values.tolist()

        print(f"\n\n{apr}")
        
        stat, p = wilcoxon(data2, data1)
        estimate, magnitude = a_statistics(data1, data2)
        print(f"12 stat: {stat}, p: {p}, estimate: {estimate}, magnitude: {magnitude}")
        
        stat, p = wilcoxon(data1, data3)
        estimate, magnitude = a_statistics(data1, data3)
        print(f"13 stat: {stat}, p: {p}, estimate: {estimate}, magnitude: {magnitude}")
        
        stat, p = wilcoxon(data2, data3)
        estimate, magnitude = a_statistics(data2, data3)
        print(f"23 stat: {stat}, p: {p}, estimate: {estimate}, magnitude: {magnitude}")
            
        # print(apr, apr_df.shape[0]/3)
        all_apr_df = all_apr_df.append(apr_df)

# https://gist.github.com/jacksonpradolima/f9b19d65b7f16603c837024d5f8c8a65
def a_statistics(treatment, control):
    m = len(treatment)
    n = len(control)

    if m != n:
        raise ValueError("Data d and f must have the same length")

    r = ss.rankdata(treatment + control)
    r1 = sum(r[0:m])

    # Compute the measure
    # A = (r1/m - (m+1)/2)/n # formula (14) in Vargha and Delaney, 2000
    A = (2 * r1 - m * (m + 1)) / (2 * n * m)  # equivalent formula to avoid accuracy errors
    print(f"A: {A}")

    levels = [0.147, 0.33, 0.474]  # effect sizes from Hess and Kromrey, 2004
    magnitude = ["negligible", "small", "medium", "large"]
    scaled_A = (A - 0.5) * 2
    print(f"scaled_A: {scaled_A}")

    magnitude = magnitude[bisect_left(levels, abs(scaled_A))]
    estimate = A

    return estimate, magnitude

if __name__ == "__main__":
    df_all, _ = Plot_util.load_all_df()
    statistical_tests(df_all)