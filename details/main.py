#!/usr/bin/env python

import panel as pn
import pandas as pd

from aiida import load_profile
from details.isotherms import plot_isotherms, get_widom_df
from details.dft_info import plot_energy_steps
from details.structure import structure_jsmol
from details.utils import get_mat_id, get_details_title, get_geom_table, get_appl_table, get_title
from pipeline_config import get_mat_nodes_dict

load_profile()

pn.extension(css_files=['details/static/style.css'])


class DetailView():

    def __init__(self):
        self.mat_id = get_mat_id()
        self.mat_nodes_dict = get_mat_nodes_dict(self.mat_id)
        print(">> Display details of MAT_ID:", self.mat_id, self.mat_nodes_dict['orig_cif'])

    def title_col(self):
        col = pn.Column(width=700)
        col.append(pn.pane.Markdown(get_details_title(self.mat_nodes_dict['orig_cif'])))
        return col

    def structure_col(self):
        nodes = self.mat_nodes_dict
        col = pn.Column(sizing_mode='stretch_width')
        col.append(get_title('Cell optimized structure', uuid=nodes['opt_cif_ddec'].uuid))
        col.append(pn.pane.Bokeh(structure_jsmol(nodes['opt_cif_ddec'])))
        col.append(get_title('Energy profile during cell optimization', uuid=nodes['dftopt'].uuid))
        col.append(pn.pane.Bokeh(plot_energy_steps(dftopt_out=nodes['dftopt'])))
        col.append(get_title('Geometric properties', uuid=nodes["opt_zeopp"].uuid))
        col.append(pn.pane.Markdown(get_geom_table(nodes["opt_zeopp"])))
        return col

    def properties_col(self):
        col = pn.Column(sizing_mode='stretch_width')
        col.append(pn.pane.Markdown('## All computed isotherms'))
        col.append(pn.pane.Bokeh(plot_isotherms(self.mat_id), sizing_mode='stretch_width'))
        col.append(pn.pane.Markdown("## All computed Henry's coefficients (mol/kg/Pa)"))
        with pd.option_context('display.max_colwidth', None):
            col.append(get_widom_df(self.mat_nodes_dict, select="kh").to_html(escape=False))
        col.append(pn.pane.Markdown("## All computed Heat of adsorption @ infinite dilution (kJ/mol)"))
        with pd.option_context('display.max_colwidth', None):
            col.append(get_widom_df(self.mat_nodes_dict, select="hoa").to_html(escape=False))
        return col

    def applications_col(self):
        col = pn.Column(sizing_mode='stretch_width')
        col.append(pn.pane.Markdown('## Numerical values for all the applications'))
        col.append(pn.pane.HTML(get_appl_table(self.mat_nodes_dict)))
        return col


dv = DetailView()

tabs = pn.Tabs(tabs_location='left', sizing_mode='stretch_width')
tabs.extend([
    ("Applications", dv.applications_col()),
    ("Properties", dv.properties_col()),
    ("Structure", dv.structure_col()),
])

page = dv.title_col()
page.append(tabs)
page.servable()
