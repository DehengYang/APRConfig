# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/12 17:00:25
@Author     : apr
'''

import logging
import os
import json
import re, shutil

import Dataset
from dataset import Bug
import Config
from utils import Cmd_util, File_util

logger = logging.getLogger()


class Quixbugs(Dataset.Dataset):
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        super().__init__(self.name)

    def _get_dataset_path(self):
        return os.path.join(Config.DATASET_PATH, "QuixBugs")

    def get_bugs(self):
        if self.bugs is not None:
            return self.bugs
        self.bugs = []
        dataset_path = os.path.join(self._get_dataset_path(), "java_programs")
        for program in os.listdir(dataset_path):
            project_path = os.path.join(dataset_path, program)
            program = program.replace(".java", "")
            if not os.path.isfile(project_path) or program != program.upper():
                continue
            bug = Bug.Bug(self, program, "")
            self.bugs += [bug]
        return self.bugs

    def get_bug(self, bug_id):
        if bug_id[-1] == '_':
            bug_id = bug_id[:-1]
        for bug in self.get_bugs():
            if bug_id.lower() == bug.project.lower():
                return bug
        return None

    def get_info_path(self):
        return os.path.join(Config.DATASET_INFO_PATH, "QuixBugs")

    def checkout(self, bug, output_dir):
        """
        output_dir is the parent dir of the bug working dir
        """
        self.set_bug_working_dir(bug, output_dir)

        dataset_path = os.path.join(self._get_dataset_path(), "java_programs")
        test_path = os.path.join(self._get_dataset_path(), "java_testcases",
                                 "junit")

        source_path = os.path.join(bug.get_working_dir(), "src", "main",
                                   "java")
        test_dst_path = os.path.join(bug.get_working_dir(), "src", "test",
                                     "java")

        if not os.path.exists(test_dst_path):
            os.makedirs(test_dst_path)
        if not os.path.exists(source_path):
            os.makedirs(source_path)

        shutil.copy(os.path.join(self.get_info_path(), "pom.xml"),
                    bug.get_working_dir())
        for program in os.listdir(dataset_path):
            project_path = os.path.join(dataset_path, program)
            program = program.replace(".java", "")
            if not os.path.isfile(
                    project_path
            ) or ".class" in program or program == program.upper():
                continue
            shutil.copy(project_path, source_path)

        shutil.copy(os.path.join(dataset_path, "%s.java" % bug.project),
                    source_path)
        test_file_path = os.path.join(test_path, "%s_TEST.java" % bug.project)
        if os.path.exists(test_file_path):
            self.prepare_test(bug, test_dst_path, test_file_path)
        else:
            test_file_path = os.path.join(self.get_info_path(),
                                          "%s_TEST.java" % bug.project)
            if os.path.exists(test_file_path):
                self.prepare_test(bug, test_dst_path, test_file_path)
        shutil.copy(os.path.join(test_path, "QuixFixOracleHelper.java"),
                    test_dst_path)

        # TODO create folders
        # TODO copy src, test and QuixFixOracleHelper
        pass

    def prepare_test(self, bug, test_dst_path, test_file_path):
        with open(test_file_path) as fd1:
            content = fd1.read().replace("%s_TEST" % bug.project,
                                         "%s_Test" % bug.project)
            with open(
                    os.path.join(test_dst_path, "%s_Test.java" % bug.project),
                    "w+") as fd2:
                fd2.write(content)

    def compile(self, bug):
        cmd = "cd %s; export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; mvn -Dhttps.protocols=TLSv1.2 test -DskipTests;" % (
            bug.get_working_dir())
        Cmd_util.run_cmd(cmd)
        pass

    def run_test(self, bug):
        cmd = "cd %s; export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; mvn -Dhttps.protocols=TLSv1.2 test;" % (
            bug.get_working_dir())
        Cmd_util.run_cmd(cmd)
        pass

    def failing_tests(self, bug):
        tests = ["java_testcases.junit.%s_Test" % bug.project]
        return tests

    # todo
    def failing_module(self, bug):
        return ""

    def source_folders(self, bug):
        return [os.path.join("src", "main", "java")]

    def test_folders(self, bug):
        return [os.path.join("src", "test", "java")]

    def bin_folders(self, bug):
        return [os.path.join("target", "classes")]

    def test_bin_folders(self, bug):
        return [os.path.join("target", "test-classes")]

    def failing_test_methods(self, bug):
        # TODO
        return []

    def classpath(self, bug):
        classpath = []
        classpath.append(
            os.path.join(Config.M2_REPO, "junit", "junit", "4.11",
                         "junit-4.11.jar"))
        classpath.append(
            os.path.join(Config.M2_REPO, "org", "hamcrest", "hamcrest-core",
                         "1.3", "hamcrest-core-1.3.jar"))

        classpath = ":".join(classpath)

        # add bin folders of src and tests of the buggy program
        bin_folder_path = os.path.join(bug.get_working_dir(),
                                       self.bin_folders(bug)[0])
        test_bin_folder_path = os.path.join(bug.get_working_dir(),
                                            self.test_bin_folders(bug)[0])
        if bin_folder_path not in classpath:
            classpath = bin_folder_path + ":" + classpath
        if test_bin_folder_path not in classpath:
            classpath = test_bin_folder_path + ":" + classpath
        return classpath

    def compliance_level(self, bug):
        return 8

    def get_patch_diff(self, bug):
        buggy_file = os.path.join(self._get_dataset_path(), "java_programs",
                                  bug.project + ".java")
        fixed_file = os.path.join(self._get_dataset_path(),
                                  "correct_java_programs",
                                  bug.project + ".java")
        patch_diff = Cmd_util.run_cmd(f"diff -Naur {buggy_file} {fixed_file}")
        return patch_diff