#!/bin/bash

# Download jsmol, and link it to be used for 'detail' and 'details' pages
echo "### Donwloading jsmol"
rm -rf jmol-14.29.22 # remove if previously existing
wget https://sourceforge.net/projects/jmol/files/Jmol/Version%2014.29/Jmol%2014.29.22/Jmol-14.29.22-binary.zip/download --output-document jmol.zip
unzip jmol.zip 
rm jmol.zip
cd jmol-14.29.22
unzip jsmol.zip 
rm jsmol.zip
cd ..
rm -f ./detail/static/jsmol ./details/static/jsmol # remove if previously existing
ln -s $(readlink -f jmol-14.29.22/jsmol) ./detail/static/jsmol  
ln -s $(readlink -f jmol-14.29.22/jsmol) ./details/static/jsmol