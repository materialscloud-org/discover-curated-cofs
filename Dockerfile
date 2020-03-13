FROM python:3.7

# Container vars
ENV AIIDA_PATH /app
ENV PYTHONPATH /app

# AiiDA profile vars
ENV AIIDA_PROFILE curated-cofs
ENV AIIDADB_ENGINE postgresql_psycopg2
ENV AIIDADB_PASS 7rvbeWPTH90trfKnCAsY7F18PupI31ZEJzSJ0wT6is6XalcN1A
ENV AIIDADB_NAME test_qb_leopold_7887e09294d3db7f91be99cc227fddf6
ENV AIIDADB_HOST host.docker.internal
ENV AIIDADB_BACKEND django
ENV AIIDADB_PORT 5432
ENV AIIDADB_REPOSITORY_URI file:///app/.aiida/repository/curated-cofs
ENV AIIDADB_USER aiida_qs_leopold_7887e09294d3db7f91be99cc227fddf6
ENV default_user_email leopold.talirz@gmail.com

# Materials Cloud vars
ENV EXPLORE_URL https://dev-www.materialscloud.org/explore/curated-cofs
ENV BOKEH_PREFIX "/curated-cofs"

# Install recent nodejs for bokeh & jsmol-bokeh-extension
# See https://github.com/nodesource/distributions/blob/master/README.md#installation-instructions
RUN curl -sL https://deb.nodesource.com/setup_13.x | bash -
RUN apt-get update && apt-get install -y --no-install-recommends \
  nodejs \
  graphviz \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean all

WORKDIR /app

# Install jsmol
RUN wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
RUN unzip jmol.zip && cd jmol-14.29.22 && unzip jsmol.zip

# Install discover section
WORKDIR /app/discover-cofs

COPY figure ./figure
COPY detail ./detail
COPY data ./data
COPY select-figure ./select-figure
RUN ln -s /app/jmol-14.29.22/jsmol ./detail/static/jsmol
COPY setup.py ./
RUN pip install -e .
RUN reentry scan -r aiida
COPY .docker/serve-app.sh /opt/
COPY .docker/config.json $AIIDA_PATH/.aiida/

# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]
