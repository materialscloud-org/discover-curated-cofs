#!/bin/bash -e

# This script is executed whenever the docker container is (re)started.

#===============================================================================
# debugging
set -x

#===============================================================================
# write AiiDA config file
cat > $AIIDA_PATH/.aiida/config.json <<EOF
{
    "CONFIG_VERSION": {
        "CURRENT": 3,
        "OLDEST_COMPATIBLE": 3
    },
    "default_profile": "curated-cofs",
    "profiles": {
        "${AIIDA_PROFILE}": {
            "AIIDADB_ENGINE": "${AIIDADB_ENGINE}",
            "AIIDADB_PASS": "${AIIDADB_PASS}",
            "AIIDADB_NAME": "${AIIDADB_NAME}",
            "AIIDADB_HOST": "${AIIDADB_HOST}",
            "AIIDADB_BACKEND": "${AIIDADB_BACKEND}",
            "AIIDADB_PORT": "${AIIDADB_PORT}",
            "PROFILE_UUID": "ec243733c4454dad9ebb47b5b80ec90a",
            "default_user_email": "${default_user_email}",
            "AIIDADB_REPOSITORY_URI": "${AIIDADB_REPOSITORY_URI}",
            "AIIDADB_USER": "${AIIDADB_USER}",
            "options": {}
        }
    }
}
EOF

#===============================================================================
panel serve figure detail select-figure  \
    --port 5006                 \
    --log-level debug           \
    --allow-websocket-origin "*" \
    --prefix "$BOKEH_PREFIX" \
    --use-xheaders
# --allow-websocket-origin discover.materialscloud.org 
# --allow-websocket-origin localhost:5006

#===============================================================================

#EOF
