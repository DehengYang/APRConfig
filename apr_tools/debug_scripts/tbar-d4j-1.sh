debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""

        cd /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15;
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="/home/apr/env/jdk1.7.0_80/bin/:$PATH";
        export JAVA_HOME="/home/apr/env/jdk1.7.0_80/bin/";

        timeout 240m java $debug -Xmx4g -Xms1g -cp /mnt/data/bias_validation_2021/execution_framework/../apr_tools/TBar/versions/TBar-0.0.1-SNAPSHOT-jar-with-dependencies.jar edu.lu.uni.serval.tbar.main.Main  \
            --flDir /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/dataset/../gzoltar \
            --flTimeCost 10.5170 \
            --outputDir /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/dataset/../gzoltar/../tbar_0 \
            --jvmPath /home/apr/env/jdk1.7.0_80/bin/ \
            --externalProjPath /mnt/data/bias_validation_2021/execution_framework/../patch_validator/PatchExecution/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
            --binJavaDir /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/build/ \
            --binTestDir /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/build-tests/ \
            --srcJavaDir /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/source/ \
            --failedTests org.jfree.chart.plot.junit.PiePlot3DTests \
            --dependencies /mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/build/:/mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/build-tests/:/mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/lib/junit.jar:/mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/lib/servlet.jar:/mnt/data/bias_validation_2021/execution_framework/../results_defects4j/defects4j_Chart_15/defects4j_Chart_15/defects4j_Chart_15/lib/itext-2.0.6.jar:/mnt/data/bias_validation_2021/datasets/defects4j/framework/projects/lib/junit-4.11.jar  \
            --onlyRunDefault false
