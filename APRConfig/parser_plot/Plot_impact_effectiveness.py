import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from venn import venn
import xlsxwriter

from utils import Dataframe_util, File_util
import Plot_util

cur_dir = os.path.dirname(os.path.abspath(__file__))
parse_result_dir = Plot_util.parse_result_dir
save_dir = Plot_util.save_dir

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list

# cnt = 0


def plot(df_all_filter_final):
    df_has_patch = df_all_filter_final[df_all_filter_final.has_patch ==
                                       "yes"].copy()
    has_patch_dict = {}
    for apr in apr_name_list:
        for validate_mode in range(1, 4):
            repaired_bugs = set(df_has_patch[df_has_patch.apr == f"{apr}_{validate_mode}"].bug.values)
            has_patch_dict[f'{apr}_{validate_mode}'] = repaired_bugs

    save_to_file(df_has_patch)
    
    # print(has_patch_dict)
    plot_venn(has_patch_dict)
    # plot_boxplot_pv12_3_diff(has_patch_dict, df_all_filter_final)
    # plot_boxplot_pv12_diff(has_patch_dict, df_all_filter_final)
    # plot_boxplot_ncp_intersection(has_patch_dict, df_all_filter_final)
    # global cnt
    # print("cnt: ", cnt)

def plot_boxplot_ncp_intersection(has_patch_dict, df_all_filter_final):
    ncp_df = pd.DataFrame(columns=['apr', 'bug', 'ncp'])

    # for apr in apr_name_list:
    for apr in ['nopol', 'dynamoth']:
        apr_1 = has_patch_dict[f"{apr}_1"]
        apr_2 = has_patch_dict[f"{apr}_2"]
        apr_3 = has_patch_dict[f"{apr}_3"]
        same = apr_1 & apr_2 & apr_3
        print(len(same))
        for bug in same:
            ncp_1 = get_ncp(df_all_filter_final, apr, bug, 1)
            ncp_2 = get_ncp(df_all_filter_final, apr, bug, 2)
            ncp_3 = get_ncp(df_all_filter_final, apr, bug, 3)
            if isinstance(ncp_1, int) and isinstance(ncp_2, int) and isinstance(ncp_3, int) and ncp_1 == ncp_2 and ncp_2 == ncp_3:
                ncp_df.loc[ncp_df.shape[0]] = [apr, bug, ncp_1]
                print(f"bug: {bug} apr: {apr}, ncp1: {ncp_1}, ncp2: {ncp_2}, ncp3: {ncp_3}") 
            else:
                pass
                # print(f"bug: {bug} apr: {apr}, ncp1: {ncp_1}, ncp2: {ncp_2}, ncp3: {ncp_3}") 
    
    ncp_df["apr"].replace(
        apr_name_dict,
        inplace=True)

    Plot_util.set_theme()
    plt.figure(figsize=(6, 6))  #figsize=(9, 6)
    ax = sns.boxplot(x='apr', y='ncp', data=ncp_df) #, orient = 'h'
    ax.set_xlabel("APR Techniques")
    ax.set_ylabel("NCP")

    plt.tight_layout()
    figure = plt.gcf()
    plt.show()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    figure.savefig(os.path.join(save_dir, "ncp_dist.pdf"), dpi=800)


def save_to_file(df_has_patch):
    wb = xlsxwriter.Workbook(os.path.join(save_dir, 'patches.xlsx'))
    worksheet = wb.add_worksheet()
    
    col = 0
    for apr in apr_name_list:
        for i in range(1, 4):
            col += 1
            worksheet.write(0, col, f"{apr}_{i}")
    
    # start point
    row = 1
    df_has_patch.sort_values(['bug','apr'], inplace=True)
    duplicate_bugs = []
    for bug in list(df_has_patch.bug.values):
        col = 0
        if bug in duplicate_bugs:
            continue
        else:
            duplicate_bugs.append(bug)
        worksheet.write(row, col, bug)
        for apr in apr_name_list:
            for i in range(1, 4):
                tmp_df = df_has_patch[(df_has_patch.bug == bug) & (df_has_patch.apr.str.startswith(f"{apr}_{i}"))]
                if tmp_df.shape[0] > 1:
                    assert False
                col += 1
                if tmp_df.shape[0] > 0:
                    if Plot_util.dataset_name == 'quixbugs':
                        worksheet.write(row, col, "yes")
                    else:
                        worksheet.write(row, col, f"{tmp_df.machine.values}")
        row+= 1
    wb.close()


def plot_boxplot_pv12_diff(has_patch_dict, df_all_filter_final):
    ncp_diff_df = pd.DataFrame(columns=['apr', 'bug', 'ncp_diff', 'pv'])

    for apr in ['simfix', 'tbar']:  #['nopol']:
        apr_1 = has_patch_dict[f"{apr}_1"]
        apr_2 = has_patch_dict[f"{apr}_2"]
        diff_12 = apr_1 - apr_2
        diff_21 = apr_2 - apr_1

        for bug in diff_12:
            ncp_1 = get_ncp(df_all_filter_final, apr, bug, 1)
            ncp_2 = get_ncp(df_all_filter_final, apr, bug, 2)
            ncp_diff = ncp_1 - ncp_2
            # TODO: resolve this error!
            # if ncp_diff > 1000 or ncp_diff <= 1:
            #     print(apr, bug, ncp_diff)
            #     continue
            ncp_diff_df.loc[ncp_diff_df.shape[0]] = [apr, bug, ncp_diff,'pv12']
        for bug in diff_21:
            ncp_1 = get_ncp(df_all_filter_final, apr, bug, 1)
            ncp_2 = get_ncp(df_all_filter_final, apr, bug, 2)
            ncp_diff = ncp_2 - ncp_1
            # TODO: resolve this error!
            # if ncp_diff > 1000 or ncp_diff <= 1:
            #     print(apr, bug, ncp_diff)
            #     continue
            ncp_diff_df.loc[ncp_diff_df.shape[0]] = [apr, bug, ncp_diff,'pv21']
    print(ncp_diff_df.to_string())
        
def get_ncp(df_all_filter_final, apr, bug, mode):

    row = df_all_filter_final.loc[
                (df_all_filter_final.apr == f'{apr}_{mode}')
                & (df_all_filter_final.bug == bug)]
    # print(row.to_string())
    if row.shape[0] > 1:
        row = row.iloc[0]
        # print(row.to_string())
        # raise Exception()
        # global cnt
        # cnt += 1
        # print("cnt: ", cnt)

    try:
        return int(row['ncp'])
    except:
        return row['ncp']

def plot_boxplot_pv12_3_diff(has_patch_dict, df_all_filter_final):
    ncp_diff_df = pd.DataFrame(columns=['apr', 'bug', 'ncp_diff'])
    
    for apr in ['simfix', 'tbar']:
        apr_1 = has_patch_dict[f"{apr}_1"]
        apr_2 = has_patch_dict[f"{apr}_2"]
        apr_3 = has_patch_dict[f"{apr}_3"]

        # compare 1,2 & 3
        diff_1 = apr_1 - apr_3
        diff_2 = apr_2 - apr_3 - apr_1

        for bug in diff_1:
            ncp_1 = get_ncp(df_all_filter_final, apr, bug, 1)
            ncp_3 = get_ncp(df_all_filter_final, apr, bug, 3)
            ncp_diff = ncp_1 - ncp_3
            # TODO: resolve this error!
            # if ncp_diff <= 0:
            #     print(apr, bug, ncp_diff)
            #     continue
            ncp_diff_df.loc[ncp_diff_df.shape[0]] = [apr, bug, ncp_diff]
        for bug in diff_2:
            ncp_2 = get_ncp(df_all_filter_final, apr, bug, 2)
            ncp_3 = get_ncp(df_all_filter_final, apr, bug, 3)
            ncp_diff = ncp_2 - ncp_3
            # if ncp_diff <= 0:
            #     print(apr, bug, ncp_diff)
            #     continue
            ncp_diff_df.loc[ncp_diff_df.shape[0]] = [apr, bug, ncp_diff]

    print(ncp_diff_df.to_string())
    # return

    ncp_diff_df["apr"].replace(
        apr_name_dict,
        inplace=True)

    font_size = Plot_util.FONT_SIZE
    sns.set_theme(style="darkgrid",
                  font=Plot_util.FONT,
                  palette='muted', ## deep, muted, bright, pastel, dark, colorblind
                  rc={
                      'font.size': font_size,
                      'axes.labelsize': font_size,
                      'axes.titlesize': font_size,
                      'xtick.labelsize': font_size,
                      'ytick.labelsize': font_size,
                      'legend.fontsize': font_size
                  })
    plt.figure(figsize=(5, 6))  #figsize=(9, 6)
    ax = sns.boxplot(x='apr', y='ncp_diff', data=ncp_diff_df) #, orient = 'h'
    ax.set_xlabel("APR Techniques")
    ax.set_ylabel("$\Delta_{patch}$")

    medians = ncp_diff_df.groupby('apr')['ncp_diff'].median()
    means = ncp_diff_df.groupby('apr')['ncp_diff'].mean()
    print(medians)
    for i in range(len(medians)):
        ax.text(i,
                medians[i] + 50,
                "Median: {:.1f}".format(medians[i]),
                ha="center",
                fontsize=14,
                fontfamily='Arial')
        ax.text(i,
                medians[i] - 150,
                "Mean: {:.1f}".format(means[i]),
                ha="center",
                fontsize=14,
                fontfamily='Arial')

    plt.tight_layout()
    figure = plt.gcf()
    plt.show()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    figure.savefig(os.path.join(save_dir, "ncp_diff_pv12_3.pdf"), dpi=800)


def plot_venn(has_patch_dict):
    # plot venn graphs
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(20, 20))  #
    ax_list = []
    for row in axes:
        for col in row:
            ax_list.append(col)

    for i in range(len(apr_name_list)):
        apr = apr_name_list[i]
        apr_1 = has_patch_dict[f"{apr}_1"]
        apr_2 = has_patch_dict[f"{apr}_2"]
        apr_3 = has_patch_dict[f"{apr}_3"]
        paired_dict = {}
        paired_dict['mode_1'] = apr_1
        paired_dict['mode_2'] = apr_2
        paired_dict['mode_3'] = apr_3

        if apr == 'simfix':
            print(apr_3-apr_2)    

        # print(f"{apr} union: {len(new_fixed | original_fixed)}")
        # print(f"{apr} intersection: {len(new_fixed & original_fixed)}")
        # print(f"{apr} diff (apr_1): {apr_1 & apr_3 - apr_2}\n") # simfix
        # print(f"{apr} diff (apr_1): {apr_1 - apr_3}\n") # dynamoth&nopol
        # print(f"{apr} diff (apr_2): {apr_1 & apr_2 - apr_3}")

        ax = ax_list[i]
        print(apr, paired_dict)

        if len(paired_dict['mode_1'])  == 0 and len(paired_dict['mode_2'])  == 0 and len(paired_dict['mode_3'])  == 0:
            continue

        venn(paired_dict, ax=ax, legend_loc='best', figsize=(
            12, 12
        ))  #,fontsize= Plot_util.FONT_SIZE ,figsize=(15,15) ,figsize=(6, 6)
        ax.set_title(f"{apr_name_dict[apr]}")
        # plt.title(f"Number of Fixed Bugs by {apr_name_dict[apr]}")

    figure = plt.gcf()
    plt.show()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    figure.savefig(os.path.join(save_dir, "venn_effectiveness.jpg"), dpi=800)


if __name__ == "__main__":
    df_all_filter_final, _ = Plot_util.load_all_df() #'quixbugs' #defects4j
    plot(df_all_filter_final)
