# -*- coding: utf-8 -*-
# pylint: disable=unsubscriptable-object, too-many-locals

def structure_jsmol(cif_str):
    from jsmol_bokeh_extension import JSMol
    import bokeh.models as bmd

    script_source = bmd.ColumnDataSource()

    info = dict(
        height="100%",
        width="100%",
        use="HTML5",
        serverURL="https://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
        j2sPath="https://chemapps.stolaf.edu/jmol/jsmol/j2s",
        #serverURL="https://www.materialscloud.org/discover/scripts/external/jsmol/php/jsmol.php",
        #j2sPath="https://www.materialscloud.org/discover/scripts/external/jsmol/j2s",
        #serverURL="detail/static/jsmol/php/jsmol.php",
        #j2sPath="detail/static/jsmol/j2s",
        script="""set antialiasDisplay ON;
    load data "cifstring"
    {}
    end "cifstring"
    """.format(cif_str)
        ## Note: Need PHP server for approach below to work
        #    script="""set antialiasDisplay ON;
        #load cif::{};
        #""".format(get_cif_url(entry.filename))
    )

    applet = JSMol(
        width=600,
        height=600,
        script_source=script_source,
        info=info,
        #js_url="detail/static/jsmol/JSmol.min.js",
    )

    return applet