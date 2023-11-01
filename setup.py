#!/usr/bin/env python

from __future__ import absolute_import
from setuptools import setup

if __name__ == '__main__':
    setup(packages=["detail", "figure", "select-figure", "pipeline_config"],
          name="discover-curated-cofs",
          author="Leopold Talirz",
          author_email="leopold.talirz@epfl.ch",
          description="A Materials Cloud DISCOVER section for CURATED COFs.",
          license="MIT",
          classifiers=["Programming Language :: Python"],
          version="1.0.0",
          install_requires=[
              "aiida-core~=2.3",
              "bokeh~=1.4.0",
              "jsmol-bokeh-extension~=0.2.1",
              "requests~=2.21.0",
              "panel~=0.8.1",
              "param~=1.9.3",
              "pandas~=1.0.5",
              "pyjanitor~=0.20.2",
              "jinja2~=3.0.0",
              "frozendict~=2.3.2",
              "numpy~=1.23.1",
          ],
          extras_require={"pre-commit": ["pre-commit==1.17.0", "prospector==1.2.0", "pylint==2.4.0"]})
