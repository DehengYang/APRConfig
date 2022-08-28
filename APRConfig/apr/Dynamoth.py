import os

import Apr
import Config
from utils import Cmd_util


class Dynamoth(Apr.Apr):
    def __init__(self, args):
        super().__init__(args)
        """
        dynamoth
        release date: (same to repairthemall)
        commit id: 7ba58a78d
        """
        self.jarPath = ""
        self.jarJavaVersion = Config.JAVA8_HOME
        self.mainClass = "cofix.main.Main"

    def repair(self):
        """
        cd /mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1;
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
TZ="America/New_York"; export TZ;
export PATH="/home/apr/env/jdk1.8.0_202/bin/:$PATH";
export JAVA_HOME="/home/apr/env/jdk1.8.0_202/bin/";
time java -Xmx4g -Xms1g -cp /mnt/recursive-repairthemall/RepairThemAll-Nopol-github/script/../repair_tools/nopol.jar:/home/apr/env/jdk1.8.0_202/bin//../lib/tools.jar fr.inria.lille.repair.Main \
	--mode repair \
	--type pre_then_cond \
	--oracle angelic \
	--synthesis smt \
	--flocal gzoltar \
	--json \
	--solver z3 \
	--solver-path /mnt/recursive-repairthemall/RepairThemAll-Nopol-github/script/../libs/z3/build/z3 \
	--complianceLevel 4 \
	--source source/ \
	--classpath "build/:build-tests/:/mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1/build/:/mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1/build-tests/:/mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1/lib/junit.jar:/mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1/lib/iText-2.1.4.jar:/mnt/benchmarks/repairDir/Nopol_Defects4J_Chart_1/lib/servlet.jar:/mnt/recursive-repairthemall/RepairThemAll-Nopol-github/script/../benchmarks/defects4j/framework/projects/lib/junit-4.11.jar:/mnt/recursive-repairthemall/RepairThemAll-Nopol-github/script/../repair_tools/nopol.jar" \
    --maxTime 180 \
    --buggylocPath "/mnt/benchmarks/buggylocs/Defects4J/Defects4J_Chart_1/buggyloc.txt"
        """
        cmd = """
            cd {self.workingDir};
            export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
            TZ="America/New_York"; export TZ;
            export PATH="{self.jarJavaVersion}:$PATH";
            export JAVA_HOME="{self.jarJavaVersion}";

            time java {self.jarPath} -cp {Config.JAVA_ARGS} {self.mainClass}  \\
                --timeout {self.timeout} \\
                --srcJavaDir {self.srcJavaDir} \\
                --binJavaDir {self.binJavaDir} \\
                --binTestDir {self.binTestDir} \\
                --jvmPath {self.jvmPath} \\
                --failedTests {self.failedTests} \\
                --dependencies {self.dependencies} \\
                --workingDir {self.outputDir};
            """
        Cmd_util.run_cmd(cmd)
        pass