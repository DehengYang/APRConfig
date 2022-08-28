import re, os, json
import Config
from utils import File_util, List_util

from dataset import Dataset_factory

if __name__ == "__main__":
    output_dir = os.path.join(Config.PROJECT_PATH, "patch_explorer", "output")
    # output_dir = os.path.join(Config.PROJECT_PATH, "patch_explorer", "output2")
    # output_dir = os.path.join(Config.PROJECT_PATH, "patch_explorer", "output_for_bears_dynamoth")
    non_plausible_patches = {
        "compile error": [],
        "pass partial nt, pass all pt": [],
        "not pass nt, pass all pt": [],
        "pass nt, not pass all pt": []
    }
    statistics = {}
    for apr_tool in os.listdir(output_dir):
        statistics[apr_tool] = {}
        for dataset in os.listdir(os.path.join(output_dir, apr_tool)):
            dataset_instance = Dataset_factory.DatasetFactory().create_dataset(dataset)

            statistics[apr_tool][dataset] = {
                "compile error": 0,
                "pass partial nt, pass all pt": 0,
                "not pass nt, pass all pt": 0,
                "pass nt, not pass all pt": 0,
                "all patches": 0
            }
            for bug_result in os.listdir(os.path.join(output_dir, apr_tool, dataset)):
                print(apr_tool, dataset, bug_result)
                # 0 -> plausible patch
                # 1 -> compile error
                # 2 -> pass partial nt, pass all pt
                # 3 -> not pass nt, pass all pt
                # 4 -> pass nt, not pass all pt
                np_type = 0
                bug_path = os.path.join(output_dir, apr_tool, dataset, bug_result)
                bug_output = File_util.read_file(bug_path)
                prev_test, after_test = bug_output[:bug_output.index("Test result after patching")], \
                    bug_output[bug_output.index("Test result after patching"):]
                prev_failing_tests, after_failing_tests = [], []
                if dataset == "Defects4J":
                    find = re.search("Failing tests: (\d+)", after_test)
                    if find == None:
                        np_type = 1
                    else:
                        num_failedtest = int(find.groups()[0])
                        pattern = re.compile('- (.*)::(.*)')
                        matches = re.findall(pattern, prev_test)
                        prev_failing_tests = []
                        for match in matches:
                            prev_failing_tests.append(f"{match[0]}#{match[1]}")
                        prev_failing_tests = list(set(prev_failing_tests))
                        matches = re.findall(pattern, after_test)
                        after_failing_tests = []
                        for match in matches:
                            after_failing_tests.append(f"{match[0]}#{match[1]}")
                        after_failing_tests = list(set(after_failing_tests))
                        # print(num_failedtest, len(after_failing_tests))
                        assert num_failedtest == len(after_failing_tests)
                else:  # bears
                    bug = dataset_instance.get_bug(bug_result[:-len(".txt")])
                    bug_failing_tests = dataset_instance.failing_test_methods_2(bug)  #failing_tests

                    # prev_test = prev_test[prev_test.index("Results"):]
                    # prev_test = prev_test[:prev_test.index("Tests run:")]
                    # after_test = after_test[after_test.index("Results"):]
                    # after_test = after_test[:after_test.index("Tests run:")]
                    # pattern = re.compile('  (\S*?):(.*)')
                    pattern = re.compile('(\S*?)  Time elapsed:(.*)<<< (\S*)!')
                    matches = re.findall(pattern, prev_test)
                    prev_failing_tests = []
                    for match in matches:
                        prev_failing_tests.append(match[0])
                    prev_failing_tests = list(set(prev_failing_tests))
                    # remove fake fail tests
                    fake_fail_tests = List_util.get_uniq_in_src(prev_failing_tests, bug_failing_tests)
                    prev_failing_tests.clear()
                    prev_failing_tests.extend(bug_failing_tests)

                    matches = re.findall(pattern, after_test)
                    after_failing_tests = []
                    for match in matches:
                        after_failing_tests.append(match[0])
                    after_failing_tests = list(set(after_failing_tests))

                    after_result = after_test[after_test.index("Results"):]
                    find = re.findall("  (\S*?):(.*)", after_result)
                    if len(find) != len(after_failing_tests):
                        import pdb
                        pdb.set_trace()
                    assert len(find) == len(after_failing_tests)

                    # remove fake fail tests
                    after_failing_tests = List_util.get_uniq_in_src(after_failing_tests, fake_fail_tests)

                assert len(prev_failing_tests) > 0 or np_type == 1
                # flag1 -> some ft fail to pass
                # flag2 -> some pt fail to pass
                # flag3 -> all ft fail to pass
                flag1, flag2, flag3 = False, False, True
                for pft in prev_failing_tests:
                    if pft in after_failing_tests:
                        flag1 = True
                    else:
                        flag3 = False
                for aft in after_failing_tests:
                    if aft not in prev_failing_tests:
                        flag2 = True
                        break
                # 0 -> plausible patch
                # 1 -> compile error
                # 2 -> pass partial nt, pass all pt
                # 3 -> not pass nt, pass all pt
                # 4 -> pass nt, not pass all pt
                if (flag1 and not flag3) and not flag2:
                    np_type = 2
                elif (flag1 and flag3) and not flag2:
                    np_type = 3
                elif (not flag1 and not flag3) and flag2:
                    np_type = 4

                if np_type == 1:
                    non_plausible_patches["compile error"].append(
                        f"{apr_tool}_{dataset}_{bug_result.replace('.txt', '')}")
                    statistics[apr_tool][dataset]["compile error"] += 1
                elif np_type == 2:
                    non_plausible_patches["pass partial nt, pass all pt"].append(
                        f"{apr_tool}_{dataset}_{bug_result.replace('.txt', '')}")
                    statistics[apr_tool][dataset]["pass partial nt, pass all pt"] += 1
                elif np_type == 3:
                    non_plausible_patches["not pass nt, pass all pt"].append(
                        f"{apr_tool}_{dataset}_{bug_result.replace('.txt', '')}")
                    statistics[apr_tool][dataset]["not pass nt, pass all pt"] += 1
                elif np_type == 4:
                    non_plausible_patches["pass nt, not pass all pt"].append(
                        f"{apr_tool}_{dataset}_{bug_result.replace('.txt', '')}")
                    statistics[apr_tool][dataset]["pass nt, not pass all pt"] += 1
                statistics[apr_tool][dataset]["all patches"] += 1

    output_json = {"Non-plausible Patches Content": non_plausible_patches, "Statistics": statistics}
    File_util.write_to_file(os.path.join(Config.PROJECT_PATH, "patch_explorer", "non-plausible-patch.json"), json.dumps(output_json))

    # File_util.write_to_file(os.path.join(Config.PROJECT_PATH, "patch_explorer", "non-plausible-patch2.json"), json.dumps(output_json))

    # File_util.write_to_file(
    #     os.path.join(Config.PROJECT_PATH, "patch_explorer", "non-plausible-patch_bears_dynamoth.json"),
    #     json.dumps(output_json))
