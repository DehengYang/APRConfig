import os

import Main_dataset_util, Config
from utils import Dir_util, Dataset_util, File_util

cur_dir = Dir_util.get_cur_dir(__file__)

File_util.rm_file(Config.log_file)

# 
# Config.debug_dataset_module = True

total_split_cnt = 8
cur_split_cnt = 1
tool_name_list = ['tbar_2'] # 'nopol_1', 'nopol_2', 'nopol_3', 'dynamoth_1', 'dynamoth_2', 'dynamoth_3'
dataset_name = "bears"

if __name__ == "__main__":
    localizer_name = "gzoltar"
    bug_ids_or_range_file_path = Dataset_util.get_bug_ids_path(dataset_name)

    Config.TMP_OUTPUT_DIR = os.path.join(Config.PARENT_PROJECT_PATH, f"results_{dataset_name}")

    bug_ids = Dataset_util.get_bug_ids_from_txt(bug_ids_or_range_file_path)
    bug_ids = Dataset_util.split_bug_ids(bug_ids, total_split_cnt, cur_split_cnt)

    bug_ids = ['INRIA-spoon_210079209-210080599']

    Main_dataset_util.retry_clean_dir(tool_name_list, dataset_name, localizer_name, bug_ids, retry=False)
    Main_dataset_util.run_dataset(tool_name_list, dataset_name, localizer_name, bug_ids)
