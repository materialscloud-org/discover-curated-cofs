#!/bin/bash -e
set -x

#===============================================================================
# start postgres
. /opt/postgres.sh

#===============================================================================
# import COF database
verdi import cof-database.aiida > import.log

# no need to keep the duplicate
rm cof-database.aiida

#EOF
