import os

# MAX_INT
MAX_INT = 1000000000000

# the path of APRConfig
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
PARENT_PROJECT_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                   "..")

M2_REPO = os.path.expanduser("~/.m2/repository")

DATASET_PATH = os.path.abspath(os.path.join(PROJECT_PATH, "..", "datasets"))
DATASET_INFO_PATH = os.path.abspath(
    os.path.join(PROJECT_PATH, "..", "datasets", "dataset_info"))
assert os.path.exists(DATASET_PATH)
assert os.path.exists(DATASET_INFO_PATH)

# jdk
JAVA7_HOME = os.path.expanduser("~/env/jdk1.7.0_80/bin/")
JAVA8_HOME = os.path.expanduser("~/env/jdk1.8.0_202/bin/")
JAVA_ARGS = "-Xmx4g -Xms1g"
# JAVA_ARGS = "-Xmx8g -Xms2g" # just for nopol/dynamoth exceptional cases. (out of heap size or memory)
assert os.path.exists(JAVA7_HOME)
assert os.path.exists(JAVA8_HOME)

# TIMEOUT = 7200 # in seconds
TIMEOUT = 120  #120*3 validation strategies  # in minutes

# tmp dir for patch diff
TMP_BUGGY_DIR = "/tmp/buggy"
TMP_FIXED_DIR = "/tmp/fixed"

# output
TMP_OUTPUT_DIR = os.path.join(PARENT_PROJECT_PATH, "results")
LOG_NAME = "execution_framework.log"

# FL
GZOLTAR_JAR_PATH = os.path.join(
    PARENT_PROJECT_PATH,
    "fl_modules/gzoltar_localizer/versions/fault_localizer-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
)
# PV
EXTERNAL_VALIDATOR = os.path.join(
    PARENT_PROJECT_PATH,
    "patch_validator/patch_validator/versions/PatchTest-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
)