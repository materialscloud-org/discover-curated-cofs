#!/usr/bin/env python

from __future__ import absolute_import
from setuptools import setup

if __name__ == '__main__':
    # Provide static information in setup.json
    # such that it can be discovered automatically
    setup(packages=["detail", "figure", "select-figure"],
          name="discover-curated-cofs",
          author="Leopold Talirz",
          author_email="leopold.talirz@epfl.ch",
          description="A Materials Cloud DISCOVER section for CURATED COFs.",
          license="MIT",
          classifiers=["Programming Language :: Python"],
          version="0.2.0",
          install_requires=[
              "aiida-core~=1.1.0",
              "bokeh~=1.4.0",
              "jsmol-bokeh-extension~=0.2.1",
              "pandas~=0.24.2",
              "requests~=2.21.0",
              "panel~=0.8.1",
              "param~=1.9.3",
              "jupyter",
              "graphviz~=0.13",
              "pre-commit",
              "yapf==0.28.0",
              "pylint>=2.4.0"
          ],
          extras_require={
            "pre-commit": [
                 "pre-commit==1.17.0",
                 "prospector==1.2.0",
                 "pylint==2.4.0"
            ]
          })
