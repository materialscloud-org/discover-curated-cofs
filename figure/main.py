# coding: utf-8
from aiida import load_profile
import config
import bokeh.models as bmd

load_profile()


def get_plot(inp_x, inp_y, inp_clr):

    # query for results
    from figure.query import get_data_aiida
    inp_list = [inp_x, inp_y, inp_clr]
    results_wnone = get_data_aiida(inp_list)  #returns [inp_x_value, inp_y_value, inp_clr_value, cof-id]
    # dump None lists that make bokeh crash! TODO: improve!
    results = []
    for l in results_wnone:
        if not None in l:
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
    cof_label = [x.split("_")[1] for x in group_label]

    data = {'x': x, 'y': y, 'color': clrs, 'name': cof_label}

    # create bokeh plot
    import bokeh.plotting as bpl
    from bokeh.palettes import Plasma256

    source = bmd.ColumnDataSource(data=data)

    # Todo: If possible, setting the axis scale should be moved to "update_legends"
    q_x = config.quantities[inp_x]
    q_y = config.quantities[inp_y]

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
        #active_scroll='box_zoom',
        active_drag='box_zoom',
        output_backend='webgl',
        title='',
        title_location='right',
        x_axis_type=q_x['scale'],
        y_axis_type=q_y['scale'],
    )
    p_new.title.align = 'center'
    p_new.title.text_font_size = '10pt'
    p_new.title.text_font_style = 'italic'

    update_legends(p_new, inp_x, inp_y, inp_clr, hover, tap)

    cmap = bmd.LinearColorMapper(palette=Plasma256, low=min(clrs), high=max(clrs))
    fill_color = {'field': 'color', 'transform': cmap}
    p_new.circle('x', 'y', size=10, source=source, fill_color=fill_color)
    cbar = bmd.ColorBar(color_mapper=cmap, location=(0, 0))
    #cbar.color_mapper = bmd.LinearColorMapper(palette=Viridis256)
    p_new.add_layout(cbar, 'right')

    return p_new, msg


def update_legends(p, inp_x, inp_y, inp_clr, hover, tap):

    q_x = config.quantities[inp_x]
    q_y = config.quantities[inp_y]

    #title = "{} vs {}".format(q_x["label"], q_y["label"])
    xlabel = "{} [{}]".format(q_x["label"], q_x["unit"])
    ylabel = "{} [{}]".format(q_y["label"], q_y["unit"])
    xhover = (q_x["label"], "@x {}".format(q_x["unit"]))
    yhover = (q_y["label"], "@y {}".format(q_y["unit"]))

    q_clr = config.quantities[inp_clr]
    if 'unit' not in q_clr.keys():
        clr_label = q_clr["label"]
        clr_val = "@color"
    else:
        clr_val = "@color {}".format(q_clr['unit'])
        clr_label = "{} [{}]".format(q_clr["label"], q_clr["unit"])

    hover.tooltips = [
        ("name", "@name"),
        xhover,
        yhover,
        (q_clr["label"], clr_val),
    ]

    q_clr = config.quantities[inp_clr]
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

    url = "detail?id=@name"
    tap.callback = bmd.OpenURL(url=url)


import panel as pn
import param
import config
from collections import OrderedDict

pn.extension()
plot_dict = OrderedDict(((config.quantities[q]['label'], q) for q in config.quantities))


class StructurePropertyVisualizer(param.Parameterized):

    x = param.Selector(objects=plot_dict, default=config.presets["default"]["x"])
    y = param.Selector(objects=plot_dict, default=config.presets["default"]["y"])
    color = param.Selector(objects=OrderedDict(plot_dict), default=config.presets["default"]["clr"])
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

gspec = pn.GridSpec(sizing_mode='stretch_both', max_width=900)
gspec[0, 0] = explorer.param
gspec[:2, 1:4] = explorer.plot
gspec[1, 0] = explorer.msg

gspec.servable()
