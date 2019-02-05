#!/bin/bash

# Download jsmol
echo "### Donwloading jsmol"
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
unzip jmol.zip 
cd jmol-14.29.22
unzip jsmol.zip
mv jsmol ../detail/static
cd ..
rm -r jmol-14.29.22

# Download data
echo "### Downloading test data"
cd data/
export base_url=https://object.cscs.ch/v1/AUTH_b1d80408b3d340db9f03d373bbde5c1e/discover-cofs/test_data; \
    wget ${base_url}/structures.tgz &&\
    wget ${base_url}/properties.csv

# Extract data
tar xf structures.tgz && rm structures.tgz

cd ..

# Create sqlite DB
echo "### Creating sqlite database"
python import_db.py

