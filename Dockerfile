# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover
USER scientist

# Download COF DB
WORKDIR /project
RUN export base_url=http://archive.materialscloud.org/file/2018.0003/v2; \
    wget ${base_url}/structures.tgz &&\
    wget ${base_url}/properties.tgz
RUN tar xf structures.tgz && rm structures.tgz && \
    tar xf properties.tgz && rm propertiez.tgz

# Copy bokeh app
WORKDIR /project/lsmo-bokeh-app
COPY app detail import-db.py requirements.txt ./
COPY serve-app.sh /opt/

# install app, set up DB
RUN pip install -r requirements.txt
RUN python import-db.py

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]

#EOF
