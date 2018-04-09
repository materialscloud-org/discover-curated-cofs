#!/bin/bash -e
set -x

#===============================================================================
# start postgres
source /opt/postgres.sh

#===============================================================================
# import COF database
#verdi import cof-database.aiida > import.log

#psql -h localhost -U mcloud -d coflsmo -f aiida-db-backup.psql
psql -h localhost -d template1 -c "DROP DATABASE aiidadb;"
psql -h localhost -d template1 -c "DROP EXTENSION plpgsql;"
psql -h localhost -d template1 -c "CREATE DATABASE aiidadb OWNER aiida;"
psql -h localhost -d aiidadb -U aiida -f aiida-db-backup.psql

stop_psql

#-c "CREATE USER aiida WITH PASSWORD 'aiida_db_passwd';"
#   psql -h localhost -d template1 -c "CREATE DATABASE aiidadb OWNER aiida;"
#   psql -h localhost -d template1 -c "GRANT ALL PRIVILEGES ON DATABASE aiidadb to aiida;"

#EOF
