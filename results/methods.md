
In the "details" page of each material, each result is associated to an AiiDA logo
which links to Explore page of the AiiDA Node containing the value(s).
In the Explore page, one can navigate back to the calculation that produced this results,
and back again to its input and the provenance of the inputs.
When a `CalcJob` is submitted to an external code, all the inputs and outputs are stored in the format required by
the software. See for example:
* a Zeo++ calculation: [CalcJobNode](http://hub.matscreen.com/explore/ownrestapi/details/38fe6ee0-8ecc-4675-8f08-faca0b9cbe6e?nodeType=NODE&base_url=http:~2F~2Fhub.matscreen.com~2Frest~2Fapi~2Fv4)
* a CP2K calculation: [CalcJobNode](http://hub.matscreen.com/explore/ownrestapi/details/b6c76734-1ae7-451f-b68d-7216821daa2d?nodeType=NODE&base_url=http:~2F~2Fhub.matscreen.com~2Frest~2Fapi~2Fv4)
* a Chargemol (DDEC) calculation: [CalcJobNode](http://hub.matscreen.com/explore/ownrestapi/details/6c4cb9d9-367d-4c02-8658-5e5d2f1ff9b6?nodeType=NODE&base_url=http:~2F~2Fhub.matscreen.com~2Frest~2Fapi~2Fv4)
* a RASPA calculation: [CalcJobNode](http://hub.matscreen.com/explore/ownrestapi/details/ea743954-3892-468f-bfec-f17c03b1df4a?nodeType=NODE&base_url=http:~2F~2Fhub.matscreen.com~2Frest~2Fapi~2Fv4)


For all Metal-Organic Frameworks (MOFs) and Covalent Organic Frameworks (COFs),
a similar workflow is applied, with minor differences due to improvements in the newer versions of the protocol.
The original protocol was described in [Ongari2019](https://doi.org/10.1021/acscentsci.9b00619),
using the [Multistage work chain](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#multistage-work-chain)
for the DFT optimization, the [DDEC plugin](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#cp2kmultistageddec-work-chain)
to compute the partial charges of the frameworks,
the [Isotherm work chain](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#isotherm-work-chain)
to compute single-molecule adsorption isotherms,
and finally the [`calc_pe`](https://github.com/danieleongari/calc_pe) utility to compute the CO2 parasitic energy.
For other applications, the optimized structures with DDEC charges were submitted to the `Isotherm work chain`  
(or [`IsothermMultiTemp work chain`](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#isothermmultitemp-work-chain))
for the gas molecules of interest, and post processed to compute the [working capacity](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#working-capacity-calculators) 
or the [selectivity](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#selectivity-calculators), 
depending on the application.

The following force field parameters, mixed according to the [Lorentz-Bertherlot rules](https://en.wikipedia.org/wiki/Combining_rules#Lorentz-Berthelot_rules), are used:

* CO2: TraPPE & UFF
* N2: TraPPE & UFF
* H2: Buch & UFF
* CH4: TraPPE & UFF
* O2: TraPPE & UFF
* Kr: BOATO & UFF
* Xe: BOATO & UFF
* H2S: ESP-MM & UFF
* H2O: TIP4P/2005 & UFF

Note that for the most recent calculations, the [`Force Field Builder`](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#force-field-builder) was employed to store and retrieve the parameters.
The available force fields are stored in [this file](https://github.com/lsmo-epfl/aiida-lsmo/blob/master/aiida_lsmo/calcfunctions/ff_data.yaml), together with their references, to be parsed by the `Force Field Builder` utility.
