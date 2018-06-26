#!/bin/bash -e
set -x

#===============================================================================
# start postgres
source /opt/postgres.sh
psql_start

#===============================================================================
# import COF database
verdi import cof-database.aiida > import.log

# no need to keep the duplicate
psql_stop
rm cof-database.aiida

#EOF
