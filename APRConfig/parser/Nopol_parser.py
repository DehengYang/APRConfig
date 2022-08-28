from numpy import info
from pandas.core.indexing import _iAtIndexer
import dataset
from logging import Logger
import logging
import os, re

from utils import File_util
import Parser

logger = logging.getLogger()

class NopolParser(Parser.Parser):
    def __init__(self, tool_name, apr_dir, validate_mode) -> None:
        super().__init__(apr_dir)
        self.tool_name = tool_name
        self.validate_mode = validate_mode
        self.is_complete_flag = False

    def get_data_dict(self):
        """
        collect data:
        'validation_strategey', 'time_cost', 'ncp', 'ntce', 'has_patch'
        """
        # validation_strategey
        self.get_validation_strategy()

        # sanity check!
        if not os.path.exists(self.repair_log_path):
            return
        if len(File_util.read_file_add_wrap(os.path.join(self.apr_dir, "parsed_fl.txt")))  == 0:
            return

        # TODO : OutOfMemoryError GC (so many for both orginal repairthemall and cur versions)
        if not os.path.exists(self.info_path):
            return self.data_dict, False

        # info_str = File_util.read_file(self.info_path)
        info_lines = File_util.read_file_add_wrap(self.info_path)

        # check_validate_problem: filter_pass_all_flag
        true_patch_no = None
        if self.data_dict['filter_pass_all_flag'] is not None:
            # "1_default.txt"
            true_patch_no = int(self.data_dict['filter_pass_all_flag'].split("_")[0])
            pass

        # get 'ncp', 'ntce', 'has_patch'
        self.get_patch_info(info_lines, true_patch_no)

        # TODO: DEPRECATED
        # # get time_cost
        # pgvTotalTimeCost = self.get_time_cost(info_lines)
        # if pgvTotalTimeCost > 0:
        #     print(pgvTotalTimeCost - self.data_dict['time_cost' + self.validate_mode], self.data_dict['pg_time_' + self.validate_mode] - self.data_dict['time_cost' + self.validate_mode])
        #     self.data_dict['pg_time_' + self.validate_mode] = pgvTotalTimeCost - self.data_dict['time_cost' + self.validate_mode]
        # else: # exit abnormally 
        #     self.data_dict['pg_time_' + self.validate_mode] -= self.data_dict['time_cost' + self.validate_mode]
        self.data_dict['fl_time'] = self.get_fl_run_time()
        self.data_dict["time_cost"] = self.data_dict['pg_time_' + self.validate_mode]
        self.data_dict['pg_time_' + self.validate_mode] -= self.data_dict['time_cost' + self.validate_mode]

        self.is_complete_flag = True

    def get_validation_strategy(self):
        if self.validate_mode == "1":
            self.data_dict['validation_strategey'] = 'selection'
        elif self.validate_mode == "2":
            self.data_dict['validation_strategey'] = 'prioritization'
        elif self.validate_mode == "3":
            self.data_dict['validation_strategey'] = 'default'

    def is_last_stmt(self, info_lines, line_cnt, curStmt):
        if line_cnt >= len(info_lines):
            return True
        for index in range(line_cnt, len(info_lines)):
            line = info_lines[index]
            if not line.startswith("[STMT_INFO]"):
                if index == len(info_lines) - 1:
                    return True
                continue
            pattern = re.compile(
                    r'\[STMT_INFO\] curStmt: SourceLocation (.*) singleStmtPGVTimeCost: (.*)'
                )
            match = re.findall(pattern, line)[0]
            cnt = 0
            thisCurStmt = match[cnt]
            if curStmt != thisCurStmt:
                return True
            else:
                return False


    def get_patch_info(self, info_lines, true_patch_no):
        pv_cnt = 1
        line_cnt = 0
        for line in info_lines:
            line_cnt += 1
            if line.startswith("[STMT_INFO] "):
                # [STMT_INFO] curStmt: SourceLocation com.google.javascript.jscomp.type.SemanticReverseAbstractInterpreter:419 singleStmtPGVTimeCost: 8.002
                pattern = re.compile(
                    r'\[STMT_INFO\] curStmt: SourceLocation (.*) singleStmtPGVTimeCost: (.*)'
                )
                match = re.findall(pattern, line)[0]
                cnt = 0
                curStmt = match[cnt]
                cnt += 1
                singleStmtPGVTimeCost = float(match[cnt])

                """
                for nopol and dynmoath, there are multiple try for a single stmt. therefore, there are multiple [STMT_INFO]. we should select the last one as its total time spent on this stmt.
                """
                if self.is_last_stmt(info_lines, line_cnt, curStmt):
                    self.data_dict['pg_time_' + self.validate_mode] += singleStmtPGVTimeCost
                    if true_patch_no is not None and pv_cnt > true_patch_no:
                        break

            if line.startswith("[PV_INFO] "):
                if true_patch_no is not None and pv_cnt > true_patch_no:
                    continue
                pv_cnt += 1
                #[PV_INFO] curStmt: SourceLocation java_programs.QUICKSORT:26 singleCompileTimeCost: 0.066, singlePVTimeCost: 0.139 pvInfo: compilePasstesttrue NTCE: 12
                pattern = re.compile(
                    r'\[PV_INFO\] curStmt: SourceLocation .* singleCompileTimeCost: (.*), singlePVTimeCost: (.*) pvInfo: (.*) NTCE: (.*)'
                )
                match = re.findall(pattern, line)[0]
                cnt = 0
                singleCompileTimeCost = float(match[cnt])
                cnt += 1
                singlePVTimeCost = float(match[cnt])
                cnt += 1
                pvInfo = match[cnt]
                cnt += 1
                NTCE = int(match[cnt])

                self.data_dict['ntce' + self.validate_mode] += NTCE
                self.data_dict['ncp' + self.validate_mode] += 1
                self.data_dict['time_cost' + self.validate_mode] += singleCompileTimeCost + singlePVTimeCost

                self.data_dict['compile_time'] += singleCompileTimeCost

                pvInfo = match[-2]
                if pvInfo == "compilePasstesttrue" or pv_cnt == true_patch_no: # special event handling
                    self.data_dict['has_patch' + self.validate_mode] += 1
                else:
                    pass

    def get_time_cost(self, info_lines):
        # DONE:TODO: last line is null
        # apr2 /mnt/data/bias_validation_2021/results_defects4j/defects4j_Lang_63/nopol_1/execution_framework.log
        # workaround
        if len(info_lines) == 0:
            return -1
        
        last_line = info_lines[-1]
        # [FINAL_INFO] FL_TIME_COST: 1.433 flTimeCost: 0.007 beforeFLTimeCost: 1.396 afterPVTimeCost: 0.017 pgvTotalTimeCost: 0.901
        pattern = re.compile(
            'FL_TIME_COST: (.*) flTimeCost: (.*) beforeFLTimeCost: (.*) afterPVTimeCost: (.*) pgvTotalTimeCost: (.*)'
        )
        # '[FINAL_INFO] FL_TIME_COST: 1.337 flTimeCost: 0.005 beforeFLTimeCost: 1.365 afterPVTimeCost: 0.011 pgvTotalTimeCost: 1.314'

        matches = re.findall(pattern, last_line)
        if len(matches) == 0:
            return -1
        assert len(matches) == 1
        match = matches[0]
        flTimeCost = float(match[0]) + float(match[1])
        beforeFLTimeCost = float(match[2])
        afterPVTimeCost = float(match[3])
        pgvTotalTimeCost = float(match[4])
        total_time_cost = flTimeCost + beforeFLTimeCost + afterPVTimeCost + pgvTotalTimeCost

        self.data_dict['fl_time'] = flTimeCost
        self.data_dict["time_cost"] = total_time_cost

        return pgvTotalTimeCost