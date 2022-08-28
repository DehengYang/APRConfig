import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from utils import Dataframe_util
import Plot_util


cur_dir = os.path.dirname(os.path.abspath(__file__))
parse_result_dir = Plot_util.parse_result_dir
save_dir = Plot_util.save_dir

apr_name_dict = Plot_util.apr_name_dict
apr_name_list = Plot_util.apr_name_list

def add_compile_time(row):
    if row['apr'].startswith('simfix') or  row['apr'].startswith('tbar'):
        return float(row['pv_time']) + float(row['compile_time'])
    return float(row['pv_time'])

def statistical_tests(df_all):
    df_has_patch = df_all[df_all.has_patch == "yes"].copy()
    df_has_patch['fl_time'] = df_has_patch['fl_time'].astype(float)

    all_apr_df = pd.DataFrame()
    for apr in ['nopol', 'dynamoth', 'simfix', 'tbar']:
        apr_df = df_has_patch[df_has_patch.apr.str.startswith(apr)].copy()
        for bug in apr_df.bug.values:
            tmp_df = apr_df[apr_df.bug == bug]
            if tmp_df.shape[0]  > 3:
                print(tmp_df.to_string())

            if tmp_df.shape[0] != 3:
                apr_df.drop(tmp_df.index, inplace=True)
        
        all_apr_df = all_apr_df.append(apr_df)

    all_apr_df['repair_time'] = all_apr_df['repair_time'].astype(float) + all_apr_df['fl_time'].astype(float)
    all_apr_df['fl_time'] = all_apr_df['fl_time'].astype(float)
    all_apr_df['pg_time'] = all_apr_df['pg_time'].astype(float)
    all_apr_df['pv_time'] = all_apr_df['pv_time'].astype(float)

    all_apr_df['pv_time'] = all_apr_df['pv_time'].astype(float)
    all_apr_df['pv_time'] = all_apr_df.apply(lambda row:add_compile_time(row), axis = 1)

    all_apr_df['pg_time'] = all_apr_df['repair_time'].astype(float) - all_apr_df['fl_time']  - all_apr_df['pv_time'] #

    # all_apr_df = all_apr_df.round({'repair_time': 2, 'fl_time': 2, 'pg_time': 2, 'pv_time': 2})
    Dataframe_util.save_df_str(os.path.join(parse_result_dir, 'all_apr_df.csv'), all_apr_df[['apr', 'bug', 'repair_time',
        'fl_time', 'pg_time', 'pv_time', 'machine']])
    # raise Exception

    all_apr_df['fl_time'] = all_apr_df['fl_time']/all_apr_df['repair_time']
    all_apr_df['pv_time'] = all_apr_df['pv_time']/all_apr_df['repair_time']
    all_apr_df['pg_time'] = all_apr_df['pg_time']/all_apr_df['repair_time']
    all_apr_df['fl_pg_time'] = all_apr_df['fl_time'] + all_apr_df['pg_time']

    grouped_all_apr_df = pd.DataFrame(columns=['apr', 'bug', 'Proportion', 'stage'])
    for index, row in all_apr_df.iterrows():
        grouped_all_apr_df.loc[grouped_all_apr_df.shape[0]] = [row['apr'], row['bug'],row['pv_time'], 'Patch validation']
        grouped_all_apr_df.loc[grouped_all_apr_df.shape[0]] = [row['apr'], row['bug'],row['fl_pg_time'], 'Other']
        # grouped_all_apr_df.loc[grouped_all_apr_df.shape[0]] = [row['apr'], row['bug'],row['pg_time'], 'Patch generation']
    
    apr_label_dict = {}
    cnt = 1
    order_list = []
    for apr in ['nopol', 'dynamoth', 'simfix', 'tbar']:
        apr_label_dict[f'{apr}_1'] = f"${apr_name_dict[apr]}_s$"
        apr_label_dict[f'{apr}_2'] = f"${apr_name_dict[apr]}_p$"
        apr_label_dict[f'{apr}_3'] = f"${apr_name_dict[apr]}_n$"
        order_list.extend([apr_label_dict[f'{apr}_1'], apr_label_dict[f'{apr}_2'], apr_label_dict[f'{apr}_3']])
        # apr_label_dict[f'{apr}_1'] = cnt 
        # cnt += 1 
        # apr_label_dict[f'{apr}_2'] = cnt
        # cnt += 1 
        # apr_label_dict[f'{apr}_3'] = cnt
        # cnt += 2

    grouped_all_apr_df["apr"].replace(
        apr_label_dict,
        inplace=True)
    
    
    fig = plt.figure(figsize=(6, 6))
    Plot_util.set_theme(10)
    # sns.boxplot(y="apr", x="Proportion", hue="stage", data=grouped_all_apr_df, width=0.5, orient='h')
    # sns.boxplot(x="apr", y="Proportion", hue="stage", data=grouped_all_apr_df, width=0.5, orient='v')
    # positions=[1, 2, 3,     5,6,7,     9,10,11,   13,14,15]
    sns.boxplot(y='apr', x="Proportion", hue="stage", data=grouped_all_apr_df, width=0.6, orient='h',  order=order_list)
    # adjust_box_widths(fig, 0.9)
    ax = plt.gca() 
    # ax.tick_params(axis='x', rotation=30)
    plt.legend(title='', loc='upper center') #upper center
    # plt.ylabel("APR techniques")
    plt.ylabel("")

    # ax = plt.gca()  # Or get the axis another way
    # for artist in ax.artists:
    #     _reduce_box_width(artist, factor=.5)
    # horizontal_lines = [l for l in ax.lines
    #                     if len(l.get_path().vertices) != 0 and
    #                     l.get_path().vertices[0, 1] == l.get_path().vertices[1, 1]]
    # for line in horizontal_lines:
    #     _reduce_horizontal_line_width(line)
    # ax.redraw_in_frame()
    
    # df = grouped_all_apr_df
    # xvals = np.unique(df.apr)
    # positions = range(1, len(xvals) + 1)
    # plt.boxplot([df[df.apr == xi].percentage for xi in xvals],
    #         positions=positions, 
    #          medianprops={'color': 'black'}, 
    #         ) #widths=[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], patch_artist=True, showfliers=False, boxprops={'facecolor': 'none'},
    # means = [np.mean(df[df.apr == xi].percentage) for xi in xvals]
    # plt.plot(positions, means, '--k*', lw=2)

    plt.tight_layout()
    figure = plt.gcf()
    plt.show()
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    figure.savefig(os.path.join(save_dir, "reason_efficiency.pdf"), dpi=800)



def _reduce_box_width(artist, factor=.5):
    vertices = artist.get_path().vertices
    artist_width = vertices[1, 0] - vertices[0, 0]
    vertices[0, 0] += artist_width * (factor/2)
    vertices[1, 0] -= artist_width * (factor/2)
    vertices[2, 0] -= artist_width * (factor/2)
    vertices[3, 0] += artist_width * (factor/2)
    vertices[4, 0] += artist_width * (factor/2)



def _reduce_horizontal_line_width(artist, factor=.5):
    vertices = artist.get_path().vertices
    artist_width = vertices[1, 0] - vertices[0, 0]
    vertices[0, 0] += artist_width * (factor/2)
    vertices[1, 0] -= artist_width * (factor/2)



import numpy as np
from matplotlib.patches import PathPatch

def adjust_box_widths(g, fac):
    """
    Adjust the widths of a seaborn-generated boxplot.
    """

    # iterating through Axes instances
    for ax in g.axes:

        # iterating through axes artists:
        for c in ax.get_children():

            # searching for PathPatches
            if isinstance(c, PathPatch):
                # getting current width of box:
                p = c.get_path()
                verts = p.vertices
                verts_sub = verts[:-1]
                xmin = np.min(verts_sub[:, 0])
                xmax = np.max(verts_sub[:, 0])
                xmid = 0.5*(xmin+xmax)
                xhalf = 0.5*(xmax - xmin)

                # setting new width of box
                xmin_new = xmid-fac*xhalf
                xmax_new = xmid+fac*xhalf
                verts_sub[verts_sub[:, 0] == xmin, 0] = xmin_new
                verts_sub[verts_sub[:, 0] == xmax, 0] = xmax_new

                # setting new width of median line
                for l in ax.lines:
                    if np.all(l.get_xdata() == [xmin, xmax]):
                        l.set_xdata([xmin_new, xmax_new])

if __name__ == "__main__":
    df_all, _ = Plot_util.load_all_df()
    statistical_tests(df_all)