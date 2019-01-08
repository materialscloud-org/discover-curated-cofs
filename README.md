# Materials Cloud Discover Section for Covalent Organic Frameworks

Using

 * bokeh server
 * sqlite database backend
   (AiiDA database backend in alpha)
 * jsmol for structure visualization

## Prerequisites

 * python
 * nodejs >= 6

## Installation

```
pip install -e .     # install python dependencies
./prepare.sh         # download the data (run only once)
bokeh serve --show figure detail   # run app
```

## Configuration

Feel free to adapt this app to your own needs:

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

## Docker

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
```
