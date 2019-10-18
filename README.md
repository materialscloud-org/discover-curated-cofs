[![Build Status](https://travis-ci.org/materialscloud-org/structure-property-visualizer.svg?branch=master)](https://travis-ci.org/materialscloud-org/structure-property-visualizer)

# Structure-Property-Visualizer

Use this app to generate interactive visualizations like [these](https://www.materialscloud.org/discover/cofs#mcloudHeader)
for atomic structures and their properties.

## Inner working

The query for results is done in most of the cases by searching a Node having the as label a certain CURATED-COF ID,
and search for the WorkFunctionNode with `attributes.function_name=="link_outputs"` that links together all the output.
(In the future we could directly label the WorkFunctionNode with the ID of the COF)

This WorkFunctionNode also has the extra `curated_cofs_version` that is `0` for structures that were not considered
(i.e., charged, "C" COFs containing counter ions), `1` for the version published, and `2` for the update of October 2019.
We will use the index `2` until we need to change the API again.
The nodes connected are

```
Inputs            Type
----------------  -------
orig_cif          CifData (StructureData in v1)
orig_zeopp_out    Dict
orig_cif_qeq      CifData (only in v1)
orig_qeq_henry    Dict (only in v1)
dftopt_out        Dict (SinglefileData in v1)
opt_cif_ddec      CifData
opt_zepp_out      Dict
isot_co2_geo_out  Dict (only in v2)
isot_co2_out      Dict
isot_n2_geo_out   Dict (only in v2)
isot_n2_out       Dict
pe_out            Dict
```

## Re-implementation based on Panel

Use as jupyter notebook:
```
jupyter notebook
# open figure/main.ipynb
```

Use with panel:
```
panel serve detail/ figure/
```

## Features

 * interactive scatter plots via [bokeh server](https://bokeh.pydata.org/en/1.0.4/)
 * interactive structure visualization via [jsmol](https://chemapps.stolaf.edu/jmol/docs/)
 * simple input: provide CIF/XYZ files with structures and CSV file with their properties
 * simple deployment on [materialscloud.org](https://www.materialscloud.org/discover/menu) through [Docker containers](http://docker.com)
 * driven by database backend:
   1. [sqlite](https://www.sqlite.org/index.html) database (default)
   1. [AiiDA](http://www.aiida.net/) database backend (less tested)

## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Installation

```
git clone https://github.com/materialscloud-org/structure-property-visualizer.git
cd structure-property-visualizer
pip install -e .     # install python dependencies
./prepare.sh         # download test data (run only once)
```

### Running the app

```
bokeh serve --show figure detail select-figure   # run app
```

## Customizing the app

### Input data
 * a set of structures in `data/structures`
   * Allowed file extensions: `cif`, `xyz`
 * a CSV file `data/properties.csv` with their properties
   * has a column `name` whose value `<name>` links each row to a file in `structures/<name>.<extension>`.
 * adapt `import_db.py` accordingly and run it to create the database

### Plots

The plots can be configured using a few YAML files in `figure/static`:
 * `columns.yml`: defines metadata for columns of CSV file
 * `filters.yml`: defines filters available in plot
 * `presets.yml`: defines presets for axis + filter settings

## Docker deployment

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
# open http://localhost:3245/cofs/select-figure
```
