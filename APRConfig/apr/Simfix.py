import os

import Apr
import Config


class Simfix(Apr.Apr):
    def __init__(self, args, validate_mode):
        super().__init__(args)
        self.onlyRunDefault = "false"
        if validate_mode == "1":
            self.onlyRunDefault = "true" 
        """
        simfix
        release date: July 2018 (from acm)
        commit id: 76108b10f48b4f00e3743e551e8e4774232ec244
        """
        #TODO
        self.jarPath = os.path.join(
            Config.PARENT_PROJECT_PATH, "apr_tools",
            "SimFix/versions/simfix-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
        self.jarDeps = os.path.join(Config.PARENT_PROJECT_PATH, "apr_tools",
                                    "SimFix/lib/*")
        self.jarJavaVersion = Config.JAVA7_HOME
        self.mainClass = "cofix.main.Main"

    def repair(self):
        # timeout 360m java {Config.JAVA_ARGS} -cp {self.jarPath}:{self.jarDeps} {self.mainClass}  \\
        cmd = f"""
        cd {self.workingDir};
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="{self.jarJavaVersion}:$PATH";
        export JAVA_HOME="{self.jarJavaVersion}";

        timeout 360m java {Config.JAVA_ARGS} -cp {self.jarPath}:{self.jarDeps} {self.mainClass}  \\
            --flDir {self.fl_dir} \\
            --flTimeCost {self.fl_time_cost} \\
            --outputDir {self.outputDir} \\
            --jvmPath {self.jvmPath} \\
            --externalProjPath {self.externalProjPath} \\
            --binJavaDir {self.binJavaDir} \\
            --binTestDir {self.binTestDir} \\
            --srcJavaDir {self.srcJavaDir} \\
            --failedTests {self.failedTests} \\
            --dependencies {self.dependencies} \\
            --onlyRunDefault {self.onlyRunDefault}
        """
        self.run_repair_cmd(cmd)
        pass