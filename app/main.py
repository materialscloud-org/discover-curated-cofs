# -*- coding: utf-8 -*-
from os.path import dirname, join
from aiida import load_dbenv, is_dbenv_loaded
from aiida.backends import settings
if not is_dbenv_loaded():
    load_dbenv(profile=settings.AIIDADB_PROFILE)

import bokeh.models as bmd
from bokeh.io import curdoc
from bokeh.layouts import layout
from plot import tab_plot

html = bmd.Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create each of the tabs
tabs = bmd.widgets.Tabs(tabs = [tab_plot()])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
