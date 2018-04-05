# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover

# Copy COF database
USER root
WORKDIR /opt/cofdb
RUN base_url=http://archive.materialscloud.org/file/2018.0003/v1;  \
    wget ${base_url}/cof-database.aiida;
#COPY cof-database.aiida .
COPY import-cofdb.sh .
RUN  chown -R root:root /opt/cofdb/;                                \
     chmod -R +r /opt/cofdb/;                                       \
     chmod -R +x /opt/cofdb/import-cofdb.sh                         
     
EXPOSE 8888

USER scientist

RUN /opt/cofdb/import-cofdb.sh

WORKDIR /project
COPY start-singleuser.sh /opt/
CMD ["/opt/start-singleuser.sh"]

#EOF
