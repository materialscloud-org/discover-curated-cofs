#!/bin/bash -e
set -x

#===============================================================================
# start postgres
source /opt/postgres.sh
psql_start

#===============================================================================
# import COF database
verdi import data/parameters.aiida &> import_new.log

# no need to keep the duplicate
psql_stop
rm parameters.aiida
#rm cof-database.aiida

#EOF
