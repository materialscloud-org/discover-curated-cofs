#!/usr/bin/env python
# coding: utf-8
import panel as pn
from os.path import join, dirname, realpath

THIS_DIR = dirname(realpath(__file__))

info_md = open(join(THIS_DIR, "info.md")).read()

pn.extension()

t = pn.Column(width=700)
t.append(pn.pane.HTML('<a href="results"><< Go Back</a>'))
t.append(pn.pane.Markdown(info_md))
t.servable()
