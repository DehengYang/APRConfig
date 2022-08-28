from matplotlib import pyplot as plt
import numpy as np
import os
import seaborn as sns

from utils import Dataframe_util

cur_dir = os.path.dirname(os.path.abspath(__file__))
d4j_parse_result_dir = os.path.abspath(os.path.join(cur_dir, "..", "..", "results_defects4j"))
quixbugs_parse_result_dir = os.path.abspath(os.path.join(cur_dir, "..", "..", "results_quixbugs", "parsed_results/"))

dataset_name = 'defects4j' # quixbugs defects4j
if dataset_name == 'quixbugs':
    parse_result_dir = quixbugs_parse_result_dir
elif dataset_name == 'defects4j':
    parse_result_dir = d4j_parse_result_dir
save_dir = os.path.abspath(os.path.join(cur_dir, "..", "..", "figs"))
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

apr_name_dict = {
    "nopol": "Nopol",
    "dynamoth": "DynaMoth",
    'simfix': "SimFix",
    "tbar": "TBar"
}
apr_name_list = ['simfix', 'tbar', 'nopol', 'dynamoth']

FONT_SIZE = 14
FONT = 'DejaVu Sans'  # Helvetica
PALETTE = 'muted'  # deep, muted, bright, pastel, dark, colorblind

exceptions = [
    # only dynamoth 2 can generate a patch, dyn1 timeout, and dyn2 directly passed(with no patch found).
    ['dynamoth', 'Math_74'],  
    # timeout exception in simfix_1_select  machine 2 /home/apr/bias_validation_2021/results_defects4j/defects4j_Math_61/simfix_1/validate/279_select.txt.log
    ['simfix', 'Math_61'],
    # NullPointerException  machine 4 /home/apr/bias_validation_2021/results_defects4j/defects4j_Closure_88/simfix_1/validate/1951_prioritize.txt.log  simfix 2 has patch but with exception
    ['simfix', 'Closure_88'],
    # timeout exception /home/apr/bias_validation_2021/results_defects4j/defects4j_Mockito_22/tbar_2/validate/1136_select.txt.log machine 1  tbar 
    ['tbar', 'Mockito_22'],
    # Can't test IS_JAVA value  error. /home/apr/bias_validation_2021/results_defects4j/defects4j_Lang_55/tbar_1/patch2.txt
    ['tbar', 'Lang_55'],
    # TimeoutException  /home/apr/bias_validation_2021/results_defects4j/defects4j_Closure_16/tbar_1/validate/2263_select.txt.log machine 2
    ['tbar', 'Closure_16'],
    # exception in validation of simfix3 
    ['simfix_3', 'Mockito_37', 1],

    # duplicates!
    ['nopol_1', 'Time_11', 1],
    ['nopol_3', 'Time_11', 4],
    ['nopol_3', 'Time_14', 4],
    ['nopol_3', 'Closure_3', 4],
    ['nopol_3', 'Closure_5', 4],
    ['nopol_1', 'Math_69', 2],
    ['nopol_1', 'Math_80', 2],
    ['nopol_3', 'Closure_127', 4],
    ['nopol_1', 'Closure_3', 4],
    ['dynamoth_1', 'Mockito_34', 2],
    ['dynamoth_1', 'Closure_48', 3],
    ['dynamoth_2', 'Chart_9', 3],
    ['dynamoth_1', 'Chart_9', 1],
    ['dynamoth_1', 'Mockito_38', 1],
    ['dynamoth_1', 'Chart_9', 3],
    ['dynamoth_3', 'Chart_9', 3],
#     Time_14 nopol
# Math_69 nopol
# Closure_3 nopol
# Closure_5 nopol


    # deleted the folder in corresponding machine. because original (e.g., tbar0) is right
    # 3330,tbar_1,tbar_1,defects4j,Math_15,374.823,353.723,0,45.59099999999999,325.65999999999997,46,16940,yes,NO,NO,,NO,NO,3
    # 5007,tbar_1,tbar_2,defects4j,Mockito_8,644.3110000000001,22.336000000000002,0,542.9090000000002,96.31599999999992,683,1682,yes,NO,NO,,NO,NO,1

    
]


def set_theme(legend_font_size=FONT_SIZE):
    font_size = FONT_SIZE
    sns.set_theme(
        style="darkgrid",
        font=FONT,
        palette='muted',  ## deep, muted, bright, pastel, dark, colorblind
        rc={
            'font.size': font_size,
            'axes.labelsize': font_size,
            'axes.titlesize': font_size,
            'xtick.labelsize': font_size,
            'ytick.labelsize': font_size,
            'legend.fontsize': legend_font_size
        })


def show_values_on_bars(axs):
    def _show_on_single_plot(ax):
        for p in ax.patches:
            _x = p.get_x() + p.get_width() / 2
            _y = p.get_y() + p.get_height() + 1
            # value = '{:.2f}'.format(p.get_height())
            value = '{:.0f}'.format(p.get_height())
            ax.text(_x,
                    _y,
                    value,
                    ha="center",
                    fontsize=FONT_SIZE,
                    fontfamily=FONT)

    if isinstance(axs, np.ndarray):
        for idx, ax in np.ndenumerate(axs):
            _show_on_single_plot(ax)
    else:
        _show_on_single_plot(axs)


def load_all_df(parse_result_dir=parse_result_dir):
    if dataset_name == 'defects4j':
        merge_dir = os.path.join(parse_result_dir, 'merge')
        df_all_filter_final = Dataframe_util.read_csv(
            os.path.join(merge_dir, 'df_all_filter_final.csv'))
        
        df_all_filter_final = exclude_exceptions(df_all_filter_final)

        # 1)
        df =  df_all_filter_final[df_all_filter_final.vm_error == 'YES']
        print(df.shape)
        df_all_filter_final.loc[df_all_filter_final.vm_error == 'YES', 'has_patch'] = 0

        # 2) replace
        df_all_filter_final['filter_pass_file'] = df_all_filter_final['filter_pass_file'].replace(np.nan, '-')
        # df_all_filter_final['filter_pass_file'] = df_all_filter_final['filter_pass_file'].astype(int)
        df_all_filter_final.loc[df_all_filter_final.apr.str.startswith('simfix')  & (df_all_filter_final.filter_pass_file != '-'), 'ncp'] = df_all_filter_final['filter_pass_file']
        # print( df_all_filter_final['filter_pass_file'])
        df_all_filter_final.loc[df_all_filter_final.apr.str.startswith('tbar')  & (df_all_filter_final.filter_pass_file != '-'), 'ncp'] = df_all_filter_final['filter_pass_file']

        rta_df = Dataframe_util.read_csv(os.path.join(merge_dir, 'rta_df.csv'))
    elif dataset_name == 'quixbugs':
        df_all_filter_final = Dataframe_util.read_csv(
            os.path.join(parse_result_dir, 'repair_df.csv'))
        rta_df = None

    print("df_all_filter_final:", df_all_filter_final.shape)
    
    # write
    # df_all_filter_final = df_all_filter_final.sort_values(['bug', 'apr'])
    # Dataframe_util.write_csv(os.path.join(parse_result_dir, 'df_sort.csv'), df_all_filter_final)

    return df_all_filter_final, rta_df

def exclude_exceptions(df_all_filter_final):
    print("current exceptions:", len(exceptions))

    for exp in exceptions:
        if len(exp) == 2:
            tool_name = exp[0]
            bug = exp[1]
            if "_" not in tool_name:
                df_all_filter_final = df_all_filter_final.drop( df_all_filter_final.loc[ (df_all_filter_final.apr.str.startswith(tool_name)) & (df_all_filter_final.bug == bug) ].index)
        if len(exp) == 3:
            tool_name = exp[0]
            bug = exp[1]
            machine = exp[2]
            if "_" in tool_name:
                df_all_filter_final = df_all_filter_final.drop( df_all_filter_final.loc[ (df_all_filter_final.apr == tool_name) & (df_all_filter_final.bug == bug) & (df_all_filter_final.machine == machine)].index)
    
    return df_all_filter_final

def load_literature_data(rta_df):
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


def save_df(df, save_path):
    df.to_csv(save_path)


def restore_df(save_path):
    return Dataframe_util.read_csv(save_path)