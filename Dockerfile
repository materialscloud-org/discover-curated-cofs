# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover
USER scientist

# Download COF DB
WORKDIR /project
RUN base_url=http://archive.materialscloud.org/file/2018.0003/v1;  \
    wget ${base_url}/cof-database.aiida;

# Import COF DB
COPY import-cofdb.sh /opt/
RUN /opt/import-cofdb.sh

# Copy bokeh app
WORKDIR /project/lsmo-bokeh-app
COPY README.md description.html main.py ./

# start bokeh server
EXPOSE 5006
COPY start-singleuser.sh /opt/
CMD ["/opt/start-singleuser.sh"]

#EOF
