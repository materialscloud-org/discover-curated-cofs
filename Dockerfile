# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover
USER scientist


# Install jsmol extension
WORKDIR /project
RUN git clone https://github.com/ltalirz/jsmol-bokeh-extension.git
RUN export PYTHONPATH=$PYTHONPATH:/project/jsmol-bokeh-extension

# Copy bokeh app
WORKDIR /project/lsmo-bokeh-app
COPY app detail requirements.txt ./
COPY serve-app.sh /opt/

# install app
RUN pip install --user -r requirements.txt

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]

#EOF
