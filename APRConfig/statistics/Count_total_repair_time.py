from datetime import time
from utils import Dataframe_util, Time_util
import os, re
import pandas as pd

cur_dir = os.path.dirname(os.path.abspath(__file__))


def merge_repair_df(df_dir, save_dir, dataset_name):
    if dataset_name == 'defects4j':
        df_all = pd.DataFrame()
        for i in range(1, 5):
            df_path = os.path.join(df_dir, f"machine_{i}", "repair_time_df.csv")
            df = Dataframe_util.read_csv(df_path)

            df['machine'] = df.shape[0] * [i]

            df_all = df_all.append(df)

        df_all_str_save_path = os.path.join(save_dir, "repair_time_cost_all.txt")
        Dataframe_util.save_df_str(df_all_str_save_path, df_all)

        df_all['seconds'] = df_all.apply(lambda row: to_seconds(row), axis=1)

        print_total_time(df_all)

    else:
        df_path = os.path.join(df_dir, "repair_time_df.csv")
        df = Dataframe_util.read_csv(df_path)
        df['seconds'] = df.apply(lambda row: to_seconds(row), axis=1)
        print_total_time(df)

def print_total_time(df):
    Total = df['seconds'].sum()
    print("total time(s):", Total)
    print("total time(m):", Total / 60)
    print("total time(h):", Total / 3600)
    print("total time(d):", Total / (3600 * 24))

def to_seconds(row):
    time_str = row['repair_time']
    # 0 days 00:29:59
    matches = re.findall(re.compile("(.*?) days (.*?):(.*?):(.*)"), time_str)
    # day, h, m, s = [int(i) for i in matches]
    # print(matches[0])
    assert len(matches) == 1
    day, h, m, s = [int(i) for i in matches[0]]
    time_cost = day * 24 * 3600 + h * 3600 + m * 60 + s
    return time_cost


def filter_df(df_all):
    bugs = list(set(df_all.bug.values))
    bugs.sort()
    df_all_filter = pd.DataFrame()

    cnt_dict = {
        "tbar2_cnt": 0,
        "tbar1_cnt": 0,
        "simfix2_cnt": 0,
        "simfix1_cnt": 0
    }

    for bug in bugs:
        df_tmp = df_all[df_all.bug == bug]
        for apr in ['tbar', 'simfix']:
            # e.g., if tbar 2 exists, then drop tbar 0 and tbar 1
            if (df_tmp[df_tmp.ori_apr == f"{apr}_2"]).shape[0] != 0:
                cnt_dict[f"{apr}2_cnt"] += 1
                # print(f"before: {df_tmp.shape}")
                df_tmp = df_tmp.drop(
                    df_tmp.loc[(df_tmp.ori_apr == f"{apr}_0") | (
                        df_tmp.ori_apr == f"{apr}_1")].index)  # inplace = True
                # print(f"after: {df_tmp.shape}")

            # e.g., if tbar 1 exists, we then drop tbar1&2 parsed from tbar 0
            if (df_tmp[df_tmp.ori_apr == f"{apr}_1"]).shape[0] != 0:
                cnt_dict[f"{apr}1_cnt"] += 1
                df_tmp = df_tmp.drop(
                    df_tmp.loc[(df_tmp.ori_apr == f"{apr}_0")
                               & ((df_tmp.apr == f"{apr}_1")
                                  | (df_tmp.apr == f"{apr}_2"))].index)
                df_tmp = df_tmp.drop(
                    df_tmp.loc[(df_tmp.ori_apr == f"{apr}_1")
                               & (df_tmp.apr == f"{apr}_3")].index)
        df_all_filter = df_all_filter.append(df_tmp)

    for apr in ['tbar', 'simfix']:
        print(
            f"[version 2: run insufficient memory cases] (e.g., if tbar 2 exists, then drop tbar 0 and tbar 1) {apr}2_cnt: {cnt_dict[f'{apr}2_cnt']}"
        )
        print(
            f"[version 1: incomplete pv 1 and 2 cases] (if tbar 1 exists, we then drop tbar1&2 parsed from tbar 0) {apr}1_cnt: {cnt_dict[f'{apr}1_cnt']}"
        )
    print(f"df_all_filter shape: {df_all_filter.shape}")

    return df_all_filter


if __name__ == "__main__":
    dataset_name = 'defects4j' #'quixbugs' #'defects4j'
    df_dir = os.path.abspath(
        os.path.join(cur_dir, "..", '..', f"results_{dataset_name}/parsed_results"))
    save_dir = os.path.abspath(
        os.path.join(cur_dir, "..", "..", f"results_{dataset_name}", "merge"))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    """
    pay attention to here before analyzing!
    """
    df_all = merge_repair_df(df_dir, save_dir, dataset_name)
    
    print(0.5759375+173.1041550925926)
    print(0.68009259259262 * 24)