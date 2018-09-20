#!/bin/bash

cd data/

# Download data
export base_url=http://archive.materialscloud.org/file/2018.0003/v2; \
    wget ${base_url}/structures.tgz &&\
    wget ${base_url}/properties.tgz

# Extract data
tar xf structures.tgz && rm structures.tgz && \
    tar xf properties.tgz && rm properties.tgz

cd ..

# Create sqlite DB
python import_db.py
