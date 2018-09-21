# using https://github.com/materialscloud-org/mc-docker-stack/tree/discover
#
FROM mc-docker-stack:discover
USER root
WORKDIR /project


# Install jsmol
RUN wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
RUN unzip jmol.zip && cd jmol-14.29.22 && unzip jsmol.zip

# Install jsmol bokeh extension
RUN git clone https://github.com/ltalirz/jsmol-bokeh-extension.git
RUN apt-get update && apt-get install -y --no-install-recommends nodejs
# adds to global PYTHONPATH
RUN echo "/project/jsmol-bokeh-extension" >> /usr/local/lib/python2.7/dist-packages/site-packages.pth

# Copy bokeh app
WORKDIR /project/discover-cofs
COPY figure ./figure
COPY detail ./detail
RUN ln -s /project/jmol-14.29.22/jsmol ./detail/static/jsmol
COPY setup.py import_db.py ./
RUN pip install -e .
COPY serve-app.sh /opt/

RUN chown -R scientist:scientist /project

USER scientist

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]

#EOF
