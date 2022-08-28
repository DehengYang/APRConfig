debug="-Xdebug -Xrunjdwp:transport=dt_socket,address=8000,server=y"

#debug=""


cd /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5;
            export JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8 -Duser.language=en-US -Duser.country=US -Duser.language=en";
            TZ="America/New_York"; export TZ;
            export PATH="/home/apr/env/jdk1.8.0_202/bin/:$PATH";
            export JAVA_HOME="/home/apr/env/jdk1.8.0_202/bin/";
            time java -Xmx4g -Xms1g -cp /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../fl_modules/gzoltar_localizer/versions/gzoltar_localizer-0.0.1-SNAPSHOT-jar-with-dependencies.jar apr.module.fl.main.Main \
                --externalProjPath /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../patch_validator/patch_validator/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar \
                --srcJavaDir /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/source/ \
                --binJavaDir /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build/ \
                --binTestDir /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build-tests/ \
                --jvmPath /home/apr/env/jdk1.7.0_80/bin/ \
                --failedTests org.jfree.data.xy.junit.XYSeriesTests \
                --dependencies /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build/:/home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/build-tests/:/home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/junit.jar:/home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/servlet.jar:/home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5/lib/itext-2.0.6.jar:/home/apr/data/2021_11_multi_chunk_repair/APRConfig/datasets/defects4j/framework/projects/lib/junit-4.11.jar \
                --outputDir /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/dataset/../gzoltar \
                --workingDir /home/apr/data/2021_11_multi_chunk_repair/APRConfig/APRConfig/../results_defects4j/defects4j_Chart_5/defects4j_Chart_5/defects4j_Chart_5;
