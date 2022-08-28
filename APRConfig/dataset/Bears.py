# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/13 21:11:34
@Author     : apr
'''

import logging
import os
import json

import Dataset
from dataset import Bug
import Config
from utils import Cmd_util

logger = logging.getLogger()


class Bears(Dataset.Dataset):
    def __init__(self):
        self.name = self.__class__.__name__.lower()
        super().__init__(self.name)
        

    def get_bug(self, bug_id):
        bug_id = bug_id.replace("_", "-")
        separator = "-"
        splitted = bug_id.split(separator)

        project = splitted[0]
        if len(splitted) < 3:
            project = "-".join(splitted[:-1])
        else:
            patched = splitted[-1]
            buggy = splitted[-2]
            project = "-".join(splitted[:-2])

        for bug in self.get_bugs():
            if bug.project.lower() == project.lower():
                if len(splitted) < 3 or bug.bug_id.lower() == (
                        "%s-%s" % (buggy, patched)):
                    return bug
        return None

    def _get_info_path(self):
        return os.path.join(Config.DATASET_INFO_PATH, "bears")

    def _get_dataset_path(self):
        return os.path.join(Config.DATASET_PATH, "bears")

    def get_bugs(self):
        if self.bugs is not None:
            return self.bugs

        self.bugs = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as f:
            data = json.load(f)
            for b in data:
                (organization, project) = b["repository"]["url"].replace(
                    "https://github.com/", "").split("/")
                self.bugs += [
                    Bug.Bug(
                        self, "%s-%s" % (organization, project),
                        "%s-%s" % (b['builds']['buggyBuild']['id'],
                                   b['builds']['fixerBuild']['id']), b['diff'])
                ]
        return self.bugs

    def _get_project_info(self, bug):
        try:
            return bug.maven_info
        except AttributeError:
            pass
        local_working_directory = bug.get_working_dir()
        pom_path = bug.info['reproductionBuggyBuild']['projectRootPomPath']
        buggy_build_id = bug.info['builds']['buggyBuild']['id']
        pom_path = pom_path.partition(str(buggy_build_id))[2]
        pom_path = pom_path.replace("/pom.xml", "")
        pom_path = pom_path.replace("/", "", 1)
        if pom_path:
            local_working_directory = os.path.join(local_working_directory,
                                                   pom_path)
        cmd = """cd %s;
mvn com.github.tdurieux:project-config-maven-plugin:1.0-SNAPSHOT:info -q;
""" % (local_working_directory)

        info = json.loads(Cmd_util.run_cmd(cmd))
        bug.maven_info = info
        return info

    def checkout(self, bug, output_dir):
        self.set_bug_working_dir(bug, output_dir)

        # branch id: u'webfirmframework-wff-453188520-453188718'
        branch_id = "%s-%s" % (bug.project, bug.bug_id)

        cmd = f"""
        cd {self._get_dataset_path()}; 
        git reset .; 
        git checkout -- .;
        git clean -x -d --force; 
        git checkout -f master; 
        git checkout -f {branch_id}
        """

        Cmd_util.run_cmd(cmd)

        # '/mnt/recursive-repairthemall/RepairThemAll/script/../benchmarks/bears/bears.json'
        # at this time, the benchmarks/bears/ are changed into bug-id version
        bears_info_path = os.path.join(self._get_dataset_path(), "bears.json")
        with open(bears_info_path) as fd:
            bug.info = json.load(fd)

        cmd = f"""
        cd {self._get_dataset_path() };
        git log --format=format:%H --grep='Changes in the tests';
        """
        bug_commit = Cmd_util.run_cmd(cmd)

        if len(bug_commit) == 0:
            # if no bug_commit, then choose bug commit ID with message containing "Bug commit"
            cmd = f"cd {self._get_dataset_path()}; git log --format=format:%H --grep='Bug commit'"
            bug_commit = Cmd_util.run_cmd(cmd)

        # u'cd /mnt/recursive-repairthemall/RepairThemAll/script/../benchmarks/bears;
        # \ngit checkout -f b0706752ab6c822c6ab9758eb6cae8923b49e700;
        # \ncp -r . /mnt/workingDir/Bears_webfirmframework-wff_453188520-453188718'
        cmd = f"""cd {self._get_dataset_path()};
            git checkout -f {bug_commit};
            cp -r . {bug.get_working_dir()}"""

        Cmd_util.run_cmd(cmd)
        pass

    def compile(self, bug):
        local_working_directory = bug.get_working_dir()
        pom_path = bug.info['reproductionBuggyBuild'][
            'projectRootPomPath']  #./workspace/INRIA/spoon/211342085/pom.xml
        buggy_build_id = bug.info['builds']['buggyBuild']['id']  # 211342085
        pom_path = pom_path.partition(str(buggy_build_id))[2]
        pom_path = pom_path.replace("/pom.xml", "")
        pom_path = pom_path.replace("/", "", 1)  #u'wffweb
        if pom_path:
            local_working_directory = os.path.join(
                local_working_directory, pom_path
            )  # obtain pom.xml path. u'/mnt/workingDir/Bears_webfirmframework-wff_453188520-453188718/wffweb'
        # export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
        cmd = f"""
            cd {local_working_directory};
            

            mvn -Dhttps.protocols=TLSv1.2 install -V -B -DskipTests -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true; 
            
            mvn -Dhttps.protocols=TLSv1.2 test -DskipTests -V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Denforcer.skip=true;
            
            mvn dependency:build-classpath -Dmdep.outputFile="classpath.info";
            """
        Cmd_util.run_cmd(cmd)

    def run_test(self, bug):
        local_working_directory = bug.get_working_dir()
        pom_path = bug.info['reproductionBuggyBuild']['projectRootPomPath']
        buggy_build_id = bug.info['builds']['buggyBuild']['id']
        pom_path = pom_path.partition(str(buggy_build_id))[2]
        pom_path = pom_path.replace("/pom.xml", "")
        pom_path = pom_path.replace("/", "", 1)
        if pom_path:
            local_working_directory = os.path.join(local_working_directory,
                                                   pom_path)
        cmd = f"""cd {local_working_directory};
            export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true; 
            rm -rf .git; git init; git commit -m 'init' --allow-empty;

            mvn test -V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Djacoco.skip=true -Denforcer.skip=true;
            """
        Cmd_util.run_cmd(cmd)

    def failing_tests(self, bug):
        tests = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace(
                    "https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'],
                                    b['builds']['fixerBuild']['id'])

                if bug.project.lower() == project_id.lower(
                ) and bug.bug_id.lower() == bug_id.lower():
                    for t in b['tests']['failingClasses']:
                        tests += [t['testClass']]
                    return tests
        return tests

    def failing_test_methods(self, bug):
        tests = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace(
                    "https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'],
                                    b['builds']['fixerBuild']['id'])

                if bug.project.lower() == project_id.lower(
                ) and bug.bug_id.lower() == bug_id.lower():
                    for t in b['tests']['failureDetails']:
                        tests += [t['testClass'] + "#" + t['testMethod']]
                    return tests
        return tests

    def failing_module(self, bug):
        failing_module = bug.info['tests']['failingModule']
        buggy_build_id = str(bug.info['builds']['buggyBuild']['id'])
        try:
            index_build = failing_module.index(buggy_build_id + "/")
            return failing_module[index_build + len(buggy_build_id) + 1:]
        except ValueError:
            return "root"

    def source_folders(self, bug):
        folders = []

        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = module['baseDir'].replace(
                bug.get_working_dir() + '/', '')
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self.abs_to_rel(bug.get_working_dir(),
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
                return self.abs_to_rel(bug.get_working_dir(), module['tests'])

        return folders

    def bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self.abs_to_rel(bug.get_working_dir(),
                                       module['binSources'])
        return []

    def test_bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module[
                    'name']:
                return self.abs_to_rel(bug.get_working_dir(),
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

        # return ":".join(deps)

        # add junit jar
        classpath = ":".join(deps)
        if "/junit-4" not in classpath and "/junit-3" not in classpath:
            deps += [
                os.path.join(Config.M2_REPO, "junit", "junit", "4.12",
                             "junit-4.12.jar")
            ]
            deps += [
                os.path.join(Config.M2_REPO, "org", "hamcrest",
                             "hamcrest-core", "1.3", "hamcrest-core-1.3.jar")
            ]

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

    def compliance_level(self, bug):
        info = self._get_project_info(bug)
        return info['complianceLevel']

    def abs_to_rel(self, root, folders):
        if root[-1] != '/':
            root += "/"
        output = []
        for folder in folders:
            output.append(folder.replace(root, ""))
        return output

    def get_patch_diff(self, bug):
        assert bug.get_patch_diff() is not None
        return bug.get_patch_diff()