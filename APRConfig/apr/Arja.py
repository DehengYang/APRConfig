import os

import Apr
import Config
from utils import Cmd_util


class Arja(Apr.Apr):
    def __init__(self, args):
        super().__init__(args)
        """
        arja
        release date: (same to repairthemall)
        commit id: e60b990f9
        commit id: 8a8083c4abd19c215a2b4d17b1d63fddd628c621 (used by durieux)
        """
        self.tool_name = args["apr_name"]
        self.external = os.path.join(Config.PARENT_PROJECT_PATH, "apr_tools","arja/external")
        self.jarPath = os.path.join(
            Config.PARENT_PROJECT_PATH, "apr_tools",
            "arja/target/Arja-0.0.1-SNAPSHOT-jar-with-dependencies.jar")
        self.jarJavaVersion = Config.JAVA7_HOME
        self.mainClass = "us.msu.cse.repair.Main"

    def repair(self):
        """
        timeout 120m java -d64 -Xmx4g -Xms1g -XX:MaxPermSize=1024m -XX:+UseConcMarkSweepGC -XX:+CMSClassUnloadingEnabled -XX:+CMSClassUnloadingEnabled -cp {/home/tdurieux/defects4j4repair/script/../libs/}jmetal.jar:/home/tdurieux/defects4j4repair/script/../repair_tools/arja.jar us.msu.cse.repair.Main \
        """

        cmd = f"""
        cd {self.workingDir};
            export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
            TZ="America/New_York"; export TZ;
            export PATH="{self.jarJavaVersion}:$PATH";
            export JAVA_HOME="{self.jarJavaVersion}";

            timeout {self.timeout}m java -cp {os.path.join(Config.PARENT_PROJECT_PATH, "libs", "jmetal.jar")}:{self.jarPath} {self.mainClass} \
                {self.tool_name} \
                -DexternalProjRoot {self.external} \
                -DsrcJavaDir {self.srcJavaDir} \
                -DbinJavaDir {self.binJavaDir} \
                -DbinTestDir {self.binTestDir} \
                -DdiffFormat true \
                -Dseed 0 \
                -Ddependences {self.dependencies};
        """
        self.run_repair_cmd(cmd)
        pass