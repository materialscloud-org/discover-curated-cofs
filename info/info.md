# Info & Methods

In the "details" page of a material you can find a small AiiDA logo close to every result:
this links to the Explore page of the AiiDA Node where that value is contained.
In the Explore page, one can navigate back to the calculation that produced the result,
and go back again to browse its inputs and their provenance.

Indeed, when a CalcJob is submitted to an external code, all the inputs and outputs are stored in the format required 
or printed by the software. See for example:

* a Zeo++ calculation: 
[CalcJobNode](https://dev-www.materialscloud.org/explore/curated-cofs/details/f155fce9-684c-402a-a397-85eaa7d32311?nodeType=NODE)
* a CP2K calculation: 
[CalcJobNode](https://dev-www.materialscloud.org/explore/curated-cofs/details/c7b8f809-12a3-449e-afed-b580299c7b2c?nodeType=NODE)
* a Chargemol (DDEC) calculation: 
[CalcJobNode](https://dev-www.materialscloud.org/explore/curated-cofs/details/dc3f6c31-f588-4904-9ce9-7e9df2662e1d?nodeType=NODE)
* a RASPA calculation: 
[CalcJobNode](https://dev-www.materialscloud.org/explore/curated-cofs/details/0ba4bc65-7847-4393-8edc-a8e335bf2189?nodeType=NODE)


For all Covalent Organic Frameworks (COFs) a similar workflow is applied, 
with possible minor differences due to improvements in the newer versions of the protocol.
The protocol and settings are described in [Ongari2019](https://doi.org/10.1021/acscentsci.9b00619),
using the [Multistage work chain](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#multistage-work-chain)
for the DFT optimization, the [DDEC plugin](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#cp2kmultistageddec-work-chain)
to compute the partial charges of the frameworks,
the [Isotherm work chain](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#isotherm-work-chain)
to compute single-molecule adsorption isotherms,
and finally the [calc_pe](https://github.com/danieleongari/calc_pe) code to compute the CO2 parasitic energy.

For other applications, the optimized structures with DDEC charges were submitted to the Isotherm work chain
(or [IsothermMultiTemp work chain](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#isothermmultitemp-work-chain))
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

Note that for the most recent calculations, the [Force Field Builder](https://aiida-lsmo.readthedocs.io/en/latest/workflows.html#force-field-builder) was employed to store and retrieve the parameters.
The available force fields are stored in [this file](https://github.com/lsmo-epfl/aiida-lsmo/blob/master/aiida_lsmo/calcfunctions/ff_data.yaml), together with their references, to be parsed by the Force Field Builder utility.
