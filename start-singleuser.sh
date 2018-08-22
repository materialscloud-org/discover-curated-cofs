#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

#===============================================================================
# debuging
set -x

#===============================================================================
# start postgres
source /opt/postgres.sh
psql_start

#===============================================================================
# environment
export PYTHONPATH=/project
export SHELL=/bin/bash

#===============================================================================
# setup AiiDA
aiida_backend=sqlalchemy

if [ $aiida_backend = "django" ]; then
    verdi daemon stop || true
    echo "yes" | python /usr/local/lib/python2.7/dist-packages/aiida/backends/djsite/manage.py --aiida-profile=default migrate
    verdi daemon start
fi

#===============================================================================
bokeh serve .                   \
    --port 5006                 \
    --log-level debug           \
    --allow-websocket-origin "*" \
    --use-xheaders
# --allow-websocket-origin discover.materialscloud.org 
# --allow-websocket-origin localhost:5006

##start Jupyter notebook server
#cd /project
#/opt/matcloud-jupyterhub-singleuser                              \
#  --ip=0.0.0.0                                                   \
#  --port=8888                                                    \
#  --notebook-dir="/project"                                      \
#  --NotebookApp.iopub_data_rate_limit=1000000000                 \
#  --NotebookApp.default_url="/apps/apps/home/start.ipynb"

#===============================================================================

#EOF
