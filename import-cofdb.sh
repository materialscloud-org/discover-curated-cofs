#!/bin/bash -e
set -x

#===============================================================================
# start postgres
. /opt/postgres.sh

#===============================================================================
# Download COF database
base_url=http://archive.materialscloud.org/file/2018.0003/v1;  \
wget ${base_url}/cof-database.aiida
verdi import cof-database.aiida > import.log

# no need to keep the duplicate
rm cof-database.aiida

#EOF
