# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/12 17:00:25
@Author     : apr
'''

import logging, os, json, shutil

import Dataset
from dataset import Bug
import Config
from utils import Cmd_util, File_util

logger = logging.getLogger()


class Bugsdotjar(Dataset.Dataset):
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        super().__init__(self.name)

    def get_bug(self, bug_id):
        separator = "-"
        if "_" in bug_id:
            separator = "_"
        split = bug_id.split(separator)
        commit = split[-1]
        project = "-".join(split[:-1])
        for bug in self.get_bugs():
            if project.lower() in bug.project.lower():
                if bug.bug_id[:8].lower() == commit[:8]:
                    return bug
        return None

    def _get_dataset_path(self):
        return os.path.join(Config.DATASET_PATH, "Bug-dot-jar")

    def get_bugs(self):
        if self.bugs is not None:
            return self.bugs
        self.bugs = []
        dataset_path = os.path.join(self._get_dataset_path(), "data")
        for project in os.listdir(dataset_path):
            project_path = os.path.join(dataset_path, project)
            if os.path.isfile(project_path):
                continue
            for commit in os.listdir(project_path):
                commit_path = os.path.join(project_path, commit)
                if not os.path.isfile(commit_path) or commit[-5:] != ".json":
                    continue
                bug = Bug.Bug(self, project.title(), commit[:-5])
                self.bugs += [bug]
        return self.bugs

    def checkout(self, bug, output_dir):
        self.set_bug_working_dir(bug, output_dir)

        dataset_path = os.path.join(self._get_dataset_path(), "data",
                                    bug.project.lower(),
                                    "%s.json" % bug.bug_id[:8])
        with open(dataset_path) as fd:
            data = json.load(fd)
            project = bug.project.split("-")[-1].upper()
            branch_id = "bugs-dot-jar_%s-%s_%s" % (project, data['jira_id'],
                                                   data['commit'])
            cmd = "cd " + os.path.join(
                self._get_dataset_path(), "repositories", bug.project.lower()
            ) + "; git reset .; git checkout -- .; git clean -x -d --force; git checkout master; git checkout " + branch_id

            Cmd_util.run_cmd(cmd)

            if os.path.exists(bug.get_working_dir()):
                File_util.rm_dir(bug.get_working_dir())
            shutil.copytree(
                os.path.join(self._get_dataset_path(), "repositories",
                             bug.project.lower()), bug.get_working_dir())
        pass

    def compile(self, bug):
        java_version = os.path.join(Config.JAVA8_HOME, '..')
        if bug.project == "Wicket":
            java_version = os.path.join(Config.JAVA7_HOME, '..')
        cmd = """cd %s;
        export JAVA_HOME="%s";
        export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
        mvn -Dhttps.protocols=TLSv1.2 install -V -B -DskipTests -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true; 
        mvn -Dhttps.protocols=TLSv1.2 test -DskipTests -V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Dhttps.protocols=TLSv1.2;
        mvn dependency:build-classpath -Dmdep.outputFile="classpath.info";
        """ % (bug.get_working_dir(), java_version)
        Cmd_util.run_cmd(cmd)
        pass

    def run_test(self, bug):
        java_version = os.path.join(Config.JAVA8_HOME, '..')
        if bug.project == "Wicket":
            java_version = os.path.join(Config.JAVA7_HOME, '..')
        cmd = """cd %s; 
        export JAVA_HOME="%s";
        export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
        rm -rf .git; git init; git commit -m 'init' --allow-empty;
        mvn -Dhttps.protocols=TLSv1.2 test -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Djacoco.skip=true -Dhttps.protocols=TLSv1.2;""" % (
            bug.get_working_dir(), java_version)
        Cmd_util.run_cmd(cmd)
        pass

    def failing_module(self, bug):
        info = self._get_project_info(bug)
        failing_tests = self.failing_tests(bug)
        path_failing_test = failing_tests[0].replace(".", "/") + ".java"

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            for test_folder in module['tests']:
                if os.path.exists(os.path.join(test_folder,
                                               path_failing_test)):
                    return module_name
        return "root"

    def failing_tests(self, bug):
        dataset_path = os.path.join(self._get_dataset_path(), "data",
                                    bug.project.lower(),
                                    "%s.json" % bug.bug_id[:8])
        with open(dataset_path) as fd:
            data = json.load(fd)
            return data['failing_tests']

    def source_folders(self, bug):
        folders = []

        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self._abs_to_rel(bug.get_working_dir(),
                                        module['sources'])
        return folders

    def test_folders(self, bug):
        folders = []

        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self._abs_to_rel(bug.get_working_dir(), module['tests'])

        return folders

    def bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self._abs_to_rel(bug.get_working_dir(),
                                        module['binSources'])
        return []

    def test_bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self._abs_to_rel(bug.get_working_dir(),
                                        module['binTests'])
        return []

    def classpath(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        deps = []

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module != module_name and failing_module != module[
                    'name']:
                deps += module['binSources']
        deps += info['classpath']

        classpath = ":".join(deps)
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

    def failing_test_methods(self, bug):
        # TODO
        return []

    def compliance_level(self, bug):
        return 7

    def _abs_to_rel(self, root, folders):
        if root[-1] != '/':
            root += "/"
        output = []
        for folder in folders:
            output.append(folder.replace(root, ""))
        return output

    def get_patch_diff(self, bug):
        assert bug.get_working_dir() is not None, "please checkout first."
        diff_path = os.path.join(bug.get_working_dir(), ".bugs-dot-jar",
                                 "developer-patch.diff")
        assert os.path.exists(diff_path)

        return File_util.read_file(diff_path)