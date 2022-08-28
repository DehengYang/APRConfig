debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""


cd /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_;
            export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
            TZ="America/New_York"; export TZ;
            export PATH="/home/apr/env/jdk1.8.0_202/bin/:$PATH";
            export JAVA_HOME="/home/apr/env/jdk1.8.0_202/bin/";
            time java $debug -Xmx4g -Xms1g -cp /mnt/data/bias_validation_2021/execution_framework/../fl_modules/gzoltar_localizer/target/gzoltar_localizer-0.0.1-SNAPSHOT-jar-with-dependencies.jar apr.module.fl.main.Main \
                --externalProjPath /mnt/data/bias_validation_2021/execution_framework/../patch_validator/PatchExecution/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
                --srcJavaDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/src/main/java \
                --binJavaDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/target/classes \
                --binTestDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/target/test-classes \
                --jvmPath /home/apr/env/jdk1.8.0_202/bin/ \
                --failedTests java_testcases.junit.MINIMUM_SPANNING_TREE_Test \
                --dependencies /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/target/test-classes:/mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/target/classes:/home/apr/.m2/repository/junit/junit/4.11/junit-4.11.jar:/home/apr/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar \
                --outputDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/dataset/../gzoltar \
                --workingDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_/quixbugs_MINIMUM_SPANNING_TREE_;
