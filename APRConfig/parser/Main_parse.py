import os, logging
import Nopol_parser
from utils import File_util, Logging_util
import pandas as pd
import numpy as np

import Main_util, Config
import Parser_factory

logger = logging.getLogger()


def add_row(is_complete_flag, repair_df, data_dict, tool_name, dataset_name,
            bug):
    if is_complete_flag:
        assert data_dict['has_patch1'] <= 1 and data_dict[
            'has_patch2'] <= 1 and data_dict['has_patch3'] <= 1
        if data_dict['has_patch1'] == 1:
            data_dict['has_patch1'] = "yes"
        if data_dict['has_patch2'] == 1:
            data_dict['has_patch2'] = "yes"
        if data_dict['has_patch3'] == 1:
            data_dict['has_patch3'] = "yes"

        if tool_name in [
                'nopol_1', 'nopol_2', 'nopol_3', 'dynamoth_1', 'dynamoth_2',
                'dynamoth_3'
        ]:
            validate_mode = tool_name.split("_")[1]

            repair_df.loc[repair_df.shape[0]] = [
                tool_name, tool_name, dataset_name,
                bug.get_proj_id(), data_dict['time_cost'],
                data_dict['fl_time'], data_dict['pg_time_' + validate_mode],
                data_dict['compile_time'],
                data_dict['time_cost' + validate_mode],
                data_dict['ncp' + validate_mode],
                data_dict['ntce' + validate_mode],
                data_dict['has_patch' + validate_mode],
                data_dict['insufficient_memory'], data_dict['filter_pass_all'], data_dict['filter_pass_all_flag'],
                data_dict['insufficient_memory_2'], '-', # not detect now.
                data_dict['repeated_timeout_executions_' + validate_mode]
            ]
        # if tool_name in ['simfix_0', 'simfix_1', 'tbar_0', 'tbar_1']:
        else:
            for validate_mode in range(1, 4):
                validate_mode = str(validate_mode)
                repair_df.loc[repair_df.shape[0]] = [
                    tool_name,
                    tool_name.split("_")[0] + "_" + validate_mode,
                    dataset_name,
                    bug.get_proj_id(), data_dict['pg_time_' + validate_mode] +
                    data_dict['time_cost' + validate_mode] +
                    data_dict['compile_time' + validate_mode],
                    data_dict['fl_time'], data_dict['pg_time'],
                    data_dict['compile_time' + validate_mode],
                    data_dict['time_cost' + validate_mode],
                    data_dict['ncp' + validate_mode],
                    data_dict['ntce' + validate_mode],
                    data_dict['has_patch' + validate_mode],
                    data_dict['insufficient_memory'],
                    data_dict['filter_pass_all' + validate_mode], data_dict['filter_pass_all_flag' + validate_mode],
                    data_dict['insufficient_memory_2'], data_dict[f'vm_error_{validate_mode}'],
                    data_dict['repeated_timeout_executions_' + validate_mode]
                ]
    else:
        repair_df.loc[repair_df.shape[0]] = [
            tool_name, tool_name, dataset_name,
            bug.get_proj_id()
        ] + ['-'] * (repair_df.shape[1] - 4)


def parse_repair_data(tool_name_list, dataset_name, localizer_name,
                      parent_output_dir):
    dataset = Main_util.get_dataset(dataset_name)
    all_bugs = dataset.get_bugs()

    # repair_df = pd.DataFrame(columns=[
    #     'apr', 'dataset', 'bug',
    #     # 'validation_strategey', 'time_cost',
    #     'pg_time', 'cur_stmt_time',
    #     "pg_time_1", "pg_time_2", "pg_time_3",
    #     'ncp1', 'ntce1', 'time_cost1',
    #     'ncp2', 'ntce2', 'time_cost2',
    #     'ncp3', 'ntce3', 'time_cost3',
    #     'has_patch1', 'has_patch2', 'has_patch3'
    # ])
    repair_df = pd.DataFrame(columns=[
        'ori_apr', 'apr', 'dataset', 'bug', 'repair_time', 'fl_time',
        'pg_time', 'compile_time', 'pv_time', 'ncp', 'ntce', 'has_patch',
        'insufficient_memory', 'filter_pass_all', 'filter_pass_file', 'insufficient_memory_2', 'vm_error', 'repeated_timeout_executions'
    ])
    for bug in all_bugs:
        for tool_name in tool_name_list:
            #
            # if bug.name != "defects4j_Closure_127":
            #     continue
            # if not (bug.name.lower() == "defects4j_closure_126" and tool_name == "simfix_0"):
            #     continue
            

            tool_name = tool_name.lower()
            # logger.info(f"parse: {tool_name} {bug.name}")
            apr_dir = os.path.join(parent_output_dir, bug.name, tool_name)

            gz_dir = os.path.join(parent_output_dir, bug.name, "gzoltar")
            gz_tests_path = os.path.join(gz_dir, "test_classes.txt")
            if os.path.exists(gz_dir):
                # TODO: simfix cannot allocate memory!
                # assert os.path.exists(gz_tests_path), f"{gz_dir}"

                if os.path.exists(gz_tests_path):
                    if len(File_util.read_file_add_wrap(gz_tests_path)) == 0:
                        # print(bug.name)
                        pass

            if not os.path.exists(apr_dir):
                continue

            # logger.info(f"now parse {apr_dir}")
            parser = Parser_factory.ParserFactory().create_parser(
                tool_name, apr_dir)
            parser.check_memory_problem(apr_dir)
            parser.check_validate_problem(apr_dir)
            parser.check_empty_patch(apr_dir)
            parser.check_memory_problem_2(apr_dir)
            # continue

            if tool_name.startswith('simfix') or tool_name.startswith('tbar'):

                parser.get_data_dict()

                # if parser.data_dict['time_out'] > 0:
                #     print(bug.get_proj_id())

                add_row(parser.is_complete_flag, repair_df, parser.data_dict,
                        tool_name, dataset_name, bug)
            else:
                parser.get_data_dict()
                data_dict = parser.data_dict
                is_complete_flag = parser.is_complete_flag
                add_row(is_complete_flag, repair_df, data_dict, tool_name,
                        dataset_name, bug)

    df_save_dir = os.path.join(parent_output_dir, "parser_results")
    make_dirs(df_save_dir)
    df_save_path = os.path.join(df_save_dir, "repair_df.csv")
    df_save_path2 = os.path.join(df_save_dir, "repair_df_str.txt")
    File_util.write_str_to_file(df_save_path2, repair_df.to_string(), False)
    repair_df.to_csv(df_save_path)


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path)


def set_logger(parent_output_dir):
    log_dir = os.path.join(parent_output_dir, "parser_results")
    make_dirs(log_dir)
    log_file = os.path.join(log_dir, "parse.log")
    logger = Logging_util.init_logger_with_file(log_file)


if __name__ == "__main__":
    import time
    start_time = time.time()

    # simfix_0 -> 1 2 3
    # simfix 1 -> 1 2
    tool_name_list = [
        'nopol_1', 'nopol_2', 'nopol_3', 'simfix_0', 'simfix_1', 'simfix_2', 'tbar_0', 'tbar_1', 'tbar_2', 'dynamoth_1', 'dynamoth_2', 'dynamoth_3'
    ]  # 'nopol_1', 'nopol_2', 'nopol_3', 'simfix_0', 'simfix_1', 'simfix_2', 'tbar_0', 'tbar_1', 'tbar_2', 'dynamoth_1', 'dynamoth_2', 'dynamoth_3'
    # 'tbar_0', 
    dataset_name = "defects4j"  #"defects4j" #"quixbugs"
    localizer_name = "gzoltar"

    parent_output_dir = Config.TMP_OUTPUT_DIR

    set_logger(parent_output_dir)

    if len(os.listdir(parent_output_dir)) > 0:
        File_util.rm_all_content_in_dir(parent_output_dir)

    tool_output_dir = os.path.abspath(
        os.path.join(parent_output_dir, "../results_" + dataset_name))
    parse_repair_data(tool_name_list, dataset_name, localizer_name,
                      tool_output_dir)

    logger.info(f"Main_parse execution time: {time.time() - start_time}s")
