conda env export --name mubench > env.yml
conda env export --name mubench --no-builds > env_no_builds.yml
# pip install pipreqs
pipreqs ../execution_framework/ --savepath ./pip_env.txt

