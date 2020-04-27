#!/usr/bin/env python

import sys
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Group
from aiida.tools.importexport import export_zip

from aiida import load_profile
load_profile()

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"
EXPORT_NAME = "export_discovery_cof_27Apr20.aiida"

EXPORT = True
CLEAR = True

desired_nodes = ['orig_cif', 'orig_zeopp', 'dftopt', 'opt_cif_ddec', 'opt_zeopp', 'isot_co2', 'isot_n2', 'appl_pecoal']


def delete_old_groups():
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + "%"}})
    if qb.all():
        print("Groups '{}' found, deleting...".format(GROUP_DIR))
        for q in qb.all():
            group = q[0]
            group.clear()
            Group.objects.delete(group.pk)


# Clear and delete old groups
delete_old_groups()

# Query for all the CURATED-COFs
qb = QueryBuilder()
qb.append(Group, filters={'label': {'like': r'curated-cof\_%\_v%'}})

# Create groups for each and fill them with desired nodes
print("Finding nodes with tag:", desired_nodes)

all_new_groups = []
for q in qb.all():
    ref_group = q[0]
    mat_id = ref_group.label.split("_")[1]
    new_group = Group(label=GROUP_DIR + mat_id).store()
    all_new_groups.append(new_group)
    left_nodes = desired_nodes.copy()
    for node in ref_group.nodes:
        if TAG_KEY not in node.extras:
            sys.exit("WARNING: node <{}> has no extra '{}'".format(node.id, TAG_KEY))
        if node.extras[TAG_KEY] in left_nodes:
            new_group.add_nodes(node)
            left_nodes.remove(node.extras[TAG_KEY])
    print(mat_id, "missing nodes: ", left_nodes)

# Export these groups
if EXPORT:
    print(" ++++++ Exporting Nodes ++++++ ")
    kwargs = {
        # general
        'outfile': EXPORT_NAME,
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
    export_zip(all_new_groups, **kwargs)

# Delete new groups after the export
if CLEAR:
    delete_old_groups()
