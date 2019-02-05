# Structure-Property-Visualizer

Use this app to generate interactive visualizations like [these](https://www.materialscloud.org/discover/cofs#mcloudHeader) 
for atomic structures and their properties.

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
 * [python](https://www.python.org/)
 * [nodejs](https://nodejs.org/en/) >= 6

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
   * has a column `name` whose value `<name>` links each row to a file in `structures/<name>.<extension>xyz`.

### Plots

The plots can be configured using a few YAML files:
 * `figure/columns.yml`: defines metadata for columns of CSV file
 * `figure/filters.yml`: defines filters available in plot
 * `figure/presets.yml`: defines presets for axis + filter settings

## Docker deployment

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
# open http://localhost:3245/select-figure
```
