[![Build Status](https://travis-ci.org/materialscloud-org/structure-property-visualizer.svg?branch=master)](https://travis-ci.org/materialscloud-org/structure-property-visualizer)

# Structure-Property-Visualizer

Use this app to generate interactive visualizations like [these](https://www.materialscloud.org/discover/cofs#mcloudHeader)
for atomic structures and their properties.

## Features

 * interactive scatter plots via [bokeh server](https://bokeh.pydata.org/en/1.0.4/)
 * interactive structure visualization via [jsmol](https://chemapps.stolaf.edu/jmol/docs/)
 * simple deployment on [materialscloud.org](https://www.materialscloud.org/discover/menu) through [Docker containers](http://docker.com)
 * driven by database backend:
   1. [AiiDA](http://www.aiida.net/) database backend (less tested)

## Inner working

For each COF we create a group, e.g., `curated-cof_05001N2_v1` that contains all the nodes that are relevant for that structure.
These nodes have the extra `curated-cof_tag`, which indicates the content of that node: e.g., `orig_cif`, `opt_cif_ddec`, `isot_n2_out`, ...


## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Running the app

```
panel serve detail/ figure/
```

## Docker deployment

```
pip install -e .
docker-compose build
docker-compose up
# open http://localhost:5006/curated-cofs
```
