[![Build Status](https://travis-ci.org/materialscloud-org/structure-property-visualizer.svg?branch=master)](https://travis-ci.org/materialscloud-org/structure-property-visualizer)

# Discover CURATED-COFs

App for generating the interactive page of https://www.materialscloud.org/discover/curated-cofs.
Built from the [Structure-Property-Visualizer]https://github.com/materialscloud-org/structure-property-visualizer).

## Inner working

For each COF we create a group, e.g., `discover_curated_cofs/05001N2` that contains all the nodes that are relevant for that structure.
These nodes have the extra `TAG_KEY`, which indicates the content of the node:
```
'orig_cif', 'orig_zeopp', 'dftopt', 'opt_cif_ddec', 'opt_zeopp', # CIF structures, DFT optimization, and pore analysis
'isot_co2', 'isot_n2', 'isotmt_h2', 'isot_ch4','isot_o2', 'kh_xe', 'kh_kr', 'kh_h2s', 'kh_h2o', # results of Isotherm work chain
'appl_pecoal', 'appl_peng', 'appl_h2storage', 'appl_ch4storage', 'appl_o2storage', 'appl_xekrsel', 'appl_h2sh2osel' # post-processing applications
```
Currently `GROUP_DIR = "discover_curated_cofs/"` and `TAG_KEY = "tag4"`, but they may vary in the future.
These groups are generated using the utility `make_export/create_groups_export.py` or they can be imported from
the latest databases stored on [Materials Cloud](https://archive.materialscloud.org/record/2020.107).

## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Installation and run

After activating your AiiDA environment:
```
git clone https://github.com/lsmo-epfl/discover-curated-cofs.git
cd discover-curated-cofs
pip install -e .     # install python dependencies
./prepare.sh         # download test data (run only once)
```

Download the latest database from [Materials Cloud](https://archive.materialscloud.org/record/2020.107)
and import it in AiiDA:
```
verdi import export_discovery_cof_xxx.aiida
```

Finally, visualize the app:
```
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
