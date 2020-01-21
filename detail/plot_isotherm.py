# -*- coding: utf-8 -*-
from __future__ import print_function
from bokeh.plotting import figure
import bokeh.models as bmd
from bokeh.layouts import row
import numpy as np

def plot_isotherm(**kwargs):
    """Plot isotherm figure"""


    tooltips = [
        ("Uptake (mol/kg)", "@q_avg"),
    ]
    hover = bmd.HoverTool(tooltips=tooltips)
    TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

    pmax = 30
    p1 = figure(tools=TOOLS, height=350, width=450, x_range=(-1, pmax+1), y_range=(-1,41))
    p1.xaxis.axis_label = 'Pressure (bar)'
    p1.yaxis.axis_label = 'Uptake (mol/kg)'

    p2 = figure(tools=TOOLS, height=350, width=250, x_range=(-51, 0+1), y_range=(-1,41))
    p2.xaxis.axis_label = 'Heat of adsorption (kJ/mol)'
    p2.yaxis.axis_label = 'Uptake (mol/kg)'

    plotcolor={'co2':'red','n2':'blue'}
    plotlabel={'co2':'CO₂','n2':u'N₂'}

    version = kwargs.pop('version')
    for gas in ['co2', 'n2']:
        isot_out = kwargs['pm_' + gas]

        if version ==1: # parse Dict from curated_cofs_version_1
            isot_out = isot_out.get_dict()
            if 'henry_coefficient_average' in isot_out.keys(): #porous
                # parse isotherm for plotting
                p = [a[0] for a in isot_out['isotherm_loading']] #(bar)
                q_avg = [a[1] for a in isot_out['isotherm_loading']] #(mol/kg)
                q_dev = [a[2] for a in isot_out['isotherm_loading']] #(mol/kg)
                q_upper = np.array(q_avg) + np.array(q_dev)
                q_lower = np.array(q_avg) - np.array(q_dev)
                h_avg = [a[1] for a in isot_out['isotherm_enthalpy']] #(kJ/mol)
                h_dev = [a[2] for a in isot_out['isotherm_enthalpy']] #(kJ/mol)
                # TRICK: use the enthalpy from widom (energy-RT) which is more accurate that the one at 0.001 bar (and which also is NaN for weakly interacting systems)
                h_avg[0] = isot_out['adsorption_energy_average']-isot_out['temperature']/120.027
                h_dev[0] = isot_out['adsorption_energy_dev']
                h_upper = np.array(h_avg) + np.array(h_dev)
                h_lower = np.array(h_avg) - np.array(h_dev)
            else: #nonporous (but I have in this detail section only porous ones!)
                p = [0, pmax]
                q_avg = q_upper = q_lower = h_avg = h_upper = h_lower = [0, 0]

        elif version ==2: # parse Dict from curated_cofs_version_2
            try: #isot_out is a Dict node = porous
                isot_out = isot_out.get_dict()

                p = isot_out['isotherm']["pressure"] #(bar)
                q_avg =  isot_out['isotherm']["loading_absolute_average"]#(mol/kg)
                q_dev =  isot_out['isotherm']["loading_absolute_dev"]#(mol/kg)
                q_upper = np.array(q_avg) + np.array(q_dev)
                q_lower = np.array(q_avg) - np.array(q_dev)
                h_avg = isot_out['isotherm']["enthalpy_of_adsorption_average"] #(kJ/mol)
                h_dev = isot_out['isotherm']["enthalpy_of_adsorption_dev"] #(kJ/mol)
                # TRICK: use the enthalpy from widom (energy-RT) which is more accurate that the one at 0.001 bar (and which also is NaN for weakly interacting systems)
                h_avg[0] = isot_out['adsorption_energy_widom_average']-isot_out['temperature']/120.027
                h_dev[0] = isot_out['adsorption_energy_widom_dev']
                h_upper = np.array(h_avg) + np.array(h_dev)
                h_lower = np.array(h_avg) - np.array(h_dev)
            except: #nonporous (but I have in this detail section only porous ones!)
                p = [0, pmax]
                q_avg = q_upper = q_lower = h_avg = h_upper = h_lower = [0, 0]

        data = dict(p=p, q_avg=q_avg, q_upper=q_upper, q_lower=q_lower, h_avg=h_avg, h_upper=h_upper, h_lower=h_lower)
        source = bmd.ColumnDataSource(data=data)

        p1.line('p', 'q_avg', source=source, line_color=plotcolor[gas], line_width=2, legend_label=plotlabel[gas])
        p1.circle('p', 'q_avg', source=source, color=plotcolor[gas], size=10, legend=plotlabel[gas])
        p1.add_layout(
            bmd.Whisker(source=source, base="p", upper="q_upper", lower="q_lower") #, level="overlay")
        )

        p2.line('h_avg', 'q_avg', source=source, line_color=plotcolor[gas], line_width=2)
        p2.circle('h_avg', 'q_avg', source=source, color=plotcolor[gas], size=10)
        p2.add_layout(
            bmd.Whisker(source=source, base="h_avg", upper="h_upper", lower="h_lower", dimension='width')  # , level="overlay")
        )

    p1.legend.location = "top_left"

    fig = row(p1, p2)

    return fig
