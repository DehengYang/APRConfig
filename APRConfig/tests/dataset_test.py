# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/12 16:23:50
@Author     : apr
'''

# import sys
# sys.path.append(".")

import unittest, os, json

# import python.dataset
from dataset import Dataset_main
from dataset import Dataset_factory
import Config


class DatasetTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.working_dir = Config.TMP_WORKING_DIR

    def test_defects4j(self):
        input_args = ["-d", "defects4j", "-b", "chart-1"]
        dataset, bug = self.get_dataset_bug(input_args)

        test_methods = dataset.failing_test_methods(bug)
        self.assertEqual(
            test_methods[0],
            'org.jfree.chart.renderer.category.junit.AbstractCategoryItemRendererTests#test2947660'
        )

    def test_bears(self):
        input_args = ["-d", "bears", "-b", "INRIA-spoon-211342085-211425556"]
        input_args = [
            "-d", "bears", "-b", "webfirmframework-wff_453188520-453188718"
        ]
        dataset, bug = self.get_dataset_bug(input_args)

        bugs = dataset.get_bugs()
        for cur_bug in bugs:
            print(f"{cur_bug.name} {cur_bug.project} {cur_bug.bug_id}")

        # dataset.compile(bug)
        # dataset.run_test(bug)
        dataset.failing_tests(bug)
        test_methods = dataset.failing_test_methods(bug)
        self.assertTrue(len(test_methods) == 1)

    def test_bugsdotjar(self):
        input_args = ["-d", "Bugsdotjar", "-b", "Wicket-f45ce896"]
        dataset, bug = self.get_dataset_bug(input_args)
        dataset.compile(bug)
        dataset.run_test(bug)
        dataset.failing_tests(bug)

    def test_quixbugs(self):
        input_args = ["-d", "quixbugs", "-b", "LCS_LENGTH"]
        dataset, bug = self.get_dataset_bug(input_args)
        dataset.compile(bug)
        dataset.run_test(bug)
        dataset.failing_tests(bug)

    def get_dataset_bug(self, input_args):
        args = Dataset_main.init_parser(input_args)
        dataset, bug = Dataset_main.parse_arg(args)

        if args.working_dir is None:
            args.working_dir = self.working_dir

        # checkout
        dataset.checkout(bug, args.working_dir)
        # dataset.compile(bug)
        # dataset.run_test(bug)
        # dataset.failing_tests(bug)
        # test_methods = dataset.failing_test_methods(bug)
        return dataset, bug

    # find and fix a bug
    def test_bears_failingclasses(self):
        bears = Dataset_factory.DatasetFactory().create_dataset("bears")
        with open(os.path.join(bears._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace(
                    "https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'],
                                    b['builds']['fixerBuild']['id'])

                if len(b['tests']['failingClasses']) > 1:
                    print(f"{project_id} {bug_id}")

    def test_get_src_dir(self):
        input_args = [
            "-d", "bears", "-b", "webfirmframework-wff_453188520-453188718"
        ]
        # input_args = ["-d", "Bugsdotjar", "-b", "Wicket-f45ce896"]
        # input_args = ["-d", "defects4j", "-b", "chart-1"]
        # input_args = ["-d", "quixbugs", "-b", "LCS_LENGTH"]

        dataset, bug = self.get_dataset_bug(input_args)
        patch_diff = dataset.get_patch_diff(bug)

        buggylocs = dataset.get_buggy_locs(bug, patch_diff)
        print(f"locs:{buggylocs}")
        print(f'patch diff: {patch_diff}')


if __name__ == '__main__':
    # run all test cases
    # unittest.main()

    # run a single test case
    singletest = unittest.TestSuite()
    # singletest.addTest(DatasetTest('test_bears'))
    # singletest.addTest(DatasetTest('test_bears_failingclasses'))
    # singletest.addTest(DatasetTest('test_bugsdotjar'))
    # singletest.addTest(DatasetTest('test_quixbugs'))
    singletest.addTest(DatasetTest('test_get_src_dir'))
    unittest.TextTestRunner().run(singletest)