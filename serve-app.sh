#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

#===============================================================================
# debuging
set -x

#===============================================================================
# start postgres
source /opt/postgres.sh
psql_start

##===============================================================================
## setup AiiDA
#aiida_backend=sqlalchemy
#
#if [ $aiida_backend = "django" ]; then
#    verdi daemon stop || true
#    echo "yes" | python /usr/local/lib/python2.7/dist-packages/aiida/backends/djsite/manage.py --aiida-profile=default migrate
#    verdi daemon start
#fi

#===============================================================================
bokeh serve .                   \
    --port 5006                 \
    --log-level debug           \
    --allow-websocket-origin "*" \
    --use-xheaders
# --allow-websocket-origin discover.materialscloud.org 
# --allow-websocket-origin localhost:5006

#===============================================================================

#EOF
