<<C1
git clone https://github.com/tdurieux/project-info-maven-plugin
cd project-info-maven-plugin 
mvn -Dhttps.protocols=TLSv1.2 install -DskipTests
C1


<<C2
cd libs/z3
python scripts/mk_make.py --java
cd build
make
make install
cd ../../
C2


echo "configure defects4j"
cd ~/env
./change-d4j-version.sh 7
cd -
echo "defects4j is configured now."
