"""Querying the DB
"""
from __future__ import absolute_import
from bokeh.models.widgets import RangeSlider, CheckboxButtonGroup
# pylint: disable=too-many-locals
data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])

get_tag = {
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
    """Query the AiiDA database

    TODO: this section needs to be fixed if more version are present for the same COF!
    TODO: add version search!
    """
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Node, Dict, Group

    filters = {}

    qb = QueryBuilder()
    qb.append(Group, project=['label'], filters={ 'label': {'like': 'curated-cof_%_v%'} }, tag='curated-cof')

    for inp in inp_list:
        if inp in  ['henry_coefficient_average_co2', 'henry_coefficient_average_n2']:
            proj = 'henry_coefficient_average' #fix to distinguish co2/n2
        else:
            proj = inp
        qb.append(Dict, project=['attributes.{}'.format(proj)], filters={'extras.curated-cof_tag': get_tag[inp]},
            with_group='curated-cof')
    print(qb.all())

    return qb.all()
