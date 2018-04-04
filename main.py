# -*- coding: utf-8 -*-
from __future__ import print_function
import collections
from os.path import dirname, join

from aiida import load_dbenv, is_dbenv_loaded
from aiida.backends import settings
if not is_dbenv_loaded():
    load_dbenv(profile=settings.AIIDADB_PROFILE)
from aiida.orm import load_node
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm.data.parameter import ParameterData

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import RangeSlider, Select, TextInput, Button
from bokeh.io import curdoc

import numpy as np

html = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# quantities
quantities = collections.OrderedDict([
    ('density', dict(label='Density', range=[10.0,1200.0], default=[1000.0,1200.0], unit='kg/m^3')),
    ('deliverable_capacity', dict(label='Deliverable capacity', range=[0.0,300.0], unit='v STP/v')),
    ('absolute_methane_uptake_high_P', dict(label='CH4 uptake High-P', range=[0.0,200.0], unit='mol/kg')),
    ('absolute_methane_uptake_low_P', dict(label='CH4 uptake Low-P', range=[0.0,200.0], unit='mol/kg')),
    ('heat_desorption_high_P', dict(label='CH4 heat of desorption High-P', range=[0.0,30.0], unit='kJ/mol')),
    ('heat_desorption_low_P', dict(label='CH4 heat of desorption Low-P', range=[0.0,30.0], unit='kJ/mol')),    
    ('supercell_volume', dict(label='Supercell volume', range=[0.0,1000000.0], unit='A^3')),
    ('surface_area', dict(label='Geometric surface area', range=[0.0,12000.0], unit='m^2/g')),
])
nq = len(quantities)

bondtype_dict = collections.OrderedDict([
    ('amide', "#1f77b4"), ('amine', "#d62728"), ('imine', "#ff7f0e"),
    ('CC', "#2ca02c"), ('mixed', "#778899"),
])
bondtypes = list(bondtype_dict.keys())
bondtype_colors = list(bondtype_dict.values())

# sliders
#inp_pks = ipw.Text(description='PKs', placeholder='e.g. 1006 1009 (space separated)', layout=layout, style=style)

def get_slider(desc, range, default=None):
    if default is None:
        default = range
    #marks = { i : str(i) for i in np.linspace(range[0], range[1], 10) }
    slider = RangeSlider(title=desc, start=range[0], end=range[1], value=default, step=0.1)
    return slider

sliders_dict = collections.OrderedDict()
for k,v in quantities.iteritems():
    desc = "{} [{}]: ".format(v['label'], v['unit'])
    if not 'default' in v.keys():
        v['default'] = None

    sliders_dict[k] = get_slider(desc, v['range'], v['default'])


# selectors
plot_options = [ (k, v['label']) for k,v in quantities.iteritems() ]
inp_x = Select(title='X', options=plot_options, value='density')
inp_y = Select(title='Y', options=plot_options, value='deliverable_capacity')
inp_clr = Select(title='Color', options=plot_options, value='supercell_volume')

btn_plot = Button(label='Plot')

source = ColumnDataSource(data=dict(x=[], y=[], uuid=[], color=[]))

p = figure(
    plot_height=600, plot_width=700,
    toolbar_location=None,
    tools=['tap', 'zoom_in', 'zoom_out', 'pan'],
    output_backend='webgl',
)
p.circle('x', 'y', size=10, source=source)
#p.circle('x', 'y', size=10, source=source, fill_color={'field':'color', 'transform':cmap})

#fig.add_layout(cbar, 'right')

#taptool = fig.select(type=bmd.TapTool)
#url="{}/@uuid".format(rest_url)
#taptool.callback = bmd.OpenURL(url=url)

controls = list(sliders_dict.values()) + [inp_x, inp_y, inp_clr, btn_plot]

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [html],
    [inputs, p],],
    sizing_mode = sizing_mode)


def update_legends():

    q_x = quantities[inp_x.value]
    q_y = quantities[inp_y.value]
    q_clr = quantities[inp_clr.value]

    title = "{} vs {}".format(q_x["label"], q_y["label"])
    xlabel = "{} [{}]".format(q_x["label"], q_x["unit"])
    ylabel = "{} [{}]".format(q_y["label"], q_y["unit"])
    clr_label = "{} [{}]".format(q_clr["label"], q_clr["unit"])

    p.xaxis.axis_label = xlabel
    p.yaxis.axis_label = ylabel

    # here: use labels of selected quantities
    hover = HoverTool(tooltips=[
        (q_x["label"], "@x"),
        (q_y["label"], "@y"),
        ("uuid", "@uuid")
    ])


def update():
    source.data = get_data()
    update_legends()
    return



#@app.callback(
#    dash.dependencies.Output('hover_info', 'children'),
#    [dash.dependencies.Input('scatter_plot', 'hoverData')])
#def update_text(hoverData):
#    if hoverData is None:
#        return ""
#
#    uuid = hoverData['points'][0]['customdata']
#    rest_url = 'http://localhost:8000/explore/sssp/details/'
#
#    node = load_node(uuid)
#    attrs = node.get_attrs()
#    s = "[View AiiDA Node]({})\n".format(rest_url+uuid)
#    for k,v in attrs.iteritems():
#        if 'units' in k:
#            continue
#        s += " * {}: {}\n".format(k,v)
#
#    return s
#
##@app.callback(
##    dash.dependencies.Output('url_bar', 'pathname'),
##    [dash.dependencies.Input('scatter_plot', 'clickData')])
##def update_url(figure, hoverData):
##    if hoverData is None:
##        return 
##
##    point = clickData['points'][0]
##
##    uuid = point['customdata']
##    rest_url = 'http://localhost:8000/explore/sssp/details'
##
##    return rest_url + uuid
#
##@app.callback(
##    dash.dependencies.Output('scatter_plot', 'figure'),
##    [dash.dependencies.Input('scatter_plot', 'figure'), 
##     dash.dependencies.Input('scatter_plot', 'hoverData')])
##def update_annotation(figure, hoverData):
##    if hoverData is None:
##        return figure
##
##    point = hoverData['points'][0]
##
##    uuid = point['customdata']
##    rest_url = 'http://localhost:8000/explore/sssp/details'
##
##    annotation = dict(x=point['x'], y=point['y'], 
##            text='<a href="{}/{}">o</a>'.format(rest_url, uuids))
##
##    figure['layout']['annotations'] = [annotation]
##    return figure
#
#@app.callback(
#    dash.dependencies.Output('click_info', 'children'),
#    [dash.dependencies.Input('scatter_plot', 'clickData')])
#def display_click_data(clickData):
#    if clickData is None:
#        return ""
#
#    rest_url = 'http://localhost:8000/explore/sssp/details/'
#    uuid = clickData['points'][0]['customdata']
#
#    #redirect(rest_url+uuid, code=302)
#    #return "clicked" + uuid
#    redirect_string="<script>window.location.href='{}';</script>".format(rest_url+uuid)
#    return redirect_string


def get_data():
    """Query AiiDA database"""

    filters = {}
    #pk_list = inp_pks.value.strip().split()
    #if pk_list:
    #    filters['id'] = {'in': pk_list}

    def add_range_filter(bounds, label):
        filters['attributes.'+label] = {'and':[{'>=':bounds[0]}, {'<':bounds[1]}]}

    for k,v in sliders_dict.iteritems():
        add_range_filter(v.value, k)

    qb = QueryBuilder()
    qb.append(ParameterData,
          filters=filters,
          project = ['attributes.'+inp_x.value, 'attributes.'+inp_y.value, 
                     'attributes.'+inp_clr.value, 'uuid']
    )

    nresults = qb.count()
    print("Results: {}".format(nresults))
    if nresults == 0:
        print("No results found.")
        #query_message.value = "No results found."
        return

    #query_message.value = "{} results found. Plotting...".format(nresults)

    # x,y position
    x, y, clrs, uuids = zip(*qb.all())
    x = map(float, x)
    y = map(float, y)

    clrs = map(float, clrs)

    uuids = map(str, uuids)

    return  dict(x=x, y=y, uuid=uuids, color=clrs)

# initial update
btn_plot.on_click(update)
update()

curdoc().add_root(l)
curdoc().title = "COF structures"

