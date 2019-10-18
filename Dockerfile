# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM aiidateam/aiida-docker-stack:v0.12.4
USER root
WORKDIR /home/aiida

# Install nodejs for jsmol-bokeh-extension
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs wget zip unzip graphviz \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean all \
    && updatedb

# Install jsmol
RUN wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
RUN unzip jmol.zip && cd jmol-14.29.22 && unzip jsmol.zip

# Copy bokeh app
WORKDIR /home/aiida/discover-cofs
COPY figure ./figure
COPY detail ./detail
COPY select-figure ./select-figure
RUN ln -s /home/aiida/jmol-14.29.22/jsmol ./detail/static/jsmol
COPY setup.py ./
RUN pip install -e .
COPY .docker/serve-app.sh /opt/
COPY .docker/config.json /home/aiida/.aiida/

USER aiida

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]

#EOF
