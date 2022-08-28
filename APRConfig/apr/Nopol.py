import os

import Apr
import Config

class Nopol(Apr.Apr):
    def __init__(self, args, tool_name, validate_mode):
        super().__init__(args)
        self.tool_name = tool_name.lower()

        self.synthesis = "smt"
        if self.tool_name == "dynamoth":
            self.synthesis = "dynamoth"
        """
        nopol
        release date: (same to repairthemall)
        commit id: 7ba58a78d
        """
        self.validate_mode = validate_mode

        self.jarPath = os.path.join(
            Config.PARENT_PROJECT_PATH, "apr_tools",
            "nopol/versions/nopol-0.2-SNAPSHOT-jar-with-dependencies.jar")
        assert os.path.exists(self.jarPath)
        self.jarJavaVersion = Config.JAVA8_HOME
        self.mainClass = "fr.inria.lille.repair.Main"

    def repair(self):
        cmd = f"""
        cd {self.workingDir};
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="{self.jarJavaVersion}:$PATH";
        export JAVA_HOME="{self.jarJavaVersion}";
        
        time java {Config.JAVA_ARGS} -cp {self.jarPath}:{Config.JAVA8_HOME}/../lib/tools.jar {self.mainClass} \\
            --fl_dir {self.fl_dir} \\
            --fl_time_cost {self.fl_time_cost} \\
            --validate_mode {self.validate_mode} \\
            --output_dir {self.outputDir} \\
            --jvm_path {self.jvmPath} \\
            --externalProjPath {self.externalProjPath} \\
            --binJavaDir {self.binJavaDir} \\
            --binTestDir {self.binTestDir} \\
            --mode repair \\
            --type pre_then_cond \\
            --oracle angelic \\
            --synthesis {self.synthesis} \\
            --flocal gzoltar \\
            --json \\
            --solver z3 \\
            --solver-path {os.path.join(Config.PARENT_PROJECT_PATH, "libs/z3/build/z3")} \\
            --complianceLevel {self.compliance_level} \\
            --source {self.srcJavaDir} \\
            --classpath {self.dependencies} \\
            --maxTime {self.timeout}
        """
        self.run_repair_cmd(cmd)
        pass