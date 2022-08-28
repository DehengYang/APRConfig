# to export data from cloud service (Aliyun ECS)
import os, shutil

from utils import File_util, Time_util, Logging_util, Cmd_util

cur_dir = os.path.dirname(os.path.abspath(__file__))

apr_tool_list = ['simfix', 'tbar', 'nopol', 'dynamoth']


def result_processor(result_dir, new_result_dir, dataset_name):
    File_util.get_folder_size(result_dir)

    # find . -type f -name execution_framework.log -size +10M -exec du -h {} \;
    for folder in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder)
        if not folder.startswith(f'{dataset_name}_'):
            continue

        # 1) copy
        copy_folder_path = os.path.join(new_result_dir, folder)
        shutil.copytree(folder_path, copy_folder_path)

        logger.info(f"\n\n\n=================================== operate on {copy_folder_path} ==============================================\n\n\n")

        # 2) remove folders
        gzoltar_dir = os.path.join(copy_folder_path, 'gzoltar')
        # /home/apr/bias_validation_2021/results_defects4j/defects4j_Closure_103/tbar_1 in machine
        if not os.path.exists(gzoltar_dir):
            logger.warn(f"{gzoltar_dir} does not exists. Skip.")
            File_util.rm_dir_safe_contain(copy_folder_path, f'results_{dataset_name}_processed')
            continue
        
        if File_util.get_folder_size(gzoltar_dir, 'mb', True) > 10:
            cmd = f"""cd {copy_folder_path};
            lrztar gzoltar
            """
            Cmd_util.run_cmd_with_output(cmd)
            assert os.path.exists(
                os.path.join(copy_folder_path, "gzoltar.tar.lrz"))
            File_util.rm_dir_safe_contain(gzoltar_dir,
                                          f'results_{dataset_name}_processed')

        for cur_folder in os.listdir(copy_folder_path):
            cur_folder_path = os.path.join(copy_folder_path, cur_folder)
            # remove defects4j_Math_79
            if cur_folder.startswith(f'{dataset_name}_'):
                assert cur_folder == folder
                File_util.rm_dir_safe_contain(
                    cur_folder_path, f'results_{dataset_name}_processed')
            # remove rerun
            if 'rerun' in cur_folder:
                File_util.rm_dir_safe_contain(
                    cur_folder_path, f'results_{dataset_name}_processed')

            for apr in apr_tool_list:
                # '/home/apr/bias_validation_2021/execution_framework/result_processor/../../results_defects4j_processed/tbar_0'
                if cur_folder.startswith(apr):
                    # remove compile dir
                    File_util.rm_dir_safe_contain(
                        os.path.join(cur_folder_path, "compile"),
                        f'results_{dataset_name}_processed')

                    #
                    remove_large_file(cur_folder_path, 'repair.log')
                    remove_large_file(cur_folder_path, 'info.txt')
                    remove_large_file(cur_folder_path,
                                      'execution_framework.log')
                    remove_large_file(cur_folder_path, 'patches.txt')
                    remove_large_file(cur_folder_path, f'{apr}.log')

                    validate_dir = os.path.join(cur_folder_path, 'validate')
                    if os.path.exists(validate_dir):
                        # validate_dir_size = File_util.get_folder_size(validate_dir)
                        cmd = f"""cd {cur_folder_path};
                        lrztar validate
                        """
                        Cmd_util.run_cmd_with_output(cmd)
                        assert os.path.exists(
                            os.path.join(cur_folder_path, "validate.tar.lrz"))
                        File_util.rm_dir_safe_contain(
                            validate_dir, f'results_{dataset_name}_processed')

                    # remove
                    tmp_method_path = os.path.join(cur_folder_path,
                                                   'tmp_methods.txt')
                    File_util.rm_file(tmp_method_path)

                    # remove
                    tmp_patch_dir_path = os.path.join(cur_folder_path, 'patch')
                    File_util.rm_dir_safe_contain(
                        tmp_patch_dir_path,
                        f'results_{dataset_name}_processed')

        # break

    File_util.get_folder_size(new_result_dir)


def remove_large_file(cur_folder_path, file_name, threshold=1, unit='mb'):
    file_path = os.path.join(cur_folder_path, file_name)
    if not os.path.exists(file_path):
        return
    if File_util.get_folder_size(file_path, unit, True) > threshold:
        cmd = f"""cd {cur_folder_path};
        lrzip {file_name}
        """
        Cmd_util.run_cmd_with_output(cmd)
        assert os.path.exists(os.path.join(cur_folder_path,
                                           f"{file_name}.lrz"))
        File_util.rm_file(file_path)


if __name__ == "__main__":
    Time_util.update_start_time()

    dataset_name = 'defects4j'

    # /home/apr/bias_validation_2021/execution_framework/result_processor
    # /home/apr/bias_validation_2021/results_defects4j
    result_dir = os.path.join(cur_dir, f'../../results_{dataset_name}')
    assert os.path.exists(result_dir)

    new_result_dir = os.path.join(cur_dir,
                                  f'../../results_{dataset_name}_processed')
    if not os.path.exists(new_result_dir):
        os.makedirs(new_result_dir)
    else:
        File_util.rm_dir(new_result_dir)
        os.makedirs(new_result_dir)

    log_file = os.path.join(new_result_dir, 'process.log')
    logger = Logging_util.init_logger_with_file(log_file)

    result_processor(result_dir, new_result_dir, dataset_name)

    # print(File_util.get_folder_size('/home/apr/bias_validation_2021/results_defects4j/defects4j_Chart_2'))

    Time_util.cal_time_cost()