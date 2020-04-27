# coding: utf-8
import config
import panel as pn
import param
from collections import OrderedDict
import bokeh.models as bmd
import bokeh.plotting as bpl
from bokeh.palettes import Plasma256

from aiida import load_profile
load_profile()

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"


def get_data_aiida(q_list):
    """Query the AiiDA database for a list of quantities."""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Dict, Group

    qb = QueryBuilder()
    qb.append(Group, project=['label'], filters={'label': {'like': GROUP_DIR + "%"}}, tag='g')

    for q in q_list:
        qb.append(Dict,
                  project=['attributes.{}'.format(q['key'])],
                  filters={'extras.{}'.format(TAG_KEY): q['dict']},
                  with_group='g')

    return qb.all()


def update_legends(p, q_list, hover):
    hover.tooltips = [
        ("COF ID", "@mat_id"),
        (q_list[0]["label"], "@x {}".format(q_list[0]["unit"])),
        (q_list[1]["label"], "@y {}".format(q_list[1]["unit"])),
        (q_list[2]["label"], "@color {}".format(q_list[2]["unit"])),
    ]

    p.xaxis.axis_label = "{} [{}]".format(q_list[0]["label"], q_list[0]["unit"])
    p.yaxis.axis_label = "{} [{}]".format(q_list[1]["label"], q_list[1]["unit"])
    p.title.text = "{} [{}]".format(q_list[2]["label"], q_list[2]["unit"])


def get_plot(inp_x, inp_y, inp_clr):
    """Returns a Bokeh plot of the input values, and a message with the number of COFs found."""
    q_list = [config.quantities[label] for label in [inp_x, inp_y, inp_clr]]
    results_wnone = get_data_aiida(q_list)  #returns [inp_x_value, inp_y_value, inp_clr_value, group.label]

    # dump None lists that make bokeh crash
    results = []
    for l in results_wnone:
        if None not in l:
            results.append(l)

    # prepare data for plotting
    nresults = len(results)
    if not results:
        results = [[0, 0, 0, 'no data']]
        msg = "No matching COFs found."
    else:
        msg = "{} COFs found.<br> <b>Click on any point for details!</b>".format(nresults)

    group_label, x, y, clrs = zip(*results)
    x = list(map(float, x))
    y = list(map(float, y))
    clrs = list(map(float, clrs))
    mat_id = [x.split("/")[1] for x in group_label]

    data = {'x': x, 'y': y, 'color': clrs, 'mat_id': mat_id}

    # create bokeh plot
    source = bmd.ColumnDataSource(data=data)

    hover = bmd.HoverTool(tooltips=[])
    tap = bmd.TapTool()
    p_new = bpl.figure(
        plot_height=600,
        plot_width=600,
        toolbar_location='above',
        tools=[
            'pan',
            'wheel_zoom',
            'box_zoom',
            'save',
            'reset',
            hover,
            tap,
        ],
        active_drag='box_zoom',
        output_backend='webgl',
        title='',  # trick: title is used as the colorbar label
        title_location='right',
        x_axis_type=q_list[0]['scale'],
        y_axis_type=q_list[1]['scale'],
    )
    p_new.title.align = 'center'
    p_new.title.text_font_size = '10pt'
    p_new.title.text_font_style = 'italic'
    update_legends(p_new, q_list, hover)
    tap.callback = bmd.OpenURL(url="detail?mat_id=@mat_id")

    # Plot vertical line for comparison with amine-based technology (PE=1MJ/kg)
    if inp_y == 'CO2 parasitic energy (coal)':
        hline = bmd.Span(location=1, dimension='width', line_dash='dashed', line_color='grey', line_width=3)
        p_new.add_layout(hline)
        hline_descr = bmd.Label(x=30, y=1, x_units='screen', text_color='grey', text='amine-based sep.')
        p_new.add_layout(hline_descr)

    cmap = bmd.LinearColorMapper(palette=Plasma256, low=min(clrs), high=max(clrs))
    fill_color = {'field': 'color', 'transform': cmap}
    p_new.circle('x', 'y', size=10, source=source, fill_color=fill_color)
    cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
    p_new.add_layout(cbar, 'right')

    return p_new, msg


pn.extension()
plot_dict = OrderedDict(((config.quantities[q]['label'], q) for q in config.quantities))


class StructurePropertyVisualizer(param.Parameterized):

    x = param.Selector(objects=plot_dict, default='CO2 Henry coefficient')
    y = param.Selector(objects=plot_dict, default='CO2 parasitic energy (coal)')
    color = param.Selector(objects=OrderedDict(plot_dict), default='Geometric Void Fraction')
    msg = pn.pane.HTML("")
    _plot = None  # reference to current plot

    @param.depends('x', 'y', 'color')
    def plot(self):
        selected = [self.x, self.y, self.color]
        unique = set(selected)
        if len(unique) < len(selected):
            self.msg.object = "<b style='color:red;'>Warning: {} contains duplicated selections.</b>".format(", ".join(
                [config.quantities[s]['label'] for s in selected]))
            return self._plot

        self._plot, self.msg.object = get_plot(self.x, self.y, self.color)
        return self._plot


explorer = StructurePropertyVisualizer()

gspec = pn.GridSpec(sizing_mode='stretch_both', max_width=1000, max_height=300)
gspec[0, 0] = explorer.param
gspec[:2, 1:4] = explorer.plot
gspec[1, 0] = explorer.msg

gspec.servable()
