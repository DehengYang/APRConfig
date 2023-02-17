git clone https://github.com/DehengYang/fault_localizer.git
mv fault_localizer gzoltar_localizer

mvn install:install-file -Dfile=gzoltar-0.1.1.jar -DgroupId=com.gzoltar -DartifactId=gzoltar -Dversion=0.1.1 -Dpackaging=jar

cd gzoltar_localizer

mvn clean package -DskipTests

[ ! -d "versions" ] && echo "mkdir versions" && mkdir versions

cp target/gzoltar_localizer-0.0.1-SNAPSHOT-jar-with-dependencies.jar versions/
