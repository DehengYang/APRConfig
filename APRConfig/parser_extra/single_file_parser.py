import argparse, sys, re
from os import path

def get_file_name(sys_args):
    parser = argparse.ArgumentParser(
        prog="Main",
        description='Run APR tools for repairing specific bugs/datasets.')
    
    parser.add_argument('-f', '--file_path', required=True, help='target file path')
    
    args = parser.parse_args(sys_args)

    return args.file_path

def get_time(file_name):
    with open(file_name, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
        total_time = 0
        for line in lines:
            # [PATCH_VALIDATION_INFO] patchId: 131 curStmt: org.apache.commons.lang3.StringUtils:3623 singleCompileTimeCost: 1.044 singleTestTimeCost1: 0.0 singleSelectionTimeCost: 0.0 singleTestTimeCost2: 0.0 singleTestTimeCost3: 0.0 cleanCompileTimeCost: 0.0 pvInfo: compileFail pvInfo1:  pvInfo2:  pvInfo3:  NTCE1: 0 NTCE2: 0 NTCE3: 0
            match = re.findall(re.compile('singleTestTimeCost1: (.*?) singleSelectionTimeCost'), line)
            if len(match) > 0: 
                time = float(match[0])
                total_time += time
                if time > 50:
                    print(time)
        print("total_time: ", total_time)

if __name__ == "__main__":
    file_name = get_file_name(sys.argv[1:])

    get_time(file_name)