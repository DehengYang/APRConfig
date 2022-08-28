import os, re
import pandas as pd
import datetime

from utils import File_util, Time_util, Dataframe_util

cur_dir = os.path.dirname(os.path.abspath(__file__))

apr_tool_list = ['simfix', 'tbar', 'nopol', 'dynamoth']


def count_repair_time(result_dir):
    time_df = pd.DataFrame(columns=['apr_folder', 'repair_time'])
    for folder in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder)
        if not folder.startswith(f'{dataset_name}_'):
            continue

        for cur_folder in os.listdir(folder_path):
            cur_folder_path = os.path.join(folder_path, cur_folder)
            for apr in apr_tool_list:
                # '/home/apr/bias_validation_2021/execution_framework/result_processor/../../results_defects4j_processed/tbar_0'
                if cur_folder.startswith(apr):
                    exec_log = os.path.join(cur_folder_path,
                                            "execution_framework.log")
                    assert os.path.exists(exec_log)

                    lines = File_util.read_file_add_wrap(exec_log)
                    for line in lines:
                        # [2021-09-05 15:03:43] {Cmd_util.py:20} INFO - cmd to run:
                        match = re.findall(re.compile(r'\[(.*?)\] {'), line)
                        if len(match) > 0:
                            # start_time = time.strptime(match[0], "%Y-%m-%d %H:%M:%S")
                            start_time = datetime.datetime.strptime(
                                match[0], "%Y-%m-%d %H:%M:%S")
                            break
                    for i in range(len(lines) - 1, -1, -1):
                        line = lines[i]
                        match = re.findall(re.compile(r'\[(.*?)\] {'), line)
                        if len(match) > 0:
                            end_time = datetime.datetime.strptime(
                                match[0], "%Y-%m-%d %H:%M:%S")
                            break
                    time_cost = end_time - start_time
                    time_df.loc[time_df.shape[0]] = [cur_folder, time_cost]
        df_save_path = os.path.join(result_dir, 'parser_results',
                                    "repair_time_df.csv")
        Dataframe_util.write_csv(df_save_path, time_df)


if __name__ == "__main__":
    Time_util.update_start_time()

    dataset_name = 'defects4j'

    # /home/apr/bias_validation_2021/execution_framework/parser
    # /home/apr/bias_validation_2021/results_defects4j
    result_dir = os.path.join(cur_dir, f'../../results_{dataset_name}')
    assert os.path.exists(result_dir)

    count_repair_time(result_dir)

    Time_util.cal_time_cost()