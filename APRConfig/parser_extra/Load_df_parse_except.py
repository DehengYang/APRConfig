"""
this script is to run after Main_parse

this is to find insufficient_memory cases.
"""

import pandas as pd
import os

from utils import Dataframe_util

cur_dir = os.path.dirname(os.path.abspath(__file__))


def get_insufficient_memory(df):
    # print(df.info())

    # df = df[df['insufficient_memory']=="YES"]
    df = df[df['insufficient_memory'] == "YES"]
    df = df[['apr', 'bug']]

    print(df.to_string(index=False))

    df["apr"].replace({
        "simfix_2": "simfix_1",
        "simfix_3": "simfix_1"
    },
                      inplace=True)
    df = df.drop_duplicates()  #subset=['apr']

    print(set(df.apr.values))
    # print(df[df.apr == "simfix_1"].shape)

    for value in set(df.apr.values):
        print(f"\n\n============== {value}:\n\n")
        print(df[df.apr == value]['bug'].to_string(index=False))


if __name__ == "__main__":
    df_path = os.path.join(cur_dir, "../..",
                           "results_defects4j/parser_results", "repair_df.csv")
    assert os.path.exists(df_path)
    df = Dataframe_util.read_csv(df_path)

    get_insufficient_memory(df)