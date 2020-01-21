from aiida import load_profile
import panel as pn
from detail.query import get_group_as_dict
from bokeh.io import curdoc
import os

load_profile()


def get_label():
    """Get structure label from URL parameter 'id'"""
    try:
        name = curdoc().session_context.request.arguments.get('id')[0]
        if isinstance(name, bytes):
            structure_label = name.decode()
    except (TypeError, KeyError, AttributeError):
        #structure_label = '05001N2' # example v1
        structure_label = '19353N2'  # example v2

    return structure_label


def provenance_link(uuid, label=None):
    """Return pn.HTML representation of provenance link."""

    if label is None:
        label = "Browse provenance\n" + uuid

    logo_url = "https://www.materialscloud.org/discover/images/ceede967.aiida-logo-128.png"
    explore_url = os.getenv(
        'EXPLORE_URL',
        "https://dev-www.materialscloud.org/explore/curated-cofs")
    return pn.pane.HTML(
        "<a href='{url}/details/{uuid}' target='_blank'><img src={logo_url} title='{label}' style='width: 20px;  height: auto;'></a>"
        .format(url=explore_url, uuid=uuid, label=label, logo_url=logo_url),
        align='center')


def get_title(text, uuid=None):
    """Return pn.Row representation of title.
    
    Includes provenance link, if uuid is specified.
    """
    title = pn.Row(pn.pane.Markdown('#### ' + text), align='center')

    if uuid is not None:
        title.append(provenance_link(uuid))

    return title


class PlainSVG(pn.pane.SVG):
    """Drop-in replacement for pn.pane.SVG that outputs plain SVG (not base64-encoded).
    
    Note: links encoded with xlink:href are not displayed in base64-encoded SVGs.
    """

    def _get_properties(self):
        p = super(PlainSVG, self)._get_properties()
        data = self._img()

        if self.object is None:
            return dict(p, text='<img></img>')
        return dict(p, text=data)


pn.extension()


# pylint: disable=import-outside-toplevel
class DetailView():
    def __init__(self):
        self.cof_label = get_label()  # get CURATED-COF-ID
        self.group_dict = get_group_as_dict(
            self.cof_label)  # get linking group

    def iso_plot(self):
        from detail.plot_isotherm import plot_isotherm
        pm_co2 = self.group_dict['isot_co2_out']
        pm_n2 = self.group_dict['isot_n2_out']
        mpl_fig = plot_isotherm(pm_co2=pm_co2,
                                pm_n2=pm_n2,
                                label=self.cof_label,
                                version=self.group_dict['version'])
        column = pn.Column(
            get_title("Isotherms for " + self.cof_label, uuid=pm_co2.uuid))
        column.append(pn.pane.Bokeh(mpl_fig))
        return column

    def ener_plot(self):
        from detail.plot_cp2k import plot_energy_steps
        dftopt_node = self.group_dict[
            'dftopt_out']  #Singlefile (v1) or Dict (v2)
        column = pn.Column(
            get_title("Robust cell optimization of " + self.cof_label,
                      uuid=dftopt_node.uuid))
        column.append(
            pn.pane.Bokeh(
                plot_energy_steps(dftopt_node, self.cof_label,
                                  self.group_dict['version'])))
        return column

    def structure_opt(self):
        from detail.structure import structure_jsmol
        cif_node = self.group_dict['opt_cif_ddec']
        column = pn.Column(
            get_title("DFT-optimized structure for " + self.cof_label,
                      uuid=cif_node.uuid))
        column.append(
            pn.pane.Bokeh(structure_jsmol(cif_str=cif_node.get_content())))
        return column

    def process(self):
        from detail.process import print_process
        process_node = self.group_dict['pe_out']
        column = pn.Column(
            get_title("Process sketch for " + self.cof_label,
                      uuid=process_node.uuid))
        column.append(pn.pane.PNG('detail/process.png', width=800))
        column.append(pn.pane.Markdown(print_process(process_node)))
        return column

    def graph(self):
        from detail.graph import get_graph
        column = pn.Column(
            PlainSVG(get_graph(self.group_dict['group'], self.group_dict)))
        column.append("CURATED-COF {}, version: {}".format(
            self.group_dict['cof_label'], self.group_dict['version']))
        return column


explorer = DetailView()

tabs = pn.Tabs()
tabs.extend([
    ("Workflow's graph", explorer.graph()),
    ('DFT-optimization energy', explorer.ener_plot()),
    ('DFT-optimized structure', explorer.structure_opt()),
    ('Isotherms', explorer.iso_plot()),
    ('CCS process', explorer.process()),
])

tabs.servable()
