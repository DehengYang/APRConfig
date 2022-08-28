import apr
from utils import Cmd_util, File_util
import Main_util, Config

import os, logging

logger = logging.getLogger()


def run_single_bug():
    tool_name = 'deptest'
    dataset_name = 'defects4j'
    localizer_name = 'gzoltar'
    bug_id = "Chart_5"

    # rename output dir
    Config.TMP_OUTPUT_DIR = Config.TMP_OUTPUT_DIR + f"_{dataset_name}"
    dataset = Main_util.get_dataset(dataset_name)
    bug = dataset.get_bug(bug_id)

    apr_dir = os.path.join(Config.TMP_OUTPUT_DIR, bug.name, tool_name)
    if os.path.isdir(apr_dir):
        File_util.rm_dir_safe_contain(apr_dir, f'{tool_name}')

    Main_util.run_single_bug(tool_name, dataset_name, localizer_name, dataset,
                             bug)


if __name__ == "__main__":
    run_single_bug()