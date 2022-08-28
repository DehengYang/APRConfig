from genericpath import exists
import os, re

from utils import File_util, Yaml_util
import Parser

import logging

logger = logging.getLogger()


class SimfixParser(Parser.Parser):
    def __init__(self, apr_dir, validate_mode) -> None:
        super().__init__(apr_dir)

        self.validate_mode = validate_mode
        if validate_mode == "1":
            self.data_dict['validation_strategey'] = 'default'

        # self.sel_data_dict = {"validation_strategey" : "selection"}
        # self.pri_data_dict = {"validation_strategey" : "prioritization"}
        # self.init_dict(self.sel_data_dict)
        # self.init_dict(self.pri_data_dict)

        self.is_complete_flag = True
        self.data_dict['time_out1'] = False
        self.data_dict['time_out2'] = False
        self.data_dict['time_out3'] = False

    def get_data_dict(self):
        """
        collect data:
        'validation_strategey', 'time_cost', 'ncp', 'ntce', 'has_patch'
        """

        # sanity check!
        if not os.path.exists(self.repair_log_path):
            self.is_complete_flag = False
            return
        repair_log_str = File_util.read_file(self.repair_log_path)
        if " [main] ends." not in repair_log_str:
            self.is_complete_flag = False
            return

        info_str = File_util.read_file(self.info_path)
        info_lines = File_util.read_file_add_wrap(self.info_path)

        # if self.validate_mode == "1":
        #     assert False
        # else:
        self.get_time_cost(info_str)
        # 'ncp', 'ntce', 'has_patch'
        self.get_patch_info(info_str, info_lines)

    def get_patch_info(self, info_str, info_lines):
        # TODO put out of this loop
        mode_dict = {1:'select', 2:'prioritize', 3:'default'}
        for i in range(1, 4):
            patch_file = os.path.join(self.apr_dir, f"patch{i}.txt")

            if self.data_dict['filter_pass_all' + str(i)] == "YES":
                self.data_dict['has_patch' + str(i)] = 1

            if os.path.exists(patch_file):
                self.data_dict['has_patch' + str(i)] = 1

                # TODO: to be removed after the experiment for these exceptional bugs is done
                if len(File_util.read_file_add_wrap(patch_file)) == 0:
                    continue

                first_line = File_util.read_file_add_wrap(patch_file)[0]
                pattern = re.compile(r"\[PATCH (.*?)\]")
                match = re.findall(pattern, first_line)[0]
                self.data_dict['patch_index' + str(i)] = int(match)

                #Error occurred during initialization of VM
                validate_log_path = os.path.join(self.apr_dir, 'validate', f'{match}_{mode_dict[i]}.txt.log')
                if os.path.exists(validate_log_path):
                    log_str = File_util.read_file(validate_log_path)
                    if "Error occurred during initialization of VM" in log_str:
                        # File_util.write_str_to_file("/home/apr/bias_validation_2021/exceptions.txt",validate_log_path)
                        self.data_dict[f'vm_error_{i}'] = 'YES'
                        self.data_dict['has_patch' + str(i)] = 0
                # reset num!
                if self.data_dict['filter_pass_all' + str(i)] == "YES":
                    self.data_dict['patch_index' + str(i)] = self.data_dict[
                        'filter_pass_all_flag' + str(i)]

        if "[PATCH_VALIDATION_INFO]" not in info_str:
            pass
        else:
            patch_cnt = 0
            # cur_stmt_time = 0
            cur_stmt_pv_time = 0
            for line in info_lines:
                if line.startswith("[TIME_OUT] "):
                    # logger.info("time_out")
                    self.data_dict['time_out'] += 1
                if line.startswith("[STMT_INFO] "):
                    # [STMT_INFO] curStmt: BREADTH_FIRST_SEARCH:30 singleStmtPGVTimeCost: 8.626
                    pattern = re.compile(
                        r'\[STMT_INFO\] curStmt: .* singleStmtPGVTimeCost: (.*)'
                    )
                    match = re.findall(pattern, line)[0]
                    cur_stmt_time = float(match)

                    self.data_dict['cur_stmt_time'] += cur_stmt_time

                    # time cost
                    if cur_stmt_pv_time > 0:
                        cur_stmt_pg_time = cur_stmt_time - cur_stmt_pv_time
                        cur_stmt_pv_time = 0
                        for validate_mode in range(1, 4):
                            if patch_cnt <= self.data_dict['patch_index' +
                                                           str(validate_mode)]:
                                self.data_dict[
                                    'pg_time_' +
                                    str(validate_mode)] += cur_stmt_pg_time

                if line.startswith(
                        "[PATCH_VALIDATION_INFO] "):  # patch id start from 1
                    patch_cnt += 1
                    #[PV_INFO] curStmt: SourceLocation java_programs.QUICKSORT:26 singleCompileTimeCost: 0.066, singlePVTimeCost: 0.139 pvInfo: compilePasstesttrue NTCE: 12
                    # [PATCH_VALIDATION_INFO] patchId: 96 curStmt: BREADTH_FIRST_SEARCH:27 singleCompileTimeCost: 0.398 singleTestTimeCost1: 0.142 singleSelectionTimeCost: 0.0 singleTestTimeCost2: 0.109 singleTestTimeCost3: 0.115 cleanCompileTimeCost: 0.0 pvInfo: compilePass pvInfo1: <lines:10,realLines:7> testfalse pvInfo2: failNeg testfalse pvInfo3:  NTCE1: 25 NTCE2: 1 NTCE3: 5
                    pattern = re.compile(
                        r'\[PATCH_VALIDATION_INFO\] patchId: .* curStmt: .* singleCompileTimeCost: (.*) singleTestTimeCost1: (.*) singleSelectionTimeCost: .* singleTestTimeCost2: (.*) singleTestTimeCost3: (.*) cleanCompileTimeCost: (.*) pvInfo: (.*) pvInfo1: (.*) pvInfo2: (.*) pvInfo3: (.*) NTCE1: (.*) NTCE2: (.*) NTCE3: (.*)'
                    )
                    match = re.findall(pattern, line)[0]
                    cnt = 0
                    singleCompileTimeCost = float(match[cnt])
                    cnt += 1
                    singleTestTimeCost1 = float(match[cnt])
                    cnt += 1
                    singleTestTimeCost2 = float(match[cnt])
                    cnt += 1
                    singleTestTimeCost3 = float(match[cnt])
                    cnt += 1

                    # just for workaround of quixbugs
                    # if singleTestTimeCost1 > singleTestTimeCost3 and singleTestTimeCost1 > 200:
                    #     singleTestTimeCost1 = singleTestTimeCost3
                    #     self.data_dict['repeated_timeout_executions_1'] = 'YES'

                    cleanCompileTimeCost = float(match[cnt])
                    cnt += 1
                    pvInfo = match[cnt]
                    cnt += 1
                    pvInfo1 = match[cnt]
                    cnt += 1
                    pvInfo2 = match[cnt]
                    cnt += 1
                    pvInfo3 = match[cnt]
                    cnt += 1
                    NTCE1 = int(match[cnt])
                    cnt += 1
                    NTCE2 = int(match[cnt])
                    cnt += 1
                    NTCE3 = int(match[cnt])

                    # check time out
                    #  pvInfo: compilePass pvInfo1:  pvInfo2:
                    if pvInfo == "compilePass" and len(pvInfo1.strip()) == 0:
                        self.data_dict['time_out1'] = True

                    cur_stmt_pv_time += singleCompileTimeCost + singleTestTimeCost1 + singleTestTimeCost2 + singleTestTimeCost3 + cleanCompileTimeCost

                    for validate_mode in range(1, 4):
                        validate_mode = str(validate_mode)
                        if self.data_dict[
                                'pg_time_' + validate_mode] + self.data_dict[
                                    'time_cost' +
                                    validate_mode] + self.data_dict[
                                        'compile_time' +
                                        validate_mode] <= 7200 and (
                                            not self.data_dict['time_out' +
                                                               validate_mode]):
                            if patch_cnt <= self.data_dict['patch_index' +
                                                           validate_mode]:
                                self.data_dict[
                                    'compile_time' +
                                    validate_mode] += singleCompileTimeCost + cleanCompileTimeCost

                                self.data_dict['time_cost' +
                                               validate_mode] += [
                                                   singleTestTimeCost1,
                                                   singleTestTimeCost2,
                                                   singleTestTimeCost3
                                               ][int(validate_mode) - 1]

                                self.data_dict['ntce' + validate_mode] += [
                                    NTCE1, NTCE2, NTCE3
                                ][int(validate_mode) - 1]
                                self.data_dict['ncp' + validate_mode] += 1

                    # TODO compile fail patches, pass patches ... (cover all)
                    # if len(pvInfo1.strip()) > 0:
                    #     self.data_dict['ncp1'] += 1
                    # if len(pvInfo2.strip()) > 0:
                    #     self.data_dict['ncp2'] += 1
                    # if NTCE3 > 0:
                    #     self.data_dict['ncp3'] += 1

                    # DEPRECATED
                    # if "testtrue" in pvInfo1:
                    #     self.data_dict['has_patch1'] += 1
                    # else:
                    #     pass
                    # if "testtrue" in pvInfo2:
                    #     self.data_dict['has_patch2'] += 1
                    # else:
                    #     pass
                    # if "testtrue" in pvInfo2: # follow 2
                    #     self.data_dict['has_patch3'] += 1
                    # else:
                    #     pass

    def get_time_cost(self, info_str):
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
        """
[FINAL_INFO]
pvSelectTimeCost: 12.572001
pvPrioritizeTimeCost: 10.6
pvDefaultTimeCost: 0.0
beforeFLTimeCost: 0.079
parseFLTimeCost: 0.003
pgvTotalTimeCost: 78.24
afterPVTimeCost: 0.0
"""

        pattern = re.compile(
            r"\[FINAL_INFO\]\npvSelectTimeCost: (.*)\npvPrioritizeTimeCost: (.*)\npvDefaultTimeCost: .*\nbeforeFLTimeCost: (.*)\nparseFLTimeCost: (.*)\npgvTotalTimeCost: (.*)\nafterPVTimeCost: (.*)"
        )
        matches = re.findall(pattern, info_str)
        match = matches[0]
        pvSelectTimeCost = float(match[0])
        pvPriotizeTimeCost = float(match[1])
        # pvDefaultTimeCost = float
        beforeFLTimeCost = float(match[2])
        parseFLTimeCost = float(match[3])
        pgvTotalTimeCost = float(match[4])
        afterPVTimeCost = float(match[5])

        self.data_dict[
            "time_cost_1"] = pgvTotalTimeCost - pvPriotizeTimeCost + beforeFLTimeCost + parseFLTimeCost + afterPVTimeCost + fl_time_cost
        self.data_dict[
            "time_cost_2"] = pgvTotalTimeCost - pvSelectTimeCost + beforeFLTimeCost + parseFLTimeCost + afterPVTimeCost + fl_time_cost

        self.data_dict['fl_time'] = fl_time_cost + parseFLTimeCost
