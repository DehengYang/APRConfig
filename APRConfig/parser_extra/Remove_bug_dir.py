"""
remove bug project folder to save space and to prepare for data export/backup.
"""

import os, shutil

cur_dir = os.path.abspath(os.path.dirname(__file__))
result_d4j_dir = os.path.join(cur_dir, "../../results_defects4j")

for bug in os.listdir(result_d4j_dir):
    bug_path = os.path.join(result_d4j_dir, bug)
    if os.path.isdir(bug_path):
        bug_dir_path = os.path.join(bug_path, bug)
        if os.path.isdir(bug_dir_path):
            print(bug_dir_path)
            shutil.rmtree(bug_dir_path)