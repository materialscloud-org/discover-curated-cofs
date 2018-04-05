#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

#===============================================================================
# debuging
set -x

#===============================================================================
#TODO setup signal handler which shuts down posgresql and aiida.
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

# import COF datbaase
for i in /opt/cofdb/*.aiida; do
   verdi import $i
done

#===============================================================================
# environment
export PYTHONPATH=/project
export SHELL=/bin/bash


#EOF
