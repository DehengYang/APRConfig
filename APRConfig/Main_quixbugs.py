import os

import Main_dataset_util, Config

bug_range = [0,10]

if __name__ == "__main__":
    tool_name_list = ['tbar_2'
                      ]  # 'nopol_1', 'dynamoth_1', 'simfix_0', 'tbar_0'
    dataset_name = "quixbugs"
    localizer_name = "gzoltar"
    Config.TMP_OUTPUT_DIR = os.path.join(Config.PARENT_PROJECT_PATH,
                                         f"results_{dataset_name}")

    Main_dataset_util.retry_clean_dir(tool_name_list,
                                  dataset_name,
                                  localizer_name,
                                  bug_range,
                                  False,
                                  bug_info_extra_name=True,
                                  retry=True)
    Main_dataset_util.run_dataset(tool_name_list,
                                  dataset_name,
                                  localizer_name,
                                  bug_range,
                                  False,
                                  bug_info_extra_name=True)

