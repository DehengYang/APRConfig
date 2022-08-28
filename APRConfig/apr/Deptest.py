import os

import Apr
import Config
from utils import File_util


class Deptest(Apr.Apr):
    def __init__(self, args, tool_name):
        super().__init__(args)
        self.tool_name = tool_name

        self.deptest_dir = os.path.join(Config.PARENT_PROJECT_PATH, "apr_tools", "Deptest/")
        self.gzoltar_dir = os.path.join(self.deptest_dir, 'deps/libs')
        self.d4j_dir = os.path.join(Config.DATASET_PATH, "defects4j")
        # this is no used now
        self.patch_exec_jar_path = os.path.join(self.deptest_dir, 'deps/libs', "PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar")

        self.patch_diff_path = os.path.join(self.outputDir, "..", "dataset", "patch.diff")


        self.jarPath = os.path.join(self.deptest_dir, "versions/purify-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
        self.jarJavaVersion = Config.JAVA8_HOME
        self.mainClass = "apr.purify.Main"
        self.dataset_name = args['dataset_name']

        # use self.failed_cases_str, rather than self.failedTests
        fault_localizer = args['fault_localizer']
        failed_test_cases_path = os.path.join(self.outputDir, "..", fault_localizer, "expected_failed_test_replicate.txt")
        failed_cases_list = File_util.read_file_add_wrap(failed_test_cases_path)
        self.failed_cases_str = ":".join(failed_cases_list)

        d4j_failed_cases = args['failedTestMethods']
        assert len(d4j_failed_cases.split(':')) == len(self.failed_cases_str.split(':')), "incorrect failed cases from gzoltar replication."

    def repair(self):
        # -testExecPath {self.patch_exec_jar_path} \\
        cmd = f"""
        cd {self.workingDir};
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="{self.jarJavaVersion}:$PATH";
        export JAVA_HOME="{self.jarJavaVersion}";
        time java {Config.JAVA_ARGS} -cp {self.jarPath} {self.mainClass} \\
            -dataset {self.dataset_name} \\
            -projDir {self.workingDir} \\
            -srcJavaDir {self.srcJavaDir} \\
            -binJavaDir {self.binJavaDir}\\
            -binTestDir {self.binTestDir} \\
            -jvmPath {self.jvmPath} \\
            -failedTestsStr {self.failed_cases_str} \\
            -gzoltarDir {self.gzoltar_dir} \\
            -d4jDir {self.d4j_dir} \\
            -logDir {self.outputDir} \\
            -patchDiffPath {self.patch_diff_path} \\
            -dependencies {self.dependencies}
        """
        self.run_repair_cmd(cmd)
        pass