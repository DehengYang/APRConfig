from utils import File_util
import Config

import os


def get_bug_ids_from_txt(bug_ids_or_range_file_path):
    bug_ids = File_util.read_file_to_list_strip(bug_ids_or_range_file_path)
    lower_bug_ids = []
    for bug_id in bug_ids:
        lower_bug_ids.append(bug_id.lower())
    return lower_bug_ids


def split_bug_ids(bug_ids, total_split_cnt, cur_split_cnt):
    split_size = int(len(bug_ids) / total_split_cnt) + 1
    split_list = []
    for i in range(0, len(bug_ids), split_size):
        split_list.append(bug_ids[i:i + split_size])
    return split_list[cur_split_cnt - 1]


def get_bug_ids_path(dataset_name):
    path = os.path.join(Config.PROJECT_PATH, 'bugs_info', f'{dataset_name.lower()}.txt')
    return path