import os, re

import Config

from utils import Dataframe_util, File_util

apr_tools = ['nopol', 'dynamoth', 'simfix', 'tbar']

def get_patch(df_path, parse_rlt_dir, result_dir, dataset_name):
    df = Dataframe_util.read_csv(df_path)

    df = df[(df.has_patch == "yes") | (df.filter_pass_all == "YES")].copy()

    # init patch
    # for apr in apr_tools:
    output_dir = os.path.join(parse_rlt_dir, "patches")
    File_util.mk_dir_from_dir_path(output_dir)
    # clean
    for file_name in os.listdir(output_dir):
        cur_file = os.path.join(output_dir, file_name) 
        if cur_file.endswith(".diff"):
            os.remove(cur_file)

    for bug in set(df.bug.values):
        bug_patch_save_path = os.path.join(output_dir, f"{bug}.diff")
        File_util.write_str_to_file(bug_patch_save_path,"",append=False)

        bug_df = df[df.bug == bug].copy()
        bug_df.sort_values("apr", inplace=True)
        for index, row in bug_df.iterrows():
            bug_name = row['bug']
            apr_name = row['apr']
            validate_mode = apr_name.split("_")[-1]
            ori_apr_name = row['ori_apr']
            filter_pass_file = row['filter_pass_file']

            ori_patch_path = os.path.join(result_dir, f"{dataset_name}_{bug_name}", 'dataset', 'patch.diff')
            ori_patch = File_util.read_file_to_str(ori_patch_path)

            # if bug.lower() == "closure_133":
            #     print()

            if 'nopol' in apr_name or 'dynamoth' in apr_name:
                # /home/apr/bias_validation_2021/results_defects4j/defects4j_Closure_48/dynamoth_3/candidate_patches.txt
                patch_file_path = os.path.join(result_dir, f"{dataset_name}_{bug_name}", ori_apr_name, 'candidate_patches.txt')

                patch_index = 0
                if not isinstance(filter_pass_file, float): # not a nan
                    patch_index = int(filter_pass_file.split("_")[0]) - 1
                else:
                    patch_index = int(row['ncp']) - 1
                if patch_index != 0:
                    print(f"patch_index: {patch_index} {bug} {apr_name}")
                
                patch = get_nopol_dyn_patch(patch_index, patch_file_path)
            else:
                if not isinstance(filter_pass_file, float): # not a nan
                    patch_file_path = os.path.join(result_dir, f"{dataset_name}_{bug_name}", ori_apr_name, 'patches.txt')

                    # in machine2, for example, /home/apr/bias_validation_2021/results_defects4j/defects4j_Math_79/simfix_0-need-rerun  I rename this dir and rerun it on other machines, so this will cause file not exist exception
                    if not os.path.exists(patch_file_path):
                        continue
                    
                    patch_index = int(filter_pass_file.split("_")[0]) 
                    patch = get_simfix_tbar_patch(patch_index, patch_file_path)
                else:
                    patch_file_path = os.path.join(result_dir, f"{dataset_name}_{bug_name}", ori_apr_name, f'patch{validate_mode}.txt')
                    
                    # in machine2, for example, /home/apr/bias_validation_2021/results_defects4j/defects4j_Math_79/simfix_0-need-rerun  I rename this dir and rerun it on other machines, so this will cause file not exist exception
                    if not os.path.exists(patch_file_path):
                        continue

                    patch = File_util.read_file(patch_file_path)

            if len(File_util.read_file_to_str(bug_patch_save_path).strip()) == 0:
                File_util.write_str_to_file(bug_patch_save_path,f"""
                ====================== human-written patch ================================
                
                {ori_patch}

                """,append=True)

            if len(patch.strip()) != 0:
                File_util.write_str_to_file(bug_patch_save_path,f"""
                ====================== {apr_name} {bug} ================================
                
                {patch}

                """,append=True)
                
def get_simfix_tbar_patch(patch_index, patch_file_path):
#     txt_str = """
#     [PATCH 19] file: /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Closure_126/defects4j_Closure_126/defects4j_Closure_126/src//com/google/javascript/jscomp/MinimizeExitPoints.java, range: <141,144>, original: if(NodeUtil.hasFinally(n)){
# Node finallyBlock=n.getLastChild();
# tryMinimizeExits(finallyBlock,exitType,labelName);
# }
# , patch: if(!n.isName()){
# return ;
# }
# if(NodeUtil.hasFinally(n)){
# Node finallyBlock=n.getLastChild();
# tryMinimizeExits(finallyBlock,exitType,labelName);
# }
# [PATCH 20]
#     """
    txt_str = File_util.read_file(patch_file_path)
    pattern = re.compile(rf"\[PATCH {patch_index}\](.*?)\[PATCH ",re.DOTALL)
    # pattern = re.compile(r"\[PATCH (.*?)tryMinimizeExits",re.DOTALL)
    match = re.findall(pattern, txt_str)[0]

    return match

def get_nopol_dyn_patch(patch_index, patch_file_path):
    # in machine3, for example, /home/apr/bias_validation_2021/results_defects4j/defects4j_Math_20/nopol_2-rerun  I rename this dir and rerun it on other machines, so this will cause file not exist exception
    if not os.path.exists(patch_file_path):
        return ""
    lines = File_util.read_file_add_wrap(patch_file_path)

    cur_index = -1
    cur_patch = ''
    patch_list = []
    for line in lines:
        if line == '[PATCH]':
            cur_index += 1
            if cur_index != 0:
                patch_list.append(cur_patch)
            cur_patch = ''
        else:
            cur_patch += line + "\n"
    patch_list.append(cur_patch)

    return patch_list[patch_index]


if __name__ == "__main__":
    dataset_name = "defects4j"  #"defects4j" #"quixbugs"
    result_dir = os.path.abspath(os.path.join(Config.TMP_OUTPUT_DIR,"../results_" + dataset_name))
    parse_rlt_dir = os.path.join(result_dir, "parser_results")
    df_path = os.path.join(parse_rlt_dir, 'repair_df.csv')

    get_patch(df_path, parse_rlt_dir, result_dir, dataset_name)
