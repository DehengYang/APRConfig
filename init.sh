#install plugin and z3
git clone https://github.com/tdurieux/project-info-maven-plugin
cd project-info-maven-plugin 
mvn -Dhttps.protocols=TLSv1.2 install -DskipTests
cd ..
rm -rf project-info-maven-plugin 

cd libs
tar zxvf z3-z3-4.7.1.tar.gz
mv z3-z3-4.7.1 z3
python scripts/mk_make.py --java
cd build
make
sudo make install
cd ../..

# 2) Init Benchmarks
cd datasets
./init.sh
cd ..

# 3) Install fl_modules
cd fl_modules
./init.sh
cd ..

# 4) Install apr tools
cd apr_tools
./init.sh
cd ..

# 5) Install patch_validator
cd patch_validator
./init.sh
cd ..

