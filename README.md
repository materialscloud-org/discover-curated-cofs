[![Build Status](https://travis-ci.org/materialscloud-org/structure-property-visualizer.svg?branch=master)](https://travis-ci.org/materialscloud-org/structure-property-visualizer)

# Discover CURATED-COFs

App for generating the interactive page of https://www.materialscloud.org/discover/curated-cofs.
Built from the [Structure-Property-Visualizer]https://github.com/materialscloud-org/structure-property-visualizer).

## Inner working

For each COF we create a group, e.g., `discover_curated_cofs/05001N2` that contains all the nodes that are relevant for that structure.
These nodes have the extra `TAG_KEY`, which indicates the content of that node: e.g., `orig_cif`, `opt_cif_ddec`, `isot_n2`, ...
Currently `GROUP_DIR = "discover_curated_cofs/"` and `TAG_KEY = "tag4"`, but they may vary in the future.

```

## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Installation and run

```
git clone https://github.com/lsmo-epfl/discover-curated-cofs.git
cd discover-curated-cofs
pip install -e .     # install python dependencies
./prepare.sh         # download test data (run only once)

bokeh serve --show detail details figure results select-figure
```

## Docker deployment

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
# open http://localhost:3245/cofs/select-figure
```
