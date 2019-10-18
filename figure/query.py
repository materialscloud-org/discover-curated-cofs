"""Querying the DB
"""
from __future__ import absolute_import
from bokeh.models.widgets import RangeSlider, CheckboxButtonGroup
# pylint: disable=too-many-locals
data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])

get_link = {
    'PE': 'pe_out',
    'WCg': 'pe_out',
    'WCv': 'pe_out',
    'Pur': 'pe_out',
    'Density': 'opt_zeopp_out',
    'ASA_m^2/g': 'opt_zeopp_out',
    'AV_Volume_fraction': 'opt_zeopp_out',
    'henry_coefficient_average_co2': 'isot_co2_out',
    'henry_coefficient_average_n2': 'isot_n2_out',
}

def get_data_aiida(inp_list):
    """Query the AiiDA database"""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Node, Dict, WorkFunctionNode

    filters = {}

    qb = QueryBuilder()
    qb.append(WorkFunctionNode, filters={ 'attributes.function_name': {'==': 'link_outputs'} }, tag='link')

    for inp in inp_list:
        if inp in  ['henry_coefficient_average_co2', 'henry_coefficient_average_n2']:
            proj = 'henry_coefficient_average' #fix to distinguish co2/n2
        else:
            proj = inp
        qb.append(Dict, project=['attributes.{}'.format(proj)], edge_filters={'label': get_link[inp]}, with_outgoing='link')
    qb.append(Node, project=['label'], edge_filters={'label': 'orig_cif'}, with_outgoing='link')

    return qb.all()
