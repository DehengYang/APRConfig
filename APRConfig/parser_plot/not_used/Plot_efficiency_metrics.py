import os
from numpy import true_divide
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from venn import venn

from utils import Dataframe_util, File_util
import Plot_util

cur_dir = os.path.dirname(os.path.abspath(__file__))
parse_result_dir = Plot_util.parse_result_dir
save_dir = Plot_util.save_dir

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list


def plot(df_all_filter_final):
    df_has_patch = df_all_filter_final[df_all_filter_final.has_patch ==
                                       "yes"].copy()
    """
    for each pv, get the venn for all tools
    """
    for pv in ['1', '2', '3']:
        pv_dict = {}
        for apr in apr_name_list:
            pv_dict[f'{apr}_{pv}'] = set(
                df_has_patch[df_has_patch.apr == f"{apr}_{pv}"].bug.values)

        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 12))  #
        ax_list = []
        for row in axes:
            for col in row:
                ax_list.append(col)

        # plot venn
        ax = venn(
            pv_dict, ax= ax_list[0],
            figsize=(6, 6))  #,fontsize= Plot_util.FONT_SIZE ,figsize=(15,15)
        ax.set_title(f"pv_{pv}")
        # plt.show()

        # get intersection
        intersection = set()
        for apr in apr_name_list:
            if len(intersection) == 0:
                intersection = intersection | pv_dict[f"{apr}_{pv}"]
            else:
                intersection = intersection & pv_dict[f"{apr}_{pv}"]
        intersection_df = pd.DataFrame()
        for bug in intersection:
            intersection_df = intersection_df.append(
                df_has_patch[(df_has_patch.bug == bug)
                             & (df_has_patch.apr.str.endswith(f'_{pv}'))])

        intersection_df.sort_values('apr', inplace=True)
        intersection_df['Repair Time'] = intersection_df['repair_time'].astype(
            float)
        intersection_df['NCP'] = intersection_df['ncp'].astype(int)
        intersection_df['NTCE'] = intersection_df['ntce'].astype(int)
        
        intersection_df = intersection_df[['apr', 'Repair Time', 'NCP', 'NTCE', 'bug', 'pg_time', 'compile_time', 'pv_time']]
        Dataframe_util.save_df_str(os.path.join(save_dir, f"intersection_df_pv_{pv}.txt"), intersection_df)

        Plot_util.set_theme()
        ax_index = 0
        for y in ['Repair Time', 'NCP', 'NTCE']:
            ax_index += 1
            # plt.figure()  #figsize=(9, 6) figsize=(10, 10)
            ax = sns.boxplot(x='apr',
                             y=y,
                             data=intersection_df,
                             showfliers=True, ax = ax_list[ax_index])  #, orient = 'h'
            # ax.set_xlabel("APR Techniques")
            ax.set_xlabel("")
            ax.set_ylabel(y)
            # plt.tight_layout()
        plt.show()


def pv_label(row):
    return 'pv_' + row['apr'].split("_")[-1]


def apr_name_label(row):
    return apr_name_dict[row['apr'].split("_")[0]]


if __name__ == "__main__":
    df_all_filter_final, rta_df = Plot_util.load_all_df()
    plot(df_all_filter_final)
