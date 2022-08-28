import os
from numpy import true_divide
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from utils import Dataframe_util, File_util
import Plot_util

cur_dir = os.path.dirname(os.path.abspath(__file__))
parse_result_dir = Plot_util.parse_result_dir
save_dir = Plot_util.save_dir

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list

def analyze_apr_df(apr_df, apr):
    for bug in set(apr_df.bug.values):
        repair_time_list = []
        for i in range(0, 3):
            repair_time_list.append(apr_df[(apr_df.bug == bug) & (apr_df.apr == f"{apr}_{i+1}")]['repair_time'].values)
        # print(apr, bug)
        print(apr, bug, repair_time_list[0], repair_time_list[1], repair_time_list[2])


def plot(df_all_filter_final):
    df_has_patch = df_all_filter_final[df_all_filter_final.has_patch ==
                                       "yes"].copy()
    df_has_patch['repair_time'] = df_has_patch['repair_time'].astype(float) + df_has_patch['fl_time'].astype(float)
    # print(df_has_patch['repair_time'].values[:3])
    
    """
    for each APR, consider&plot the intersection of the three strategies first.
    """
    all_apr_df = pd.DataFrame()
    for apr in apr_name_list:

        if Plot_util.dataset_name == 'quixbugs':
            if apr.lower() in ['nopol', 'dynamoth']:
                continue

        apr_df = df_has_patch[df_has_patch.apr.str.startswith(apr)].copy()
        for bug in apr_df.bug.values:
            tmp_df = apr_df[apr_df.bug == bug]
            if tmp_df.shape[0] != 3:
                indexes = tmp_df.index
                # print(type(indexes), indexes)
                apr_df.drop(indexes, inplace=True)
            # else:
            #     print(apr, bug)

        apr_df['repair_time'] = apr_df['repair_time'].astype(float)
        analyze_apr_df(apr_df, apr)

        print(apr, apr_df.shape[0]/3)
        all_apr_df = all_apr_df.append(apr_df)
    
    all_apr_df['repair_time'] = all_apr_df['repair_time'].astype(float)
    all_apr_df = all_apr_df.sort_values(['bug', 'apr', 'repair_time']) #, 'bug', 'apr'
    Dataframe_util.write_csv(os.path.join(parse_result_dir, 'all_apr_df.csv'), all_apr_df)
    
    # raise Exception

    # sort
    all_apr_df.sort_values('apr', inplace=True)

    # covert from string to int
    all_apr_df['Repair Time'] = all_apr_df['repair_time'].astype(float)
    all_apr_df['NCP'] = all_apr_df['ncp'].astype(int)
    all_apr_df['NTCE'] = all_apr_df['ntce'].astype(int)
    # all_apr_df['repair_time'] = pd.to_numeric(all_apr_df['repair_time'], errors='coerce')
    # print(all_apr_df.repair_time.values)

    all_apr_df['Validation Strategy'] = all_apr_df.apply(
        lambda row: pv_label(row), axis=1)
    all_apr_df['apr_name'] = all_apr_df.apply(lambda row: apr_name_label(row),
                                              axis=1)
    # all_apr_df_melt = pd.melt(all_apr_df, "pv_type", var_name="apr", value_name="repair_time")
    # print(all_apr_df_melt.to_string())

    font_size = Plot_util.FONT_SIZE
    sns.set_theme(
        style="darkgrid",
        font=Plot_util.FONT,
        palette='muted',  ## deep, muted, bright, pastel, dark, colorblind
        rc={
            'font.size': font_size,
            'axes.labelsize': font_size,
            'axes.titlesize': font_size,
            'xtick.labelsize': font_size,
            'ytick.labelsize': font_size,
            'legend.fontsize': 10
        })
    for y in ['Repair Time']: #, 'NCP', 'NTCE'
        plt.figure()  #figsize=(9, 6) figsize=(10, 10)
        ax = sns.boxplot(x='apr_name',
                         y=y,
                         hue="Validation Strategy",
                         data=all_apr_df,
                         showfliers=True)  #, orient = 'h'
        ax.set_xlabel("APR Techniques")
        ax.set_ylabel(y)
        ax.legend().set_title(None)

        plt.tight_layout()
        figure = plt.gcf()
        plt.show()
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        figure.savefig(os.path.join(save_dir, "repair_time.pdf"), dpi=800)


def pv_label(row):
    mode = int(row['apr'].split("_")[-1])
    if mode == 1:
        return 'selection'
    elif mode == 2:
        return 'prioritization'
    elif mode == 3:
        return 'naive'
    else:
        raise Exception
    # return 'pv_' + row['apr'].split("_")[-1]


def apr_name_label(row):
    return apr_name_dict[row['apr'].split("_")[0]]


if __name__ == "__main__":
    df_all_filter_final, rta_df = Plot_util.load_all_df()
    plot(df_all_filter_final)
