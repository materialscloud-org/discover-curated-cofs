# LSMO property visualizer app

Using

 * bokeh server
 * sqlite backend
   (AiiDA backend in alpha)

## Installation

```
pip install -r requirements
./prepare.sh
bokeh serve --show .
```

## Docker

```
./prepare.sh
docker-compose build
docker-compose up
```
