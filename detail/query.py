""" Queries to the DB
"""

def get_group_as_dict(cof_label):
    """Given a curated-cof label, queries the group and returns a dictionary with tags as keys and nodes as values.
    If multiple version are available qb.all()[0][0] shuld take the last one computed.
    """
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Group, Node
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': 'curated-cof_{}_v%'.format(cof_label)}}, tag='group')
    group_node = qb.all()[0][0]
    qb.append(Node, project=['extras.curated-cof_tag', '*'], with_group='group')

    group_dict = { k: v for k,v in qb.all() }

    group_dict.update({
        'cof_label': cof_label,
        'group': group_node,
        'version': int(group_node.label.split("_v")[-1]),
    })

    return group_dict
