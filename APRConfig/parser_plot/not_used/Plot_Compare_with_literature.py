import os
from numpy import save, true_divide
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from venn import venn

from utils import Dataframe_util, File_util
import Plot_util

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list

cur_dir = os.path.dirname(os.path.abspath(__file__))
parse_result_dir = os.path.abspath(
    os.path.join(cur_dir, "../../results_defects4j/parser_results-6th-rerun/"))
save_dir = os.path.join(parse_result_dir, "figs")
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


def load_all_df(parse_result_dir=parse_result_dir):
    merge_dir = os.path.join(parse_result_dir, 'merge')
    df_all_filter_final = Dataframe_util.read_csv(
        os.path.join(merge_dir, 'df_all_filter_final.csv'))
    print("df_all_filter_final:", df_all_filter_final.shape)
    rta_df = Dataframe_util.read_csv(os.path.join(merge_dir, 'rta_df.csv'))
    return df_all_filter_final, rta_df


def load_literature_data():
    merge_dir = os.path.join(parse_result_dir, 'merge')

    nopol_ori_df = rta_df[rta_df.apr == 'nopol'].copy()
    dynamoth_ori_df = rta_df[rta_df.apr == 'dynamoth'].copy()
    simfix_ori_df = Dataframe_util.read_csv(
        os.path.join(merge_dir, 'simfix_ori_df.csv'))
    tbar_ori_df = Dataframe_util.read_csv(
        os.path.join(merge_dir, 'tbar_ori_df.csv'))

    literature_df_dict = {}
    for apr in ['simfix', 'tbar', 'nopol', 'dynamoth']:
        literature_df_dict[apr] = locals()[f'{apr}_ori_df']
    return literature_df_dict


def plot_number_of_fixed_bugs(df_all_filter_final,
                              rta_df,
                              parse_result_dir=parse_result_dir):
    df_fixed_bugs_nums_csv_path = os.path.join(parse_result_dir,
                                               "df_fixed_bugs_nums.csv")

    # restore from file to avoid repeated and time-consuming parsing
    restore = False
    if restore and os.path.exists(df_fixed_bugs_nums_csv_path):
        df_fixed_bugs_nums = Plot_util.restore_df(df_fixed_bugs_nums_csv_path)
    else:
        literature_df_dict = load_literature_data()

        df_fixed_bugs = pd.DataFrame(columns=['apr', 'version', 'fixed_bug'])
        df_fixed_bugs_nums = pd.DataFrame(
            columns=['apr', 'version', 'fixed_bug_cnt'])
        fixed_bugs_paired_dict = {}
        for apr in apr_name_list:
            apr_repaired = df_all_filter_final[
                df_all_filter_final.apr.str.startswith(apr)
                & (df_all_filter_final.has_patch == "yes")].copy()
            apr_repaired.drop_duplicates('bug', inplace=True)
            apr_repaired['apr'] = [apr] * apr_repaired.shape[0]
            apr_repaired['version'] = ['new'] * apr_repaired.shape[0]
            apr_repaired.rename(columns={'bug': 'fixed_bug'}, inplace=True)

            df_fixed_bugs = df_fixed_bugs.append(
                apr_repaired[['apr', 'version', 'fixed_bug']])

            ori_apr_df = literature_df_dict[apr].copy()
            ori_apr_df['version'] = ['original'] * ori_apr_df.shape[0]
            ori_apr_df['apr'] = [apr] * ori_apr_df.shape[0]
            ori_apr_df.rename(columns={'bug': 'fixed_bug'}, inplace=True)
            df_fixed_bugs = df_fixed_bugs.append(
                ori_apr_df[['apr', 'version', 'fixed_bug']])

            df_fixed_bugs_nums.loc[df_fixed_bugs_nums.shape[0]] = [
                apr, 'new', apr_repaired.shape[0]
            ]
            df_fixed_bugs_nums.loc[df_fixed_bugs_nums.shape[0]] = [
                apr, 'original', ori_apr_df.shape[0]
            ]

            new_fixed = set(apr_repaired.fixed_bug.values)
            original_fixed = set(ori_apr_df.fixed_bug.values)
            fixed_bugs_paired_dict[f"our_data_{apr}"] = new_fixed
            fixed_bugs_paired_dict[f"literature_data_{apr}"] = original_fixed

        plot_venn(apr, fixed_bugs_paired_dict)

        df_fixed_bugs.reset_index(inplace=True, drop=True)

        File_util.write_str_to_file(os.path.join(parse_result_dir, "tmp.txt"),
                                    df_fixed_bugs.to_string(), False)

        # backup for restore
        Plot_util.save_df(df_fixed_bugs_nums, df_fixed_bugs_nums_csv_path)

    # replace xticks
    df_fixed_bugs_nums["apr"].replace(
        {
            "nopol": "Nopol",
            "dynamoth": "DynaMoth",
            'simfix': "SimFix",
            "tbar": "TBar"
        },
        inplace=True)

    font_size = Plot_util.FONT_SIZE
    sns.set_theme(style="darkgrid",
                  font=Plot_util.FONT,
                  palette=Plot_util.PALETTE,
                  rc={
                      'font.size': font_size,
                      'axes.labelsize': font_size,
                      'axes.titlesize': font_size,
                      'xtick.labelsize': font_size,
                      'ytick.labelsize': font_size,
                      'legend.fontsize': font_size
                  })
    plt.figure(figsize=(9, 6))
    figure = plt.gcf()
    ax = sns.barplot(x="apr",
                     y="fixed_bug_cnt",
                     hue="version",
                     data=df_fixed_bugs_nums,
                     ci=None)
    Plot_util.show_values_on_bars(ax)
    plt.legend(title='', loc='best', labels=['Our data', 'Literature data'])

    # Customize the axes and title
    # ax.set_title("Miles walked")
    ax.set_xlabel("APR Techniques")
    ax.set_ylabel("Number of Fixed Bugs")

    # Remove top and right borders
    # ax.spines['top'].set_visible(False)
    # ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.show()
    figure.savefig(os.path.join(save_dir, "fixed_bugs_cnt.pdf"), dpi=800)
    figure.savefig(os.path.join(save_dir, "fixed_bugs_cnt.jpg"), dpi=800)


def plot_venn(apr, fixed_bugs_all_dict):
    # plot venn graphs
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 12))
    """
    # using tuple unpacking for multiple Axes
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    """
    ax_list = []
    for row in axes:
        for col in row:
            ax_list.append(col)

    for i in range(len(apr_name_list)):
        apr = apr_name_list[i]
        new_fixed = fixed_bugs_all_dict[f"our_data_{apr}"]
        original_fixed = fixed_bugs_all_dict[f"literature_data_{apr}"]
        paired_dict = {}
        paired_dict['our_data'] = new_fixed
        paired_dict['literature_data'] = original_fixed

        print(f"{apr} union: {len(new_fixed | original_fixed)}")
        print(f"{apr} intersection: {len(new_fixed & original_fixed)}")
        print(f"{apr} diff (new specific): {new_fixed - original_fixed}\n")
        print(f"{apr} diff (original specific): {original_fixed - new_fixed}")

        ax = ax_list[i]
        venn(paired_dict, ax=ax,
             figsize=(6, 6))  #,fontsize= Plot_util.FONT_SIZE ,figsize=(15,15)
        ax.set_title(f"{apr_name_dict[apr]}")
        # plt.title(f"Number of Fixed Bugs by {apr_name_dict[apr]}")

    figure = plt.gcf()
    plt.show()
    figure.savefig(os.path.join(save_dir, f"venn.jpg"), dpi=800)

    # plt.figure()
    our_four_apr_dict = {}
    for apr in apr_name_list:
        our_four_apr_dict[apr_name_dict[apr]] = fixed_bugs_all_dict[f"our_data_{apr}"]
    print(our_four_apr_dict)
    venn(our_four_apr_dict,
         figsize=(9, 9))
    plt.show()
    figure.savefig(os.path.join(save_dir, f"venn_all.jpg"), dpi=800)


if __name__ == "__main__":
    df_all_filter_final, rta_df = load_all_df()
    plot_number_of_fixed_bugs(df_all_filter_final, rta_df)
    pass
