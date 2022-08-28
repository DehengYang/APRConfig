debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""

 cd /home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1;
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="/home/apr/env/jdk1.7.0_80/bin/:$PATH";
        export JAVA_HOME="/home/apr/env/jdk1.7.0_80/bin/";

        timeout 240m java $debug -Xmx4g -Xms1g -cp /home/apr/tools/bias_validation_2021/execution_framework/../apr_tools/TBar/target/classes:/home/apr/tools/bias_validation_2021/execution_framework/../apr_tools/TBar/target/dependency/* edu.lu.uni.serval.tbar.main.Main  \
            --flDir /home/apr/tools/bias_validation_2021/execution_framework/output/results/defects4j_Chart_1/dataset/../gzoltar \
            --flTimeCost 18.5979 \
            --outputDir /home/apr/tools/bias_validation_2021/execution_framework/output/results/defects4j_Chart_1/dataset/../gzoltar/../tbar \
            --jvmPath /home/apr/env/jdk1.7.0_80/bin/ \
            --externalProjPath /home/apr/tools/bias_validation_2021/execution_framework/../patch_validator/PatchExecution/target/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
            --binJavaDir /home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/build/ \
            --binTestDir /home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/build-tests/ \
            --srcJavaDir /home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/source/ \
            --failedTests org.jfree.chart.renderer.category.	.AbstractCategoryItemRendererTests \
            --dependencies /home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/build/:/home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/build-tests/:/home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/lib/iText-2.1.4.jar:/home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/lib/junit.jar:/home/apr/tools/bias_validation_2021/execution_framework/output/defects4j_Chart_1/lib/servlet.jar:/home/apr/tools/bias_validation_2021/datasets/defects4j/framework/projects/lib/junit-4.11.jar 
