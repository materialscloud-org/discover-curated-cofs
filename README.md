# LSMO property visualizer app

Using

 * bokeh server
 * sqlite backend
   (AiiDA backend in alpha)

## Configuration

The plots can be configured using yml files:

 * `figure/filters.yml`: defines available filters
 * `figure/presets.yml`: defines presets for axis + filter settings

## Installation

```
pip install -e .
./prepare.sh
bokeh serve --show figure detail
```

## Docker

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
```
