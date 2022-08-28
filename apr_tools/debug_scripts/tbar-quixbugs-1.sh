debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""

cd /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_;
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="/home/apr/env/jdk1.7.0_80/bin/:$PATH";
        export JAVA_HOME="/home/apr/env/jdk1.7.0_80/bin/";

        timeout 240m java $debug -Xmx4g -Xms1g -cp /mnt/data/bias_validation_2021/execution_framework/../apr_tools/TBar/versions/TBar-0.0.1-SNAPSHOT-jar-with-dependencies.jar edu.lu.uni.serval.tbar.main.Main  \
            --flDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/dataset/../gzoltar \
            --flTimeCost 1.3930 \
            --outputDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/dataset/../gzoltar/../tbar_0 \
            --jvmPath /home/apr/env/jdk1.8.0_202/bin/ \
            --externalProjPath /mnt/data/bias_validation_2021/execution_framework/../patch_validator/PatchExecution/target/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
            --binJavaDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/target/classes \
            --binTestDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/target/test-classes \
            --srcJavaDir /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/src/main/java \
            --failedTests java_testcases.junit.BREADTH_FIRST_SEARCH_Test \
            --dependencies /mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/target/test-classes:/mnt/data/bias_validation_2021/execution_framework/../results/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/quixbugs_BREADTH_FIRST_SEARCH_/target/classes:/home/apr/.m2/repository/junit/junit/4.11/junit-4.11.jar:/home/apr/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar  \
            --onlyRunDefault false
