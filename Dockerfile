# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover
USER root


# Install jsmol extension
WORKDIR /project
RUN git clone https://github.com/ltalirz/jsmol-bokeh-extension.git
RUN apt-get update && apt-get install -y --no-install-recommends nodejs
# add to global PYTHONPATH
RUN echo "/project/jsmol-bokeh-extension" >> /usr/local/lib/python2.7/dist-packages/site-packages.pth

# Copy bokeh app
WORKDIR /project/discover-cofs
COPY figure ./figure
COPY detail ./detail
COPY setup.py import_db.py ./
RUN pip install -e .
COPY serve-app.sh /opt/

RUN chown -R scientist:scientist /project

USER scientist

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]

#EOF
