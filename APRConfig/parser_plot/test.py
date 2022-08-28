from utils import Dataframe_util, Time_util
import os
import pandas as pd

import Repairthemall_parse, Simfix_tbar_parse

cur_dir = os.path.dirname(os.path.abspath(__file__))


def merge_df(df_dir, save_dir):
    df_all = pd.DataFrame()
    for i in range(1, 5):
        df_path = os.path.join(df_dir, f"repair_df_{i}.csv")
        df = Dataframe_util.read_csv(df_path)

        df['machine'] = df.shape[0] * [i]

        df_str_save_path = os.path.join(save_dir, f"df_{i}.txt")
        Dataframe_util.save_df_str(df_str_save_path, df)

        df_all = df_all.append(df)
    # print(df_all.info())
    df_all.sort_values(by=["bug", 'apr'], inplace=True)
    df_all.reset_index(inplace=True, drop=True)

    df_all_str_save_path = os.path.join(save_dir, "df_all.txt")
    # repair_df.to_csv(df_save_path)
    Dataframe_util.save_df_str(df_all_str_save_path, df_all)

    return df_all


def filter_df(df_all):

    bugs = list(set(df_all.bug.values))
    bugs.sort()
    # print(bugs)

    df_all_filter = pd.DataFrame()
    # print(f"df_all shape: {df_all.shape}")

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


def parse_insufficient_memory_cases(df):
    """
    1) check
    """
    df_memory = df[df.insufficient_memory == 'YES']
    print("insufficient memory cases:", df_memory.shape)

    for _, row in df_memory.iterrows():
        # print(row)
        df_memory_done = df[(df.insufficient_memory == "NO")
                            & (df.apr == row.apr) & (df.bug == row.bug)]
        # print(row)
        # print(f"{df_memory_done.to_string()} ================")
        if df_memory_done.shape[0] == 0:
            print("memory exception is still not eliminated yet", row.ori_apr,
                  row.apr, row.bug, row.machine)
        else:
            print("memory exception is eliminated:", row.ori_apr, row.apr,
                  row.bug, row.machine)
    """
    2) remove
    """
    # print(df.shape)
    # print(df.loc[df.insufficient_memory == "YES"].index)
    df = df.drop(df.loc[ (df.insufficient_memory == "YES") & (df.filter_pass_all != "YES") ].index)
    # print(df.shape)
    return df


# def check_nopol_dynamoth_difference(df_all_filter, rta_df):
#     for apr_name in ['Nopol', 'DynaMoth']:
#         df_nopol_patches = set(
#             df_all_filter[df_all_filter.apr.str.startswith(apr_name.lower())
#                           & (df_all_filter.has_patch == "yes")].bug.values)
#         rta_nopol_patches = set(rta_df[rta_df.apr == apr_name].bug.values)
#         print(len(df_nopol_patches), len(rta_nopol_patches))

#         print(f"union: {len(df_nopol_patches | rta_nopol_patches)}")
#         print(f"intersection: {len(rta_nopol_patches & df_nopol_patches)}")
#         print(f"diff (df specific): {df_nopol_patches - rta_nopol_patches}")
#         print(f"diff (rta specific): {rta_nopol_patches - df_nopol_patches}")

#         for bug in df_nopol_patches - rta_nopol_patches:
#             df_machine_4 = df_all_filter[
#                 df_all_filter.apr.str.startswith(apr_name.lower())
#                 & (df_all_filter.bug == bug)]
#             print(
#                 f"(df specific) {apr_name} {bug}: {df_machine_4.machine.values}"
#             )

#         for bug in rta_nopol_patches - df_nopol_patches:
#             df_machine_4 = df_all_filter[
#                 df_all_filter.apr.str.startswith(apr_name.lower())
#                 & (df_all_filter.bug == bug)]
#             print(
#                 f"(rta specific) {apr_name} {bug}: {df_machine_4.machine.values}"
#             )
#             # df_machine_4 = df_all_filter[df_all_filter.apr.str.startswith('nopol') & (df_all_filter.bug == bug) & (df_all_filter.machine == 4) ]
#             # if df_machine_4.shape[0] != 0:
#             #     print(bug)


def remove_invalid_duplicates(df_all_filter):

    print("df_all_filter.shape:", df_all_filter.shape)

    incomplete_df = df_all_filter[df_all_filter.repair_time == "-"].copy()
    for index, row in incomplete_df.iterrows():
        df_tmp = df_all_filter[(df_all_filter.repair_time != "-")
                               & (df_all_filter.bug == row['bug']) &
                               (df_all_filter.apr == row['apr'])]
        if df_tmp.shape[0] != 0:
            df_all_filter.drop(index, inplace=True)
            print("df_all_filter.shape:", df_all_filter.shape)
    return df_all_filter


# parse for rerun!
def parse_incomplete_cases(df_all_filter, save_dir):
    df_all_filter.sort_values('repair_time', inplace=True)

    incomplete_df = df_all_filter[df_all_filter.repair_time == "-"].copy()
    print("incomplete_df.shape:", incomplete_df.shape)

    # drop if all 4 tools are not complete
    bug_set = set(incomplete_df.bug.values)
    print(incomplete_df.info())
    print(len(bug_set))
    for bug in bug_set:
        # print(len(bug_set))
        values = set(
            df_all_filter[df_all_filter.bug == bug].repair_time.values)
        if len(values) == 1:
            incomplete_df.drop(
                incomplete_df.loc[incomplete_df.bug == bug].index,
                inplace=True)
            print("incomplete_df.shape:", incomplete_df.shape)
        # 149

    incomplete_df.sort_values(['apr', 'bug'], inplace=True)
    df_all_filter_str_save_path = os.path.join(save_dir,
                                               "incomplete_cases.txt")
    Dataframe_util.save_df_str(df_all_filter_str_save_path,
                               incomplete_df[['ori_apr', 'machine', 'bug']],
                               index=False)

def resolve_filter_pass_all(df_all_filter):
    df_all_filter.loc[df_all_filter['filter_pass_all'] == "YES", 'has_patch'] = 'yes'

def resolve_insufficient_memory_2(df_all_filter):
    df_all_filter.loc[df_all_filter['insufficient_memory_2'] == "YES", 'has_patch'] = '0'

if __name__ == "__main__":
    Time_util.update_start_time()
    df_dir = os.path.join(cur_dir, "../..", "results_defects4j/parser_results",
                          "all_machines")
    save_dir = os.path.join(cur_dir, "../..",
                            "results_defects4j/parser_results", "merge")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    """
    pay attention to here before analyzing!
    """
    df_filter_load_path = os.path.join(save_dir, "df_all_filter_final.csv")
    re_filter = False  # can save time if set as true

    if re_filter and os.path.exists(df_filter_load_path):
        df_all_filter = Dataframe_util.read_csv(df_filter_load_path)
    else:
        df_all = merge_df(df_dir, save_dir)

        # filter tbar and simfix
        df_all_filter = filter_df(df_all)
        df_all_filter_str_save_path = os.path.join(save_dir,
                                                   "df_all_filter_1.txt")
        Dataframe_util.save_df_str(df_all_filter_str_save_path, df_all_filter)

        # parse prior insufficient memory cases & remove them
        df_all_filter = parse_insufficient_memory_cases(df_all_filter)
        df_all_filter_str_save_path = os.path.join(save_dir,
                                                   "df_all_filter_2.txt")
        Dataframe_util.save_df_str(df_all_filter_str_save_path, df_all_filter)

        # parse '-' incomplete cases
        # 1) remove invalid duplicates
        df_all_filter = remove_invalid_duplicates(df_all_filter)
        df_all_filter_str_save_path = os.path.join(save_dir,
                                                   "df_all_filter_3.txt")
        Dataframe_util.save_df_str(df_all_filter_str_save_path, df_all_filter)

        # 1) deal with "filter_pass_all" == YES for nopol and dynamothh
        resolve_filter_pass_all(df_all_filter)
        df_all_filter_str_save_path = os.path.join(save_dir,
                                                   "df_all_filter_4.txt")
        Dataframe_util.save_df_str(df_all_filter_str_save_path, df_all_filter)

        # 2) parse duplicates that may require re-run
        parse_incomplete_cases(df_all_filter, save_dir)

        # 3) reset insufficient memory 2 cases
        resolve_insufficient_memory_2(df_all_filter)


        # save for re-load
        Dataframe_util.write_csv(df_filter_load_path, df_all_filter)

    # get original results as provided by the literature/repo of the APR tools
    rta_df = Repairthemall_parse.parse_result()
    Dataframe_util.write_csv(os.path.join(save_dir, "rta_df.csv"), rta_df)

    simfix_ori_df = Simfix_tbar_parse.parse_simfix_result()
    Dataframe_util.write_csv(os.path.join(save_dir, "simfix_ori_df.csv"),
                             simfix_ori_df)

    tbar_ori_df = Simfix_tbar_parse.parse_tbar_result()
    Dataframe_util.write_csv(os.path.join(save_dir, "tbar_ori_df.csv"),
                             tbar_ori_df)

    # time cost
    Time_util.cal_time_cost()

    # study difference
    # check_nopol_dynamoth_difference(df_all_filter, rta_df)
    # plot nopol & dynamoth
    # plot_df(df_all_filter)