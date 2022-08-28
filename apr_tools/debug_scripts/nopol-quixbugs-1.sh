debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""

cd /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_;
        export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="/home/apr/env/jdk1.8.0_202/bin/:$PATH";
        export JAVA_HOME="/home/apr/env/jdk1.8.0_202/bin/";
        
        time java $debug -Xmx4g -Xms1g -cp /mnt/data/bias_validation_2021/execution_framework/../apr_tools/nopol/versions/nopol-0.2-SNAPSHOT-jar-with-dependencies.jar:/home/apr/env/jdk1.8.0_202/bin//../lib/tools.jar fr.inria.lille.repair.Main \
            --fl_dir /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/dataset/../gzoltar \
            --fl_time_cost 1.3430 \
            --validate_mode 2 \
            --output_dir /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/dataset/../gzoltar/../nopol_debug \
            --jvm_path /home/apr/env/jdk1.8.0_202/bin/ \
            --externalProjPath /mnt/data/bias_validation_2021/execution_framework/../patch_validator/PatchExecution/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
            --binJavaDir /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/target/classes \
            --binTestDir /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/target/test-classes \
            --mode repair \
            --type pre_then_cond \
            --oracle angelic \
            --synthesis smt \
            --flocal gzoltar \
            --json \
            --solver z3 \
            --solver-path /mnt/data/bias_validation_2021/execution_framework/../libs/z3/build/z3 \
            --complianceLevel 8 \
            --source /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/src/main/java \
            --classpath /mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/target/test-classes:/mnt/data/bias_validation_2021/execution_framework/../results_quixbugs/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/quixbugs_FIND_IN_SORTED_/target/classes:/home/apr/.m2/repository/junit/junit/4.11/junit-4.11.jar:/home/apr/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar \
            --maxTime 120
