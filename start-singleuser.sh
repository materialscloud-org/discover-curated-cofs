#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

#===============================================================================
# debuging
set -x

#===============================================================================
#TODO setup signal handler which shuts down posgresql and aiida.
# setup postgresql
PGBIN=/usr/lib/postgresql/9.6/bin

# helper function to start psql and wait for it
function start_psql {
   ${PGBIN}/pg_ctl -D /project/.postgresql -l /project/.postgresql/logfile start
   TIMEOUT=20
   until psql -h localhost template1 -c ";" || [ $TIMEOUT -eq 0 ]; do
      echo ">>>>>>>>> Waiting for postgres server, $((TIMEOUT--)) remaining attempts..."
      tail -n 50 /project/.postgresql/logfile
      sleep 1
   done
}

# Start postgresql
echo "" > /project/.postgresql/logfile # empty log files
rm -vf /project/.postgresql/.s.PGSQL.5432
rm -vf /project/.postgresql/.s.PGSQL.5432.lock
rm -vf /project/.postgresql/postmaster.pid
#${PGBIN}/pg_ctl -D /project/.postgresql stop || true
start_psql

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
