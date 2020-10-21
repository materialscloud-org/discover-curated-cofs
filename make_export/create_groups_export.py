#!/usr/bin/env python
"""Utility to create the export for www.materialscloud.org/discover/curated-cofs.
Since October 2020 it is made to include all the nodes that are mentioned in the ACS Central Science Outlook.
"""

import sys
import datetime
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group
from aiida.tools.importexport.dbexport import export  # Updated to AiiDA v1.3.0

from pipeline_config import load_profile
load_profile()

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"
EXPORT_FILE_NAME = "export_discovery_cof_{}.aiida".format(datetime.date.today().strftime(r'%d%b%y'))

EXPORT = False
CLEAR = False

dis_nodes = [  # only selected nodes
    'orig_cif', 'orig_zeopp', 'dftopt', 'opt_cif_ddec', 'opt_zeopp', 'isot_co2', 'isot_n2', 'isotmt_h2', 'isot_ch4',
    'isot_o2', 'kh_xe', 'kh_kr', 'kh_h2s', 'kh_h2o', 'appl_pecoal', 'appl_peng', 'appl_h2storage', 'appl_ch4storage',
    'appl_o2storage', 'appl_xekrsel', 'appl_h2sh2osel'
]


def delete_groups():
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + "%"}})
    if qb.all():
        print("Groups '{}' found, deleting...".format(GROUP_DIR))
        for q in qb.all():
            group = q[0]
            group.clear()
            Group.objects.delete(group.pk)
    else:
        print("No previous Group {} found to delete.".format(GROUP_DIR))


# Clear and delete CSS groups created in a previous session
delete_groups()

# Query for all the CURATED-COFs
qb = QueryBuilder()
qb.append(Group, filters={'label': {'like': r'curated-cof\_%\_v%'}})
all_groups = qb.all(flat=True)  #

# Create groups for each and fill them with desired nodes
print("Creating discovery groups, with tagged nodes:", dis_nodes)

all_dis_groups = []
for full_group in all_groups:
    mat_id = full_group.label.split("_")[1]
    dis_group = Group(label=GROUP_DIR + mat_id).store()
    all_dis_groups.append(dis_group)
    left_nodes = dis_nodes.copy()
    for node in full_group.nodes:
        if TAG_KEY not in node.extras:
            sys.exit("WARNING: node <{}> has no extra '{}'".format(node.id, TAG_KEY))
        if node.extras[TAG_KEY] in left_nodes:
            dis_group.add_nodes(node)
            left_nodes.remove(node.extras[TAG_KEY])
            if node.extras[TAG_KEY] == 'orig_cif':  #to change at a certain point!
                dis_group.set_extra('mat_id', mat_id)
                for extra_key in ['doi_ref', 'workflow_version', 'name_conventional', 'class_material']:
                    extra_val = node.extras[extra_key]
                    dis_group.set_extra(extra_key, extra_val)

    print(mat_id, "missing nodes for discovery: ", left_nodes)

# Export these groups
if EXPORT:
    print(" ++++++ Exporting Nodes ++++++ ")
    kwargs = {
        # general
        'entities': all_dis_groups,
        'filename': EXPORT_FILE_NAME,
        'overwrite': True,
        'silent': False,
        'use_compression': True,
        # trasversal rules
        'input_calc_forward': False,  #cli default: False
        'input_work_forward': False,  #cli default: False
        'create_backward': True,  #cli default: True
        'return_backward': True,  #cli default: False
        'call_calc_backward': True,  #cli default: False
        'call_work_backward': True,  #cli default: False
        # include
        'include_comments': True,  #cli default: True
        'include_logs': True,  #cli default: True
    }
    export(**kwargs)

# Delete new groups after the export
if CLEAR:
    delete_groups()
