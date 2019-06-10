# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function
from __future__ import absolute_import
from os.path import dirname, join

from bokeh.layouts import layout
import bokeh.models as bmd
from bokeh.io import curdoc

#html = bmd.Div(
#    text=open(join(dirname(__file__), "static", "table.html")).read(),
#    width=960)
#curdoc().add_root(layout([html]))

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().template_variables["figures"] = [
    ["3a", "Deliverable Capacity <i>vs</i> Density"],
    ["3b", "Surface area <i>vs</i> Density (3d COFs)"],
    ["7a", "Methane uptake (low P) <i>vs</i> Density"],
    ["7b", "Methane uptake (high P) <i>vs</i> Density"],
    ["8b", "Deliverable capacity <i>vs</i> Density (2d COFs)"],
    ["9b", "Deliverable capacity <i>vs</i> Density (3d COFs)"],
    ["11", "Deliverable capacity <i>vs</i> Surface area"],
]
