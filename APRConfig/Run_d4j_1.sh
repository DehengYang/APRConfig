export PYTHONPATH=./dataset:./tests:./apr:./localization:${PYTHONPATH}


source /home/apr/env/miniconda3/etc/profile.d/conda.sh
conda activate aprconfig

python ./Run_d4j_1.py
