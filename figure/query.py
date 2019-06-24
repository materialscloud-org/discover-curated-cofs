"""Querying the DB
"""
from __future__ import absolute_import
from bokeh.models.widgets import RangeSlider, CheckboxButtonGroup
from .config import max_points
from six.moves import map
from six.moves import zip
# pylint: disable=too-many-locals
data_empty = dict(x=[0], y=[0], uuid=['1234'], color=[0], name=['no data'])


def get_data_aiida(projections, sliders_dict, quantities):
    """Query the AiiDA database"""
    from aiida import load_dbenv, is_dbenv_loaded
    from aiida.backends import settings
    if not is_dbenv_loaded():
        load_dbenv(profile=settings.AIIDADB_PROFILE)
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm.data.parameter import ParameterData
    from aiida.orm.data.structure import StructureData
    from aiida.orm import WorkCalculation, Node

    filters = {}
    #projections = projections[:3]

    #def add_range_filter(bounds, label):
    #    # a bit of cheating until this is resolved
    #    # https://github.com/aiidateam/aiida_core/issues/1389
    #    #filters['attributes.'+label] = {'>=':bounds[0]}
    #    filters['attributes.' + label] = {
    #        'and': [{
    #            '>=': bounds[0]
    #        }, {
    #            '<': bounds[1]
    #        }]
    #    }

    #for k, v in sliders_dict.items():
    #    # Note: filtering is costly, avoid if possible
    #    if not v.value == quantities[k]['range']:
    #        add_range_filter(v.value, k)
    
    qb = QueryBuilder()
    qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, tag='collect')

    # Note: This implementation is faster but does not preserve the order of projections 
    #       Could still use it but would need to reorder the columns before returning.
    # qb.append(WorkCalculation, filters={ 'attributes.function_name': {'==': 'collect_outputs'} }, tag='collect')
    # for link_label in link_attribute_dict:
    #     link_projections = [ 'attributes.' + p for p in projections if p in link_attribute_dict[link_label]]
    #     if link_projections:
    #         print(link_projections)
    #         qb.append(ParameterData, project=link_projections, edge_filters={'label': link_label}, input_of='collect')

    for p in projections:
        for link_label in link_attribute_dict:
            if p in link_attribute_dict[link_label]:
               print(p)
               qb.append(ParameterData, project=['attributes.' + p], edge_filters={'label': link_label}, input_of='collect')

    #     if link_projections:
    #         print(link_projections)
    #         qb.append(ParameterData, project=link_projections, edge_filters={'label': link_label}, input_of='collect')
    qb.append(StructureData, project=['label', 'uuid'], edge_filters={'label': 'ref_structure'}, input_of='collect')    

    return qb.all()

    #nresults = qb.count()
    #if nresults == 0:
    #    plot_info.text = "No matching COFs found."
    #    return data_empty

    #plot_info.text = "{} COFs found. Plotting...".format(nresults)


    ## x,y position
    #x, y, clrs, uuids, names, cif_uuids = list(zip(*qb.all()))
    #plot_info.text = "{} COFs queried".format(nresults)
    #x = list(map(float, x))
    #y = list(map(float, y))
    #cif_uuids = list(map(str, cif_uuids))
    #uuids = list(map(str, uuids))

    #if projections[2] == 'bond_type':
    #    #clrs = map(lambda clr: bondtypes.index(clr), clrs)
    #    clrs = list(map(str, clrs))
    #else:
    #    clrs = list(map(float, clrs))

    #return qb.all()
    #return dict(x=x, y=y, uuid=cif_uuids, color=clrs, name=names)
