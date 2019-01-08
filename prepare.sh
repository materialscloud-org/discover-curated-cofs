#!/bin/bash

# Download jsmol
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
unzip jmol.zip 
cd jmol-14.29.22
unzip jsmol.zip
mv jsmol ../detail/static
cd ..
rm -r jmol-14.29.22

# Download data
cd data/
export base_url=http://archive.materialscloud.org/file/2018.0003/v2; \
    wget ${base_url}/structures.tgz &&\
    wget ${base_url}/properties.tgz


# Extract data
tar xf structures.tgz && rm structures.tgz && \
    tar xf properties.tgz && rm properties.tgz

cd ..

# Create sqlite DB
python import_db.py

