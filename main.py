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
import bokeh.models as bmd
from bokeh.palettes import Viridis256, Viridis5
from bokeh.models.widgets import RangeSlider, Select, TextInput, Button, PreText
from bokeh.io import curdoc

import numpy as np

html = bmd.Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# quantities
quantities = collections.OrderedDict([
    ('density', dict(label='Density', range=[10.0,1200.0], unit='kg/m^3')),
    ('deliverable_capacity', dict(label='Deliverable capacity', range=[0.0,300.0], default=[175,300], unit='v STP/v')),
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

#inp_pks = ipw.Text(description='PKs', placeholder='e.g. 1006 1009 (space separated)', layout=layout, style=style)

# sliders
def get_slider(desc, range, default=None):
    if default is None:
        default = range
    return RangeSlider(title=desc, start=range[0], end=range[1], value=default, step=0.1)

sliders_dict = collections.OrderedDict()
for k,v in quantities.iteritems():
    desc = "{} [{}]".format(v['label'], v['unit'])
    if not 'default' in v.keys():
        v['default'] = None

    sliders_dict[k] = get_slider(desc, v['range'], v['default'])


# selectors
plot_options = [ (k, v['label']) for k,v in quantities.iteritems() ]
inp_x = Select(title='X', options=plot_options, value='density')
inp_y = Select(title='Y', options=plot_options, value='deliverable_capacity')
inp_clr = Select(title='Color', options=plot_options, value='surface_area')
#inp_clr = Select(title='Color', options=plot_options + [('bond_type', 'Bond type')], value='surface_area')

# plot button, output, graph
btn_plot = Button(label='Plot')
info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)

data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])
source = bmd.ColumnDataSource(data=data_empty)
hover = bmd.HoverTool(tooltips=[])
tap = bmd.TapTool()


p = figure(
    plot_height=600, plot_width=700,
    toolbar_location='below',
    tools=['pan', 'wheel_zoom', 'save', 'reset', 'zoom_in', 'zoom_out', hover, tap],
    active_scroll = 'wheel_zoom',
    output_backend='webgl',
    title='',
    title_location='right',
)

# cbar
cmap = bmd.LinearColorMapper(palette=Viridis256)
cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
p.add_layout(cbar, 'right')
# misusing plot title for cbar label
# https://stackoverflow.com/a/49517401
p.title.align = 'center'
p.title.text_font_size = '10pt'
p.title.text_font_style = 'italic'

# graph
p.circle('x', 'y', size=10, source=source, 
        fill_color={'field':'color', 'transform':cmap})

controls = list(sliders_dict.values()) + [inp_x, inp_y, inp_clr, btn_plot, plot_info]

sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
        [html],
        [inputs, p],
        [info_block],
    ],
    sizing_mode = sizing_mode)

#def update_tap(source=source, window=None):
#    info_block.text = "here"
#    print("here")
#    print(source)
#    print(cb_obj.value)


def update_legends():

    q_x = quantities[inp_x.value]
    q_y = quantities[inp_y.value]

    title = "{} vs {}".format(q_x["label"], q_y["label"])
    xlabel = "{} [{}]".format(q_x["label"], q_x["unit"])
    ylabel = "{} [{}]".format(q_y["label"], q_y["unit"])
    xhover = (q_x["label"], "@x {}".format(q_x["unit"]))
    yhover = (q_y["label"], "@y {}".format(q_y["unit"]))

    #if inp_clr.value == 'bond_type':
    #    clr_label = "Bond type"
    #    hover.tooltips = [
    #        ("name", "@name"), xhover, yhover
    #    ]
    #else:
    q_clr = quantities[inp_clr.value]
    clr_label = "{} [{}]".format(q_clr["label"], q_clr["unit"])
    hover.tooltips = [
        ("name", "@name"), xhover, yhover,
        (q_clr["label"], "@color {}".format(q_clr["unit"])),
    ]

    p.xaxis.axis_label = xlabel
    p.yaxis.axis_label = ylabel

    #cbar.title = clr_label
    p.title.text = clr_label


    url="http://localhost:8000/explore/sssp/details/@uuid"
    tap.callback = bmd.OpenURL(url=url)
    #tap.callback = bmd.CustomJS.from_py_func(update_tap)
    #tap.callback = bmd.CustomJS(code="""console.info("hello TapTool")""")

    #p.toolbar.active_hover = hover

def update():
    source.data = get_data()

    #if inp_clr.value == 'bond_type':

    #    cmap = bmd.CategoricalColorMapper(
    #            palette=bondtype_colors, factors = bondtypes)
    #    #cmap = bmd.LinearColorMapper(palette=Viridis5)
    #    #cbar.ticker = bmd.BasicTicker(desired_num_ticks=5)
    #    #colorbar.set_ticklabels(bondtypes)
    #    p.legend = 'bond_type'

    #else:
    #    cmap = bmd.LinearColorMapper(palette=Viridis256)
    cmap.low = min(source.data['color'])
    cmap.high = max(source.data['color'])

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


def get_data():
    """Query the AiiDA database"""

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
                     'attributes.'+inp_clr.value, 'uuid', 'attributes.name']
    )

    nresults = qb.count()
    if nresults == 0:
        plot_info.text = "No matching COFs found."
        return data_empty

    plot_info.text = "{} COFs found. Plotting...".format(nresults)

    # x,y position
    x, y, clrs, uuids, names = zip(*qb.all())
    x = map(float, x)
    y = map(float, y)
    uuids = map(str, uuids)

    #if inp_clr.value == 'bond_type':
    #    #clrs = map(lambda clr: bondtypes.index(clr), clrs)
    #    clrs = map(str, clrs)
    #else:
    clrs = map(float, clrs)

    return  dict(x=x, y=y, uuid=uuids, color=clrs, name=names)

# initial update
btn_plot.on_click(update)
update()

curdoc().add_root(l)
curdoc().title = "COF structures"

