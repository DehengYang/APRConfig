import logging, abc, os

from utils import Cmd_util, File_util, Yaml_util
import Config

logger = logging.getLogger()


class Parser(object, metaclass=abc.ABCMeta):
    def __init__(self, apr_dir):
        # constants
        self.localizer_name = 'gzoltar'

        self.apr_dir = apr_dir
        self.info_path = os.path.join(self.apr_dir, "info.txt")
        self.repair_log_path = os.path.join(self.apr_dir, "repair.log")

        self.data_dict = {}
        self.init_dict(self.data_dict)

    def init_dict(self, dict):
        dict['has_patch1'] = 0
        dict['has_patch2'] = 0
        dict['has_patch3'] = 0
        dict['ncp1'] = 0
        dict['ncp2'] = 0
        dict['ncp3'] = 0
        dict['ntce1'] = 0
        dict['ntce2'] = 0
        dict['ntce3'] = 0

        # patch validation time
        dict['time_cost'] = 0  # for nopol/dynamoth
        dict['time_cost1'] = 0
        dict['time_cost2'] = 0
        dict['time_cost3'] = 0

        dict['pg_time_1'] = 0
        dict['pg_time_2'] = 0
        dict['pg_time_3'] = 0

        # patch_index for simfix/tbar
        dict['patch_index1'] = Config.MAX_INT
        dict['patch_index2'] = Config.MAX_INT
        dict['patch_index3'] = Config.MAX_INT

        dict['pg_time'] = 0
        dict['cur_stmt_time'] = 0

        dict['time_out'] = 0

        # fl time
        dict['fl_time'] = 0

        # for nopol and dynamoth
        dict['compile_time'] = 0
        # for simfix and tbar
        dict['compile_time1'] = 0
        dict['compile_time2'] = 0
        dict['compile_time3'] = 0

        # insufficient memory
        dict['insufficient_memory'] = 'NO'
        dict['insufficient_memory_2'] = 'NO'

        # filter
        self.data_dict['filter_pass_all'] = "NO"
        self.data_dict['filter_pass_all_flag'] = None
        self.data_dict['filter_pass_all1'] = "NO"
        self.data_dict['filter_pass_all_flag1'] = None
        self.data_dict['filter_pass_all2'] = "NO"
        self.data_dict['filter_pass_all_flag2'] = None
        self.data_dict['filter_pass_all3'] = "NO"
        self.data_dict['filter_pass_all_flag3'] = None


        self.data_dict['vm_error_1'] = 'NO'
        self.data_dict['vm_error_2'] = 'NO'
        self.data_dict['vm_error_3'] = 'NO'

        self.data_dict['repeated_timeout_executions_1'] = 'NO'
        self.data_dict['repeated_timeout_executions_2'] = 'NO'
        self.data_dict['repeated_timeout_executions_3'] = 'NO'

    def check_memory_problem(self, apr_dir):
        cmd = f"""cd {apr_dir};
            grep -rni "There is insufficient memory" *;
        """
        output = Cmd_util.run_cmd_with_output_without_log(cmd)
        if len(output) > 0:
            self.data_dict['insufficient_memory'] = "YES"

    def check_memory_problem_2(self, apr_dir):
        """
        java.lang.OutOfMemoryError: Java heap space
        java.lang.OutOfMemoryError: GC overhead limit exceeded

        at present, only for tbar and simfix
        """
        if not('simfix' in apr_dir or 'tbar' in apr_dir):
            return

        cmd = f"""cd {apr_dir};
            grep -rni "java.lang.OutOfMemoryError: " *;
        """
        output = Cmd_util.run_cmd_with_output_without_log(cmd)
        if len(output) > 0:
            self.data_dict['insufficient_memory_2'] = "YES"
            logger.info(f"insufficient_memory_2: {apr_dir}")

    def check_validate_problem(self, apr_dir):
        # TODO check junit.framework.TestSuite$1#warning. e.g., /home/apr/bias_validation_2021/results_defects4j/defects4j_Time_14/nopol_3/validate/1_default.txt
        extra_failed_method_path = os.path.join(
            apr_dir, "../gzoltar/extra_failed_test_replicate.txt")
        dict = {'select': "1", 'prioritize': '2', 'default': '3'}

        if not os.path.exists(extra_failed_method_path):
            return
        extra_failed_methods = File_util.read_file_add_wrap(
            extra_failed_method_path)

        if len(extra_failed_methods) > 0:
            validate_path = os.path.join(apr_dir, "validate")

            # bug fix: exit if this does not exists!
            if not os.path.exists(os.path.join(apr_dir, 'info.txt')):
                self.is_complete_flag = False
                return

            # bug fix: must sort
            file_list = os.listdir(validate_path)
            file_list.sort(key=lambda x: int(x.split("_")[0]))
            for file in file_list:
                file_path = os.path.join(validate_path, file)
                if file_path.endswith(".txt"):
                    actual_failed_methods = File_util.read_file_add_wrap(
                        file_path)

                    if len(actual_failed_methods) == 0:
                        logger.info(
                            "actual_failed_methods is already empty. So skip checking."
                        )
                        continue

                    filter_failed = set(actual_failed_methods) - set(
                        extra_failed_methods)
                    if len(filter_failed) == 0:
                        if 'nopol' in apr_dir or 'dynamoth' in apr_dir:
                            self.data_dict['filter_pass_all'] = "YES"
                            self.data_dict['filter_pass_all_flag'] = file
                            break
                        else:  # simfix and tbar
                            # 351_prioritize.txt
                            mode = dict[file.split(".")[0].split("_")[-1]]
                            if self.data_dict['filter_pass_all' +
                                              mode] != "YES":
                                self.data_dict['filter_pass_all' +
                                               mode] = "YES"
                                self.data_dict['filter_pass_all_flag' +
                                               mode] = int(file.split("_")[0])

    def get_fl_run_time(self):
        output_yaml_file = os.path.join(self.apr_dir, "..",
                                        self.localizer_name,
                                        "output_data.yaml")
        fl_time_cost = 0
        if os.path.exists(output_yaml_file):
            output_dict = Yaml_util.read_yaml(output_yaml_file)
            fl_time_cost = float("{:.4f}".format(
                float(output_dict['time_cost_in_total']) -
                float(output_dict['time_cost_in_replication'])))
        assert fl_time_cost != 0

        return fl_time_cost

    def check_empty_patch(self, apr_dir):
        if 'simfix' in apr_dir.lower() or 'tbar' in apr_dir.lower():
            for i in range(1, 4):
                patch_file = os.path.join(self.apr_dir, f"patch{i}.txt")
                if os.path.exists(patch_file):
                    file_str = File_util.read_file(patch_file).strip()
                    if len(file_str) == 0:
                        logger.error(f"empty patch file: {apr_dir}")