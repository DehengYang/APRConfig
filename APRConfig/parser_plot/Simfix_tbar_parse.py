import os
import pandas as pd

cur_dir = os.path.dirname(os.path.abspath(__file__))
simfix_dir = os.path.join(cur_dir, "../../apr_tools/SimFix/final/result/patch")
tbar_dir = os.path.join(
    cur_dir, "../../apr_tools/TBar/Results/NormalFL/TBar/FixedBugs/")


def parse_simfix_result(simfix_dir=simfix_dir):
    simfix_df = pd.DataFrame(columns=['apr', 'dataset', 'bug'])
    for proj in os.listdir(simfix_dir):
        proj_dir = os.path.join(simfix_dir, proj)
        if not os.path.isdir(proj_dir):
            continue
        for id in os.listdir(proj_dir):
            simfix_df.loc[simfix_df.shape[0]] = [
                'simfix', 'defects4j', f"{proj.capitalize()}_{id}"
            ]
    simfix_df.sort_values('bug', inplace=True)
    simfix_df.reset_index(inplace=True, drop=True)
    simfix_df.drop_duplicates(subset="bug", inplace=True)
    return simfix_df


def parse_tbar_result(tbar_dir=tbar_dir):
    tbar_df = pd.DataFrame(columns=['apr', 'dataset', 'bug'])
    for file in os.listdir(tbar_dir):
        if not os.path.isdir(os.path.join(tbar_dir, file)):
            continue
        if file.endswith("_P"):
            file = file[:-2]
        tbar_df.loc[tbar_df.shape[0]] = ['tbar', 'defects4j', file]
    tbar_df.sort_values('bug', inplace=True)
    tbar_df.reset_index(inplace=True, drop=True)
    return tbar_df


if __name__ == "__main__":
    simfix_df = parse_simfix_result(simfix_dir)
    print(simfix_df['bug'].to_string())

    tbar_df = parse_tbar_result(tbar_dir)
    print(tbar_df.to_string())