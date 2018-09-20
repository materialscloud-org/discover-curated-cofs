# LSMO property visualizer app

Using

 * bokeh server
 * sqlite backend
   (AiiDA backend in alpha)

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
