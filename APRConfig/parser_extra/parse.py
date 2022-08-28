import os

from utils import File_util

cur_dir = os.path.dirname(os.path.abspath(__file__))

def parse_1(memory_error_for_simfix_tbar_file):
    """
    just run exceptional bugs in the real different set (obtained from plot_effectiveness.py)
    """

    simfix_dict = {'Chart_25', 'Math_44', 'Closure_126', 'Time_14', 'Mockito_25', 'Mockito_30', 'Math_74', 'Mockito_29', 'Math_84', 'Mockito_15', 'Mockito_37', 'Math_40', 'Lang_19', 'Mockito_27', 'Mockito_7', 'Math_61', 'Math_42', 'Closure_22', 'Mockito_31', 'Closure_21', 'Closure_46', 'Mockito_9', 'Mockito_8', 'Mockito_10', 'Closure_88', 'Closure_73', 'Math_98', 'Time_7', 'Closure_57', 'Closure_68', 'Lang_50', 'Closure_115', 'Closure_79', 'Chart_22', 'Math_71', 'Lang_60', 'Chart_14', 'Lang_41', 'Chart_20', 'Math_72', 'Math_80', 'Chart_12', 'Chart_18', 'Math_1', 'Math_35', 'Closure_106'}

    tbar_dict = {'Lang_6', 'Lang_24', 'Lang_18', 'Chart_3', 'Chart_5', 'Lang_61', 'Math_81', 'Math_104', 'Lang_55', 'Math_40', 'Math_78', 'Math_88', 'Closure_16', 'Closure_81', 'Math_106', 'Closure_7', 'Mockito_7', 'Lang_13', 'Mockito_22', 'Mockito_8', 'Closure_19', 'Math_7', 'Lang_60', 'Math_84', 'Math_20', 'Math_22', 'Closure_46', 'Closure_86', 'Math_73', 'Chart_19', 'Math_59', 'Math_77', 'Time_7', 'Closure_115', 'Closure_73', 'Time_11', 'Chart_14', 'Math_98', 'Chart_8', 'Closure_10', 'Time_17', 'Chart_20', 'Closure_38', 'Lang_22', 'Closure_2', 'Lang_47', 'Math_35', 'Math_60', 'Math_4', 'Math_3'}


    lines = File_util.read_file_add_wrap(memory_error_for_simfix_tbar_file)
    machine = -1
    for line in lines:
        if "machine" in line:
            machine = line.strip().split(" ")[-1]
        if "simfix" in line or "tbar" in line:
            splits = line.split("/")
            apr = splits[-1]
            bug = splits[-2]
            bug = bug[len("defects4j_"):]

            if 'simfix' in apr:
                if bug in simfix_dict:
                    print(apr, bug, f"machine{machine}")
            if 'tbar' in apr:
                if bug in tbar_dict:
                    print(apr, bug, f"machine{machine}")
            

if __name__ == "__main__":
    memory_error_for_simfix_tbar_file = os.path.join(cur_dir, "memory_error_for_simfix_tbar.txt")
    parse_1(memory_error_for_simfix_tbar_file)

