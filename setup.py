#!/usr/bin/env python

from __future__ import absolute_import
from setuptools import setup

if __name__ == '__main__':
    # Provide static information in setup.json
    # such that it can be discovered automatically
    setup(packages=["detail", "figure"],
          name="bokeh-discover-section",
          author="Leopold Talirz",
          author_email="info@materialscloud.org",
          description="A template for DISCOVER sections using bokeh server.",
          license="MIT",
          classifiers=["Programming Language :: Python"],
          version="0.1.1",
          install_requires=[
              "bokeh>=1.2.0",
              "jsmol-bokeh-extension>=0.2",
              "pandas",
              "sqlalchemy",
              "requests",
              "panel",
              "param",
              "jupyter",
          ],
          extras_require={
              "pre-commit":
              ["pre-commit==1.17.0", "prospector==0.12.11", "pylint==1.9.3"]
          })
