import numpy as np
import pandas as pd
from bokeh.plotting import figure
import bokeh.models as bmd
from pipeline_config import gasses, get_isotherm_nodes
from details.utils import get_provenance_url, get_provenance_link


def plot_isotherms(mat_id):  #pylint: disable=too-many-locals
    """Plot figure with all isotherms."""

    nodes_dict = get_isotherm_nodes(mat_id)

    tooltips = [
        ("Molecule", "@legend_label"),
        ("Uptake (mol/kg)", "@q_avg"),
    ]
    hover = bmd.HoverTool(tooltips=tooltips)
    tap = bmd.TapTool()
    tap.callback = bmd.OpenURL(url=get_provenance_url(uuid="@uuid"))
    TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover, tap]

    p1 = figure(tools=TOOLS, height=350, width=450)
    p1.xaxis.axis_label = 'Pressure (bar)'
    p1.yaxis.axis_label = 'Uptake (mol/kg)'

    for gas, gas_dict in gasses.items():
        if gas not in nodes_dict:
            continue

        for node in nodes_dict[gas]:
            try:  # avoid to fail if there are problems with one dict
                isot_out = node.get_dict()

                if isot_out['is_porous']:
                    p = isot_out['isotherm']["pressure"]  #(bar)
                    q_avg = isot_out['isotherm']["loading_absolute_average"]  #(mol/kg)
                    q_dev = isot_out['isotherm']["loading_absolute_dev"]  #(mol/kg)
                    q_upper = np.array(q_avg) + np.array(q_dev)
                    q_lower = np.array(q_avg) - np.array(q_dev)
                    h_avg = isot_out['isotherm']["enthalpy_of_adsorption_average"]  #(kJ/mol)
                    h_dev = isot_out['isotherm']["enthalpy_of_adsorption_dev"]  #(kJ/mol)
                    # TRICK: use the enthalpy from widom (energy-RT) which is more accurate that the one at 0.001 bar
                    # (and which also is NaN for weakly interacting systems)
                    h_avg[0] = isot_out['adsorption_energy_widom_average'] - isot_out['temperature'] / 120.027
                    h_dev[0] = isot_out['adsorption_energy_widom_dev']
                    h_upper = np.array(h_avg) + np.array(h_dev)
                    h_lower = np.array(h_avg) - np.array(h_dev)
                else:
                    p = [0, 100]
                    q_avg = q_upper = q_lower = h_avg = h_upper = h_lower = [0, 0]

                legend_label = "{} ({}K)".format(gas_dict['legend'], int(isot_out['temperature']))

                data = dict(p=p,
                            q_avg=q_avg,
                            q_upper=q_upper,
                            q_lower=q_lower,
                            h_avg=h_avg,
                            h_upper=h_upper,
                            h_lower=h_lower,
                            uuid=[str(node.uuid) for _ in q_avg],
                            legend_label=[legend_label] * len(p))
                source = bmd.ColumnDataSource(data=data)

                p1.line(x='p',
                        y='q_avg',
                        source=source,
                        line_color=gas_dict['color'],
                        line_width=2,
                        legend_label=legend_label)
                p1.circle(x='p', y='q_avg', source=source, color=gas_dict['color'], size=5, legend_label=legend_label)
                p1.add_layout(bmd.Whisker(source=source, base="p", upper="q_upper", lower="q_lower"))
            except (KeyError, TypeError):
                continue

    p1.legend.location = "bottom_right"

    fig = p1

    return fig


def get_widom_df(mat_nodes_dict, select):
    """Geting a df table for all the available Henry coefficients or heat of adsorption at zero pressure.
    Options: select = "kh" or "hoa"
    """

    property_dict = {"kh": 'henry_coefficient_average', "hoa": 'adsorption_energy_widom_average'}

    temp_list = [
        77,
        198,
        298,
        300,
    ]

    pd.set_option('display.max_colwidth', None)
    df = pd.DataFrame(index=[x['legend'] for x in gasses.values()], columns=["{}K".format(x) for x in temp_list])
    df = df.fillna("-")

    for tag, node in mat_nodes_dict.items():
        try:  # will fail if tag has no "_" separation, like "dftopt"
            wc, mol = tag.split("_")
        except ValueError:
            continue

        if mol not in gasses:
            continue

        legend = gasses[mol]['legend']

        # the try...except skips problematic or nonporous results
        # NOTE: nonporous results can not be shown because the temperature of the calculation is unknown!

        try:  # avoid to fail if there are problems with one dict
            if wc in ['kh', 'isot']:
                if select == "kh":
                    val = '{:.2e}'.format(node[property_dict[select]])
                elif select == "hoa":
                    val = '{:.2f}'.format(node[property_dict[select]])
                temperature = "{}K".format(int(node['temperature']))
                df.loc[legend, temperature] = val + get_provenance_link(uuid=node.uuid)
            elif wc in ['isotmt']:
                for i, temp in enumerate(node['temperature']):
                    if select == "kh":
                        val = '{:.2e}'.format(node[property_dict[select]][i])
                    elif select == "hoa":
                        val = '{:.2f}'.format(node[property_dict[select]][i])
                    temperature = "{}K".format(int(temp))
                    df.loc[legend, temperature] = val + get_provenance_link(uuid=node.uuid)
        except (KeyError, TypeError):
            continue

    return df
