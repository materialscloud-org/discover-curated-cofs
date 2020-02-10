"""Querying the DB."""


def get_data_aiida(q_list):
    """Query the AiiDA database for a list of quantities."""
    from aiida.orm.querybuilder import QueryBuilder
    from aiida.orm import Node, Dict, Group

    filters = {}

    qb = QueryBuilder()
    qb.append(Group, project=['label'], filters={'label': {'like': 'curated-cof\_%\_v%'}}, tag='curated-cof')

    for q in q_list:
        qb.append(Dict,
                  project=['attributes.{}'.format(q['key'])],
                  filters={'extras.curated-cof_tag': q['dict']},
                  with_group='curated-cof')

    return qb.all()
