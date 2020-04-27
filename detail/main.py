import os
import panel as pn
from bokeh.io import curdoc

from aiida import load_profile
load_profile()

TAG_KEY = "tag4"
GROUP_DIR = "discover_curated_cofs/"


def get_mat_id():
    """Get structure label from URL parameter mat_id."""
    try:
        name = curdoc().session_context.request.arguments.get('mat_id')[0]
        if isinstance(name, bytes):
            mat_id = name.decode()
    except (TypeError, KeyError, AttributeError):
        mat_id = '05001N2'  # equivalent of http://localhost:5006/detail?mat_id=05001N2

    return mat_id


def provenance_link(uuid, label=None):
    """Return pn.HTML representation of provenance link."""

    if label is None:
        label = "Browse provenance\n" + uuid

    logo_url = "detail/static/images/aiida-128.png"
    explore_url = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")
    return pn.pane.HTML(
        "<a href='{url}/details/{uuid}' target='_blank'><img src={logo_url} title='{label}' style='width: 20px;  height: auto;'></a>"
        .format(url=explore_url, uuid=uuid, label=label, logo_url=logo_url),
        align='center')


def get_title(text, uuid=None):
    """Return pn.Row representation of title.

    Includes provenance link, if uuid is specified.
    """
    title = pn.Row(pn.pane.Markdown('#### ' + text), align='start')

    if uuid is not None:
        title.append(provenance_link(uuid))

    return title


def get_mat_dict(mat_id):
    """Given a curated-cof label, queries the group and returns a dictionary with tags as keys and nodes as values.
    If multiple version are available qb.all()[0][0] shuld take the last one computed.
    """
    from aiida.orm.querybuilder import QueryBuilder  #pylint: disable=import-outside-toplevel
    from aiida.orm import Group, Node  #pylint: disable=import-outside-toplevel
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': GROUP_DIR + mat_id}}, tag='group')
    qb.append(Node, project=['extras.{}'.format(TAG_KEY), '*'], with_group='group')

    mat_dict = {}
    for k, v in qb.all():
        mat_dict[k] = v

    return mat_dict


# pylint: disable=import-outside-toplevel
class DetailView():

    def __init__(self):
        self.mat_id = get_mat_id()  # get CURATED-COF-ID
        self.mat_dict = get_mat_dict(self.mat_id)  # get linking group

    def graph(self):
        from detail.graph import get_graph
        column = pn.Column(pn.pane.SVG(get_graph(self.mat_dict)))
        column.append("CURATED-COF {}".format(self.mat_id))
        return column

    def dft_plot(self):
        from detail.structure import structure_jsmol
        from detail.plot_cp2k import plot_energy_steps, print_bandgap
        dftopt_node = self.mat_dict['dftopt']
        opt_cif_ddec = self.mat_dict['opt_cif_ddec']
        column = pn.Column()
        column.append(get_title("DFT-optimized structure for " + self.mat_id, uuid=opt_cif_ddec.uuid))
        column.append(pn.pane.Bokeh(structure_jsmol(cif_str=opt_cif_ddec.get_content())))
        column.append(pn.Row(pn.pane.Markdown('')))  # Some space
        column.append(get_title("Energy profile of the DFT optimization " + self.mat_id, uuid=dftopt_node.uuid))
        column.append(pn.pane.Bokeh(plot_energy_steps(dftopt_node)))
        column.append(pn.Row(pn.pane.Markdown('#### {}'.format(print_bandgap(dftopt_node))), align='start'))
        return column

    def iso_plot(self):
        from detail.plot_isotherm import plot_isotherm
        isot_co2 = self.mat_dict['isot_co2']
        isot_n2 = self.mat_dict['isot_n2']
        mpl_fig = plot_isotherm(isot_co2=isot_co2, isot_n2=isot_n2)
        column = pn.Column(get_title("Isotherms for " + self.mat_id, uuid=isot_co2.uuid))
        column.append(pn.pane.Bokeh(mpl_fig))
        return column

    def process(self):
        from detail.process import print_process
        process_node = self.mat_dict['appl_pecoal']
        column = pn.Column(get_title("Process sketch for " + self.mat_id, uuid=process_node.uuid))
        column.append(pn.pane.PNG('detail/process.png', width=800))
        column.append(pn.pane.Markdown(print_process(process_node)))
        return column


pn.extension()
explorer = DetailView()

tabs = pn.Tabs()
tabs.extend([
    ("Workflow's graph", explorer.graph()),
    ('DFT-optimization', explorer.dft_plot()),
    ('Isotherms', explorer.iso_plot()),
    ('CCS process', explorer.process()),
])

tabs.servable()
