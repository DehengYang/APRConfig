debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""


cd /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5;
export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
        TZ="America/New_York"; export TZ;
        export PATH="/home/apr/env/jdk1.8.0_202/bin/:$PATH";
        export JAVA_HOME="/home/apr/env/jdk1.8.0_202/bin/";
        time java $debug -Xmx4g -Xms1g -cp /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../apr_tools/Deptest/versions/purify-0.0.1-SNAPSHOT-jar-with-dependencies.jar apr.purify.Main \
            -dataset defects4j \
            -projDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5 \
            -srcJavaDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/source/ \
            -binJavaDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build/\
            -binTestDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build-tests/ \
            -jvmPath /home/apr/env/jdk1.7.0_80/bin/ \
            -failedTestsStr org.jfree.data.xy.junit.XYSeriesTests#testBug1955483 \
            -gzoltarDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../apr_tools/Deptest/deps/libs \
            -d4jDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/datasets/defects4j \
            -logDir /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/dataset/../gzoltar/../deptest \
            -patchDiffPath /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/dataset/../gzoltar/../deptest/../dataset/patch.diff \
            -dependencies /mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build/:/mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build-tests/:/mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/junit.jar:/mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/servlet.jar:/mnt/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/itext-2.0.6.jar:/mnt/data/2021_11_multi_chunk_repair/APRConfig/datasets/defects4j/framework/projects/lib/junit-4.11.jar
