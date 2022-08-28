"""
repairthemall: rta for short
"""

import os
import pandas as pd

from utils import Json_util

repairthemall_dir = os.path.expanduser(
    "~/tools/RepairThemAll_experiment/results")
dataset = "Defects4J"  # QuixBugs


def parse_result(repairthemall_dir=repairthemall_dir, dataset=dataset):
    rta_df = pd.DataFrame(columns=['apr', 'dataset', 'bug'])
    dataset_dir = os.path.join(repairthemall_dir, dataset)
    for proj in os.listdir(dataset_dir):
        proj_dir = os.path.join(dataset_dir, proj)
        if not os.path.isdir(proj_dir):
            continue

        for id in os.listdir(proj_dir):
            id_dir = os.path.join(proj_dir, id)
            if not os.path.isdir(id_dir):
                continue

            for apr in ['Nopol', 'DynaMoth']:
                apr_dir = os.path.join(id_dir, apr)
                assert os.path.isdir(apr_dir)

                for seed in os.listdir(apr_dir):
                    seed_dir = os.path.join(apr_dir, seed)

                    if not os.path.isdir(seed_dir):
                        assert False
                        # continue

                    result_json_file = os.path.join(seed_dir, "result.json")
                    if not os.path.exists(result_json_file):
                        continue
                    result_dict = Json_util.read_json(result_json_file)
                    if len(result_dict['patches']) > 0:
                        # print(f"{apr} {proj} {id} {result_dict['patches']}")
                        # print(f"{apr} {proj} {id}")
                        rta_df.loc[rta_df.shape[0]] = [
                            apr.lower(), dataset, f'{proj}_{id}'
                        ]
    rta_df.sort_values(['apr', 'bug'], inplace=True)
    rta_df.reset_index(inplace=True, drop=True)
    # print(rta_df.to_string())

    return rta_df


if __name__ == "__main__":
    parse_result(repairthemall_dir, dataset)
