# How to Extend APRConfig to Support More Datasets, Fault Localizers, Patch Generation Algorithms, and Patch Validators?

- [How to Extend APRConfig to Support More Datasets, Fault Localizers, Patch Generation Algorithms, and Patch Validators?](#how-to-extend-aprconfig-to-support-more-datasets-fault-localizers-patch-generation-algorithms-and-patch-validators)
  - [1. Adding Support for a New Dataset](#1-adding-support-for-a-new-dataset)
  - [2. Adding Support for a New Fault Localizer](#2-adding-support-for-a-new-fault-localizer)
  - [3. Adding Support for a New Patch Generation Algorithm](#3-adding-support-for-a-new-patch-generation-algorithm)
  - [4. Adding Support for a New Patch Validator](#4-adding-support-for-a-new-patch-validator)
  - [5. Acknowledgement](#5-acknowledgement)

Publicly executable frameworks that integrate multiple datasets or APR tools could serve as an infrastructure and benefits follow-up research in the community. <!-- We notice that in the APR community, there is still one such executable framework (i.e., [RepairThemAll](https://github.com/program-repair/RepairThemAll)) for general bugs in Java programs.  --> Here We aim to contribute a new executable framework to facilitate a fairer APR evaluation. While it costs much engineering effort to construct such an executable framework, we plan to continuously maintain this repository. Accordingly, we provide the guideline on how to extend APRConfig with more datasets, fault localizers, patch generation algorithms, and patch validators. Any question or contribution is much welcomed.

## 1. Adding Support for a New Dataset

1. Add the dataset directory into the `datasets` folder.

2. Modify the `APRConfig/dataset/Dataset_factory.py` as highlighted in the following comments:

```python
import logging

import Defects4j
import Bears # 1. add import
import Quixbugs

logger = logging.getLogger()


class DatasetFactory():
    def create_dataset(self, dataset_name):
        if dataset_name.lower() == "defects4j":
            return Defects4j.Defects4j()
        elif dataset_name.lower() == "bears": # 2. add an else if stmt
            return Bears.Bears()
        elif dataset_name.lower() == "quixbugs":
            return Quixbugs.Quixbugs()
        else:
            raise Exception(f"unknown dataset name: {dataset_name}")
```

3. Add a new file (e.g., `Bears.py` for the Bears dataset) into the `APRConfig/dataset/` folder. The content is:

```python
import logging
import os
import json
import shutil

import Dataset
from dataset import Bug, Bears_util
import Config
from utils import Cmd_util, File_util

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
                if len(splitted) < 3 or bug.bug_id.lower() == ("%s-%s" % (buggy, patched)):
                    return bug
        return None

    def checkout_and_compile(self, bug, working_dir, bug_pool_dir):
        self.checkout(bug, working_dir)
        self.compile(bug)

        # level = self.compliance_level(bug)

        File_util.rm_dir(bug_pool_dir)
        shutil.copytree(working_dir, bug_pool_dir)

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
                (organization, project) = b["repository"]["url"].replace("https://github.com/", "").split("/")
                self.bugs += [
                    Bug.Bug(self, "%s-%s" % (organization, project),
                            "%s-%s" % (b['builds']['buggyBuild']['id'], b['builds']['fixerBuild']['id']), b['diff'])
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
            local_working_directory = os.path.join(local_working_directory, pom_path)
        cmd = f"""
        export JAVA_HOME="{os.path.join(Config.JAVA8_HOME, '..')}";
        export PATH="{Config.MAVEN_BIN}:$PATH";
        cd {local_working_directory};
        mvn com.github.tdurieux:project-config-maven-plugin:1.0-SNAPSHOT:info -q;
        """

        info = json.loads(Cmd_util.run_cmd(cmd))
        bug.maven_info = info
        return info

    def checkout_fixed(self, bug, fixed_dir):
        if not fixed_folder.endswith(bug.name):
            fixed_dir = os.path.join(fixed_dir, bug.name)
        fixed_dir = self.set_bug_working_dir(bug, fixed_dir, True)

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

        bears_info_path = os.path.join(self._get_dataset_path(), "bears.json")
        with open(bears_info_path) as fd:
            bug.info = json.load(fd)

        cmd = f"""
        cd {self._get_dataset_path() };
        git log --format=format:%H --grep='Human patch from';
        """
        fixed_commit = Cmd_util.run_cmd(cmd)

        if len(fixed_commit) == 0:
            raise Exception("fixed_commit should not be null.")
        cmd = f"""cd {self._get_dataset_path()};
            git checkout -f {fixed_commit};
            cp -r . {bug.get_working_dir()}"""

        Cmd_util.run_cmd(cmd)

        return fixed_dir

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

    def compile(self, bug, early_exit=False):
        """
        early_exit is for checkout.py
        """
        # deal with bears compilation errors
        compiler_error_bugs = File_util.read_file_to_list_strip(
            os.path.join(Config.PROJECT_PATH, 'bugs_info', Config.bears_with_compile_error_path))
        if f'{bug.project}-{bug.bug_id}' in compiler_error_bugs:
            pom_file_path = os.path.join(bug.get_working_dir(), 'pom.xml')
            assert os.path.exists(pom_file_path)
            Bears_util.change_pom_for_compilation_error_bug(pom_file_path)
            if early_exit:
                return

        local_working_directory = bug.get_working_dir()
        pom_path = bug.info['reproductionBuggyBuild']['projectRootPomPath']  #./workspace/INRIA/spoon/211342085/pom.xml
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
        export JAVA_HOME={os.path.join(Config.JAVA8_HOME, '..') };
        export PATH="{Config.MAVEN_BIN}:$PATH";
        export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;

        mvn -Dhttps.protocols=TLSv1.2 install -V -B -DskipTests -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -l.npm=true -Dskip.gulp=true -Dskip.bower=true; 

        mvn -Dhttps.protocols=TLSv1.2 test -DskipTests -V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Denforcer.skip=true;

        mvn dependency:build-classpath -Dmdep.outputFile="classpath.info";
            """
        output = Cmd_util.run_cmd(cmd)

        if "\n[INFO] BUILD FAILURE\n" in output:
            fail_to_compile_path = os.path.join(local_working_directory, "..", 'fail_to_compile.tag')
            Config.fail_to_compile = True
            logger.error("the bug fails to compile!")
            File_util.write_str_to_file(fail_to_compile_path, output, False)

        File_util.write_line_to_file(Config.log_file, output)

    def run_test(self, bug):
        local_working_directory = bug.get_working_dir()
        pom_path = bug.info['reproductionBuggyBuild']['projectRootPomPath']
        buggy_build_id = bug.info['builds']['buggyBuild']['id']
        pom_path = pom_path.partition(str(buggy_build_id))[2]
        pom_path = pom_path.replace("/pom.xml", "")
        pom_path = pom_path.replace("/", "", 1)
        if pom_path:
            local_working_directory = os.path.join(local_working_directory, pom_path)
        cmd = f"""cd {local_working_directory};
            export JAVA_HOME={os.path.join(Config.JAVA8_HOME, '..') };
            export PATH="{Config.MAVEN_BIN}:$PATH";
            export _JAVA_OPTIONS=-Djdk.net.URLClassPath.disableClassPathURLCheck=true;
            
            rm -rf .git; git init; git commit -m 'init' --allow-empty;

            mvn test -V -B -Denforcer.skip=true -Dcheckstyle.skip=true -Dcobertura.skip=true -DskipITs=true -Drat.skip=true -Dlicense.skip=true -Dfindbugs.skip=true -Dgpg.skip=true -Dskip.npm=true -Dskip.gulp=true -Dskip.bower=true -Djacoco.skip=true -Denforcer.skip=true;
            """
        return Cmd_util.run_cmd(cmd)

    def failing_tests(self, bug):
        tests = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace("https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'], b['builds']['fixerBuild']['id'])

                if bug.project.lower() == project_id.lower() and bug.bug_id.lower() == bug_id.lower():
                    for t in b['tests']['failingClasses']:
                        tests += [t['testClass']]
                    return tests
        return tests

    def failing_test_methods(self, bug):
        tests = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace("https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'], b['builds']['fixerBuild']['id'])

                if bug.project.lower() == project_id.lower() and bug.bug_id.lower() == bug_id.lower():
                    for t in b['tests']['failureDetails']:
                        tests += [t['testClass'] + "#" + t['testMethod']]
                    return tests
        return tests

    def failing_test_methods_2(self, bug):
        """
        for dynmoath patch explorer
        """
        tests = []
        with open(os.path.join(self._get_info_path(), "bugs.json")) as fd:
            data = json.load(fd)
            for b in data:
                (organization, project) = b["repository"]["url"].replace("https://github.com/", "").split("/")
                project_id = "%s-%s" % (organization, project)
                bug_id = "%s-%s" % (b['builds']['buggyBuild']['id'], b['builds']['fixerBuild']['id'])

                if bug.project.lower() == project_id.lower() and bug.bug_id.lower() == bug_id.lower():
                    for t in b['tests']['failureDetails']:
                        tests += [f"{t['testMethod']}({t['testClass']})"]
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
            # when this assert fails, you might open your workspace at via a symbol link.
            # this has been fixed by changing config PROJECT_PATH and PARENT_PROJECT_PATH
            assert bug.get_working_dir() in module[
                'baseDir'], f"bug.get_working_dir(): {bug.get_working_dir()} is not in in module['baseDir']: {module['baseDir']}"
            module_name = module['baseDir'].replace(bug.get_working_dir() + '/', '')
            if failing_module == module_name or failing_module == module['name']:
                return self.abs_to_rel(bug.get_working_dir(), module['sources'])
        return folders

    def test_folders(self, bug):
        folders = []

        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module['name']:
                return self.abs_to_rel(bug.get_working_dir(), module['tests'])

        return folders

    def bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module['name']:
                return self.abs_to_rel(bug.get_working_dir(), module['binSources'])
        return []

    def test_bin_folders(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module == module_name or failing_module == module['name']:
                return self.abs_to_rel(bug.get_working_dir(), module['binTests'])
        return []

    def classpath(self, bug):
        info = self._get_project_info(bug)
        failing_module = self.failing_module(bug)

        deps = []

        for module in info['modules']:
            module_name = os.path.basename(module['baseDir'])
            if failing_module != module_name and failing_module != module['name']:
                deps += module['binSources']
        deps += info['classpath']

        # return ":".join(deps)

        # add junit jar
        classpath = ":".join(deps)
        if "/junit-4" not in classpath and "/junit-3" not in classpath:
            deps += [os.path.join(Config.M2_REPO, "junit", "junit", "4.12", "junit-4.12.jar")]
            deps += [os.path.join(Config.M2_REPO, "org", "hamcrest", "hamcrest-core", "1.3", "hamcrest-core-1.3.jar")]

        classpath = ":".join(deps)

        # add bin folders of src and tests of the buggy program
        bin_folders = self.bin_folders(bug)
        test_folders = self.test_bin_folders(bug)
        if len(bin_folders) > 0 and len(test_folders) > 0:
            bin_folder_path = os.path.join(bug.get_working_dir(), bin_folders[0])
            test_bin_folder_path = os.path.join(bug.get_working_dir(), test_folders[0])
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
        source_folders = self.source_folders(bug)
        assert len(source_folders) == 1

        buggy_dir = os.path.join(bug.get_working_dir(), source_folders[0])

        from copy import deepcopy
        bugCopy = deepcopy(bug)
        fixed_dir = Config.TMP_FIXED_DIR
        fixed_dir = self.checkout_fixed(bugCopy, fixed_dir)
        fixed_dir = os.path.join(fixed_dir, source_folders[0])
        patch_diff = Cmd_util.run_cmd(f"diff -Naur {buggy_dir} {fixed_dir}")

        # must delete to save / space!
        logger.info(f"rm tmp_checkout_dir: {fixed_dir}")
        File_util.rm_dir_safe_contain(fixed_dir, '/tmp/')

        return patch_diff
```

## 2. Adding Support for a New Fault Localizer

1. Add the fault localizer directory into the `fl_modules` folder.

2. Modify the `APRConfig/localization/Localizer_factory.py` as highlighted in the following comments:
```python
# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/14 21:59:03
@Author     : apr
'''


import logging
import Gzoltar
import Other_localizer # 1. add import

logger = logging.getLogger()


class LocalizerFactory():
    def create_localizer(self, localizer_name, fl_args):
        if localizer_name.lower() == "gzoltar_v0.1.1" or localizer_name.lower() == "gzoltar":
            return Gzoltar.Gzoltar(fl_args)
        elif dataset_name.lower() == "other_localizer": # 2. add an else if stmt
            return Other_localizer.Other_localizer(fl_args)
        else:
            raise Exception(f"unknown localizer name: {localizer_name}")
```

3. Add a new file (e.g., `GZoltar.py` for the GZoltar fault localizer) into the `APRConfig/localization/` folder. The content is:
```python
import os

import Localizer
import Config
from utils import Cmd_util


class Gzoltar(Localizer.Localizer):
    def __init__(self, fl_args):
        super().__init__(fl_args)

        """
        gzoltar 0.1.1 version
        """
        self.jarPath = Config.GZOLTAR_JAR_PATH
        self.jarJavaVersion = Config.JAVA8_HOME
        self.mainClass = "apr.module.fl.main.Main"
    
    def localize(self):
        cmd = f"""
            cd {self.workingDir};
            export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
            TZ="America/New_York"; export TZ;
            export PATH="{self.jarJavaVersion}:$PATH";
            export JAVA_HOME="{self.jarJavaVersion}";
            timeout 20m java {Config.JAVA_ARGS} -cp {self.jarPath} {self.mainClass} \\
                --externalProjPath {self.externalProjPath} \\
                --srcJavaDir {self.srcJavaDir} \\
                --binJavaDir {self.binJavaDir} \\
                --binTestDir {self.binTestDir} \\
                --jvmPath {self.jvmPath} \\
                --failedTests {self.failedTests} \\
                --dependencies {self.dependencies} \\
                --outputDir {self.outputDir} \\
                --workingDir {self.workingDir};
        """
        self.run_fl_cmd(cmd)
        pass
```

## 3. Adding Support for a New Patch Generation Algorithm


1. Add the patch generation algorithm directory into the `apr_tools` folder.

2. Modify the `APRConfig/apr/Apr_factory.py` as highlighted in the following comments:

```python
# -*- encoding: utf-8 -*-
'''
@Description: 
@Date       : 2021/08/14 21:59:03
@Author     : apr
'''

import logging

import Simfix
import Nopol
import Tbar  # 1. add import

logger = logging.getLogger()


class AprFactory():
    def __init__(self) -> None:
        self.name = "apr"
        pass

    def create_apr(self, apr_name, apr_args):
        if apr_name.lower().startswith("simfix_"): 
            return Simfix.Simfix(apr_args, apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("nopol_"):
            return Nopol.Nopol(apr_args, "nopol", apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("dynamoth_"):
            return Nopol.Nopol(apr_args, "dynamoth", apr_name.lower().split("_")[-1])
        elif apr_name.lower().startswith("tbar_"):  # 2. add an else if stmt
            return Tbar.Tbar(apr_args, apr_name.lower().split("_")[-1])
        else:
            raise Exception(f"unknown {self.name} name: {apr_name}")
```

3. Add a new file (e.g., `TBar.py` for the TBar patch generation algorithm) into the `APRConfig/apr/` folder. The content is:
```python
import os

import Apr
import Config


class Tbar(Apr.Apr):
    def __init__(self, args, validate_mode):
        super().__init__(args)
        self.onlyRunDefault = "false"
        if validate_mode == "1":
            self.onlyRunDefault = "true"   
        """
        tbar
        release date: July 2019 (from acm)
        commit id: 35f33ec9cd5ad085deaf68c9ff4cd2653f6f7280
        """
        self.jarPath = os.path.join(
            Config.PARENT_PROJECT_PATH, "apr_tools",
            "TBar/versions/TBar-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
        self.jarJavaVersion = Config.JAVA7_HOME
        self.mainClass = "edu.lu.uni.serval.tbar.main.Main"

    def repair(self):
        # timeout 360m java {Config.JAVA_ARGS} -cp {self.jarPath} {self.mainClass}  \\
        cmd = f"""
        cd {self.workingDir};
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="{self.jarJavaVersion}:$PATH";
        export JAVA_HOME="{self.jarJavaVersion}";

        timeout 360m java {Config.JAVA_ARGS} -cp {self.jarPath} {self.mainClass}  \\
            --flDir {self.fl_dir} \\
            --flTimeCost {self.fl_time_cost} \\
            --outputDir {self.outputDir} \\
            --jvmPath {self.jvmPath} \\
            --externalProjPath {self.externalProjPath} \\
            --binJavaDir {self.binJavaDir} \\
            --binTestDir {self.binTestDir} \\
            --srcJavaDir {self.srcJavaDir} \\
            --failedTests {self.failedTests} \\
            --dependencies {self.dependencies}  \\
            --onlyRunDefault {self.onlyRunDefault}
        """
        self.run_repair_cmd(cmd)
        pass
```


## 4. Adding Support for a New Patch Validator


1. Add the patch validator directory into the `patch_validator` folder.

2. Modify the `APRConfig/Config.py` as highlighted in the following comment:
```python
import os

rerun_dataset = True

# MAX_INT
MAX_INT = 1000000000000

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
PARENT_PROJECT_PATH = os.path.join(os.path.realpath(os.path.dirname(__file__)), "..")

M2_REPO = os.path.expanduser("~/.m2/repository")
MAVEN_BIN = os.environ.get("MAVEN_BIN", "/usr/bin/mvn")

DATASET_PATH = os.path.abspath(os.path.join(PROJECT_PATH, "..", "datasets"))
DATASET_INFO_PATH = os.path.abspath(os.path.join(PROJECT_PATH, "..", "datasets", "dataset_info"))
assert os.path.exists(DATASET_PATH)
assert os.path.exists(DATASET_INFO_PATH)

JAVA7_HOME = os.path.expanduser("~/env/jdk1.7.0_80/bin/")
JAVA8_HOME = os.path.expanduser("~/env/jdk1.8.0_202/bin/")
JAVA11_HOME = os.path.expanduser("~/env/jdk-11/bin/")
JAVA_ARGS = "-Xmx4g -Xms1g"
assert os.path.exists(JAVA7_HOME)
assert os.path.exists(JAVA8_HOME)

TIMEOUT = 120 

TMP_BUGGY_DIR = "/tmp/buggy"
TMP_FIXED_DIR = "/tmp/fixed"

TMP_OUTPUT_DIR = os.path.join(PARENT_PROJECT_PATH, "results")
LOG_NAME = "execution_framework.log"

GZOLTAR_JAR_PATH = os.path.join(
    PARENT_PROJECT_PATH,
    "fl_modules/fault_localizer/versions/gzoltar_localizer-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
# specifiy the runnable jar file path of the patch validator
EXTERNAL_VALIDATOR = os.path.join(
    PARENT_PROJECT_PATH, "patch_validator/patch_validator/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
```


## 5. Acknowledgement

We would like to sincerely thank Thomas Durieux, Fernanda Madeiral, Matias Martinez, and Rui Abreu for contributing a great framework (i.e., RepairThemAll), which serves as a quite useful reference point for how to construct an executable framework. We also adopted some software design patterns used in RepairThemAll, and finally accomplished a new executable framework that properly decouples the APR implementation into three sub-modules, including fault localization, patch generation and patch validation, to support the bias mitigation and validation as well as further explorations on APR evaluation for potential end users. 
