export PYTHONPATH=./dataset:./tests:./apr:./localization:${PYTHONPATH}

source /home/apr/env/miniconda3/etc/profile.d/conda.sh
conda activate mubench

# 1) to parse execution logs
python parser/Main_parse.py

# 2) to obtain patches
python parser/get_patch.py

# 3) to calculate time cost
python parser/Count_repair_time.py

# 4) to gather data (compression with high reduction size via lrzip)
python result_processor/Result_processor.py
