# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals
from __future__ import print_function
import collections
from copy import copy
from os.path import join

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
import bokeh.models as bmd
from bokeh.palettes import Viridis256
from bokeh.models.widgets import RangeSlider, Select, Button, PreText, CheckboxButtonGroup
from bokeh.io import curdoc

import config
from config import quantities, presets
from figure.query import get_data_sqla as get_data
from figure.query import data_empty

html = bmd.Div(
    text=open(join(config.static_dir, "description.html")).read(), width=800)

redraw_plot = False


def get_preset_label_from_url():
    # get preset for figure from arguments
    args = curdoc().session_context.request.arguments
    try:
        preset_label = args.get('preset')[0]
    except (TypeError, KeyError):
        preset_label = 'default'

    return preset_label


def load_preset(attr, old, new):  # pylint: disable=unused-argument,redefined-builtin
    """Load preset and update sliders/plot accordingly"""
    # get figure from arguments
    try:
        preset = copy(presets[new])
    except KeyError:
        preset = copy(presets['default'])

    try:
        inp_x.value = preset.pop('x')
    except KeyError:
        pass
    try:
        inp_y.value = preset.pop('y')
    except KeyError:
        pass
    try:
        inp_clr.value = preset.pop('clr')
    except KeyError:
        pass

    # reset all filters
    for q in config.filter_list:
        filter = filters_dict[q]

        if isinstance(filter, RangeSlider):

            if q in preset.keys():
                filter.value = preset[q]
            else:
                filter.value = quantities[q]['range']

        elif isinstance(filter, CheckboxButtonGroup):

            if q in preset.keys():
                values = preset[q]
            else:
                values = quantities[q]['values']
            filter.active = [filter.tags.index(v) for v in values]


#inp_preset = Select(
#    title='Preset',
#    options=list(presets.keys()),
#    value=get_preset_label_from_url())
#inp_preset.on_change('value', load_preset)

# quantities
nq = len(quantities)
bondtypes = list(config.bondtype_dict.keys())
bondtype_colors = list(config.bondtype_dict.values())

# quantity selectors
plot_options = [(q, quantities[q]['label']) for q in config.plot_quantities]
inp_x = Select(title='X', options=plot_options)
inp_y = Select(title='Y', options=plot_options)
#inp_clr = Select(title='Color', options=plot_options)
inp_clr = Select(
    title='Color', options=plot_options + [('bond_type', 'Bond type')])


def on_filter_change(attr, old, new): # pylint: disable=unused-argument
    """Change color of plot button to blue"""
    btn_plot.button_type = 'primary'


# range sliders
# pylint: disable=redefined-builtin
def get_slider(desc, range, default=None):
    if default is None:
        default = range
    slider = RangeSlider(
        title=desc, start=range[0], end=range[1], value=default, step=0.1)

    slider.on_change('value', on_filter_change)
    return slider


def get_select(desc, values, default=None, labels=None):
    if default is None:
        # by default, make all selections active
        default = range(len(values))

    if labels is None:
        labels = map(str, values)

    # misuse tags to store values without mapping to str
    group = CheckboxButtonGroup(labels=labels, active=default, tags=values)
    group.on_change('active', on_filter_change)

    return group


filters_dict = collections.OrderedDict()
#for k, v in quantities.items():
for k in config.filter_list:
    v = quantities[k]
    if 'unit' not in v.keys():
        desc = v['label']
    else:
        desc = "{} [{}]".format(v['label'], v['unit'])

    if 'default' not in v.keys():
        v['default'] = None

    if v['type'] == 'float':
        filters_dict[k] = get_slider(desc, v['range'], v['default'])
    elif v['type'] == 'list':
        if 'labels' not in v.keys():
            v['labels'] = None
        filters_dict[k] = get_select(desc, v['values'], v['default'],
                                     v['labels'])

# plot button, output, graph
btn_plot = Button(label='Plot', button_type='primary')
info_block = PreText(text='', width=500, height=100)
plot_info = PreText(text='', width=300, height=100)

load_preset(None, None, get_preset_label_from_url())

source = bmd.ColumnDataSource(data=data_empty)
hover = bmd.HoverTool(tooltips=[])
tap = bmd.TapTool()


def create_plot():
    """Creates scatter plot.

    Note: While it is usually enough to update the data source, redrawing the
    plot is needed for bond_type coloring, when the colormap needs to change
    and the colorbar is removed.
    """
    global source
    p_new = figure(
        plot_height=600,
        plot_width=700,
        toolbar_location='below',
        tools=[
            'pan',
            'wheel_zoom',
            'box_zoom',
            'save',
            'reset',
            hover,
            tap,
        ],
        active_scroll='wheel_zoom',
        output_backend='webgl',
        title='',
        title_location='right',
    )
    p_new.title.align = 'center'
    p_new.title.text_font_size = '10pt'
    p_new.title.text_font_style = 'italic'

    if inp_clr.value == 'bond_type':
        from bokeh.transform import factor_cmap
        paper_palette = list(config.bondtype_dict.values())
        fill_color = factor_cmap(
            'color', palette=paper_palette, factors=bondtypes)
        p_new.circle(
            'x',
            'y',
            size=10,
            source=source,
            fill_color=fill_color,
            fill_alpha=0.6,
            line_alpha=0.4,
            legend='color')

    else:
        cmap = bmd.LinearColorMapper(palette=Viridis256)
        fill_color = {'field': 'color', 'transform': cmap}
        p_new.circle('x', 'y', size=10, source=source, fill_color=fill_color)
        cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
        #cbar.color_mapper = bmd.LinearColorMapper(palette=Viridis256)
        p_new.add_layout(cbar, 'right')

    return p_new


p = create_plot()

# inp_preset
controls = [inp_x, inp_y, inp_clr] + [_v for k, _v in filters_dict.items()
                                      ] + [btn_plot, plot_info]


def update_legends(ly):

    q_x = quantities[inp_x.value]
    q_y = quantities[inp_y.value]
    p = ly.children[0].children[1]

    #title = "{} vs {}".format(q_x["label"], q_y["label"])
    xlabel = "{} [{}]".format(q_x["label"], q_x["unit"])
    ylabel = "{} [{}]".format(q_y["label"], q_y["unit"])
    xhover = (q_x["label"], "@x {}".format(q_x["unit"]))
    yhover = (q_y["label"], "@y {}".format(q_y["unit"]))

    if inp_clr.value == 'bond_type':
        clr_label = "Bond type"
        hover.tooltips = [
            ("name", "@name"),
            xhover,
            yhover,
            ("Bond type", "@color"),
        ]
    else:
        q_clr = quantities[inp_clr.value]
        clr_label = "{} [{}]".format(q_clr["label"], q_clr["unit"])
        hover.tooltips = [
            ("name", "@name"),
            xhover,
            yhover,
            (q_clr["label"], "@color {}".format(q_clr["unit"])),
        ]

    p.xaxis.axis_label = xlabel
    p.yaxis.axis_label = ylabel
    p.title.text = clr_label

    url = "detail?name=@name"
    tap.callback = bmd.OpenURL(url=url)
    #tap.callback = bmd.CustomJS.from_py_func(update_tap)
    #tap.callback = bmd.CustomJS(code="""console.info("hello TapTool")""")

    #p.toolbar.active_hover = hover


# pylint: disable=unused-argument
def check_uniqueness(attr, old, new):
    selected = [inp_x.value, inp_y.value, inp_clr.value]
    unique = list(set(selected))
    if len(unique) < len(selected):
        double = [i for i in selected if i in unique or unique.remove(i)]
        double_str = ", ".join([quantities[d]['label'] for d in double])
        plot_info.text = "Warning: {} doubly selected.".format(double_str)
        btn_plot.button_type = 'danger'

    else:
        plot_info.text = ""
        btn_plot.button_type = 'primary'


def update():
    global redraw_plot, source

    #update_legends(l)

    projections = [inp_x.value, inp_y.value, inp_clr.value, 'name', 'filename']

    source.data = get_data(projections, filters_dict, quantities, plot_info)

    #if redraw_plot:
    if True:  # pylint: disable=using-constant-test
        figure = create_plot()
        #TO DO: for some reason this destroys the coupling to source.data
        # to figure out why (and then restrict this to actual redrawing scenarios)
        l.children[0].children[1] = figure
        redraw_plot = False

    update_legends(l)
    plot_info.text += " done!"
    btn_plot.button_type = 'success'
    return


btn_plot.on_click(update)


# pylint: disable=unused-argument
def on_change_clr(attr, old, new):
    """Remember to redraw plot next time, when necessary.

    When switching between bond_type color and something else,
    the plot needs to be redrawn.
    """
    global redraw_plot
    if (new == 'bond_type' or old == 'bond_type') and new != old:
        redraw_plot = True

    check_uniqueness(attr, old, new)


inp_x.on_change('value', check_uniqueness)
inp_y.on_change('value', check_uniqueness)
inp_clr.on_change('value', on_change_clr)

# Create a panel with a new layout
sizing_mode = 'fixed'
inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout(
    [
        [inputs, p],
        [info_block],
    ], sizing_mode=sizing_mode)
update()

# Create each of the tabs
tab = bmd.Panel(child=l, title='Scatter plot')
tabs = bmd.widgets.Tabs(tabs=[tab])

# Put the tabs in the current document for display
curdoc().title = "Covalent Organic Frameworks"
curdoc().add_root(layout([html, tabs]))
