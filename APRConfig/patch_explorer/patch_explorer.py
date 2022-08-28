import os
import Config
from unidiff import PatchSet
from dataset import Dataset_factory
from utils import Dataset_util, File_util, Json_util, Logging_util, Cmd_util

logger = Logging_util.init_console_logger()

def process_patch(patch):
    patchset = PatchSet.from_string(patch)
    modified_files = ""
    src_file0 = patchset[0].source_file
    assert "source" in src_file0 or "src" in src_file0
    if "source" in src_file0:
        i = src_file0.index("source")
        patch_n = src_file0[:i].count("/")
    elif "src" in src_file0:
        i = src_file0.index("src")
        patch_n = src_file0[:i].count("/")
    for p in patchset:
        modified_files += f" {p.source_file[i:]}"
    return patch_n, modified_files

def patch_and_test(dataset_name, bug_id, apr_tool, dataset, patch):
    if os.path.exists(os.path.join(Config.PROJECT_PATH, "patch_explorer", "output2", apr_tool, dataset_name, f"{bug_id}.txt")):
        # logger.info("Patch and test done. Skip.")
        return
    logger.info(f"Dataset: {dataset_name} Bug Id: {bug_id} Tool: {apr_tool}")
    bug = dataset.get_bug(bug_id)

    parent_output_dir = Config.TMP_OUTPUT_DIR
    working_dir = os.path.join(parent_output_dir, bug.name, bug.name)
    bug_pool_dir = os.path.join(parent_output_dir, "pool", bug.name)

    logger.info(f"Working dir: {working_dir}")
    dataset.clean_dir(bug, working_dir)

    # checkout
    logger.info(f"Dataset: {dataset_name} Bug Id: {bug_id} checkout")
    dataset.checkout_and_compile(bug, working_dir, bug_pool_dir)
    test_result1 = dataset.run_test(bug)
    # apply patch
    patch_n, modified_files = process_patch(patch)
    patch_path = os.path.join(parent_output_dir, bug.name, f"{apr_tool}.patch")
    File_util.write_to_file(patch_path, patch)
    logger.info(f"Output of patch:\n{patch}")
    logger.info(f"Apply {apr_tool} patch")
    cmd_str = f"""
    cd {working_dir};
    dos2unix {modified_files};
    patch -p{patch_n} --ignore-whitespace -i ../{apr_tool}.patch;
    """
    apply_result = Cmd_util.run_cmd(cmd_str)
    assert "FAILED" not in apply_result
    # recompile
    dataset.compile(bug)
    # test
    test_result2 = dataset.run_test(bug)
    # clean working dir
    # dataset.clean_dir(bug, working_dir)

    output_path = os.path.join(Config.PROJECT_PATH, "patch_explorer", "output2", apr_tool, dataset_name, f"{bug_id}.txt")
    output_str = f"""
    Original test result:
    {test_result1}
    Applying patch result:
    {apply_result}
    Test result after patching:
    {test_result2}
    """
    File_util.write_to_file(output_path, output_str)

def run_dataset(datasets, apr_tools, patch_dir):
    for dataset_name in datasets:
        dataset = Dataset_factory.DatasetFactory().create_dataset(dataset_name)

        bug_ids_or_range_file_path = Dataset_util.get_bug_ids_path(dataset_name)
        Config.TMP_OUTPUT_DIR = os.path.join(Config.PARENT_PROJECT_PATH, f"patch_explorer_{dataset_name}")
        Config.rerun_dataset = False
        # bug_ids = Dataset_util.get_bug_ids_from_txt(bug_ids_or_range_file_path)
        bug_ids = File_util.read_file_to_list_strip(bug_ids_or_range_file_path)
        for bug_id in bug_ids:
            b_name, b_id = bug_id.split("_")
            patch_path = os.path.join(patch_dir, dataset_name, b_name, b_id)
            for apr_tool in apr_tools:
                apr_patch_dir = os.path.join(patch_dir, dataset_name, b_name, b_id, apr_tool)
                apr_patch_dir = os.path.join(apr_patch_dir, os.listdir(apr_patch_dir)[0])
                assert os.path.exists(apr_patch_dir)
                if "result.json" not in os.listdir(apr_patch_dir):
                    continue
                else:
                    apr_patch_path = os.path.join(apr_patch_dir, "result.json")
                    result_json = Json_util.read_json(apr_patch_path)
                    patches = result_json["patches"]
                    if len(patches) == 0:
                        continue
                    else:
                        patch = patches[-1]["patch"]
                        patch_and_test(dataset_name, bug_id, apr_tool, dataset, patch)

def preprocess_patch1(bug_id, apr_tool, patch_dir):
    b_name, b_id = bug_id.split("_")
    apr_patch_dir = os.path.join(patch_dir, dataset_name, b_name, b_id, apr_tool)
    apr_patch_dir = os.path.join(apr_patch_dir, os.listdir(apr_patch_dir)[0])
    assert os.path.exists(apr_patch_dir)
    if "result.json" not in os.listdir(apr_patch_dir):
        return ""
    else:
        apr_patch_path = os.path.join(apr_patch_dir, "result.json")
        result_json = Json_util.read_json(apr_patch_path)
        patches = result_json["patches"]
        if len(patches) == 0:
            return ""
        else:
            patch = patches[-1]["patch"]
            return patch

def preprocess_patch2(bug_id, apr_tool, patch_dir):
    for m in os.listdir(patch_dir):
        mpatches = os.path.join(patch_dir, m, "patches")
        for patch in os.listdir(mpatches):
            if bug_id == patch.replace(".diff", ""):
                patch_content = File_util.read_file(os.path.join(mpatches, patch))
                if f"{apr_tool} {bug_id}" in patch_content:
                    patch_content = patch_content[patch_content.index(f"{apr_tool} {bug_id}"):]
                    sindex, eindex = patch_content.index("---"), patch_content.index("\n\n\n")
                    patch_content = patch_content[sindex:eindex]
                    patch_content_list = patch_content.split("\n")
                    for i, pcl in enumerate(patch_content_list):
                        if not (pcl.startswith("@@") or pcl.startswith("---") or pcl.startswith("+++") \
                            or pcl.startswith("-") or pcl.startswith("+")):
                            patch_content_list[i] = " "*13 + pcl
                    patch_content = "\n".join(patch_content_list)
                    return patch_content + "\n\n\n"
                else:
                    break
            else:
                continue
    return ""

def run_dataset2(datasets, apr_tools, patch_dir):
    for dataset_name in datasets:
        dataset = Dataset_factory.DatasetFactory().create_dataset(dataset_name)

        bug_ids_or_range_file_path = Dataset_util.get_bug_ids_path(dataset_name)
        Config.TMP_OUTPUT_DIR = os.path.join(Config.PARENT_PROJECT_PATH, f"patch_explorer_{dataset_name}")
        Config.rerun_dataset = False
        # bug_ids = Dataset_util.get_bug_ids_from_txt(bug_ids_or_range_file_path)
        bug_ids = File_util.read_file_to_list_strip(bug_ids_or_range_file_path)
        for bug_id in bug_ids:
            for apr_tool in apr_tools:
                patch = preprocess_patch2(bug_id, apr_tool, patch_dir)
                if patch == "": continue
                patch_and_test(dataset_name, bug_id, apr_tool, dataset, patch)

if __name__ == "__main__":
    # datasets = ["Defects4J", "Bears"]
    # apr_tools = ["Arja", "DynaMoth", "Nopol"]
    # patch_dir = "/home/apr/tools/RepairThemAll_experiment/results"
    # run_dataset(datasets, apr_tools, patch_dir)

    datasets = ["Defects4J"]
    apr_tools = ["dynamoth_1", "nopol_1"]
    patch_dir = "/mnt/data/bias_validation_2021/current_result_data/results_defects4j/parsed_results"
    run_dataset2(datasets, apr_tools, patch_dir)
