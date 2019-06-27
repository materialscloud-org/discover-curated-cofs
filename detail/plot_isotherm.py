from __future__ import print_function
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

def plot_isotherm(**kwargs):

    #plot figure
    pmax=30
    plotcolor={'co2':'red','n2':'blue'}
    plotlabel={'co2':'CO$_2$','n2':'N$_2$'}
    structure_label = kwargs['label']
    fig, ax = plt.subplots(figsize=[7, 4.5],
                           nrows=1,
                           ncols=2,
                           sharey=True,
                           gridspec_kw={"width_ratios":[1.2,0.8],
                                "wspace":0.0})
    #fig.suptitle('Isotherms for: '+ structure_label)
    ax[0].set(xlabel='Pressure (bar)',
              ylabel='Uptake (mol/kg)')
    ax[1].set(xlabel='Heat of adsorption (kJ/mol)')
    porous = False

    for gas in ['co2','n2']:
        pe_res = kwargs['pm_'+ gas].get_dict()
        if 'henry_coefficient_average' in pe_res.keys(): #porous
            # parse isotherm for plotting
            p = [a[0] for a in pe_res['isotherm_loading']] #(bar)
            q_avg = [a[1] for a in pe_res['isotherm_loading']] #(mol/kg)
            q_dev = [a[2] for a in pe_res['isotherm_loading']] #(mol/kg)
            h_avg = [a[1] for a in pe_res['isotherm_enthalpy']] #(kJ/mol)
            h_dev = [a[2] for a in pe_res['isotherm_enthalpy']] #(kJ/mol)
            # TRICK: use the enthalpy from widom (energy-RT) which is more accurate that the one at 0.001 bar (and which also is NaN for weakly interacting systems)
            h_avg[0] = pe_res['adsorption_energy_average']-pe_res['temperature']/120.027
            h_dev[0] = pe_res['adsorption_energy_dev']
        else: #non porous
            kh = 0.0
            khdev = 0.0
            p = [0, pmax]
            q_avg = [0, 0]
            q_dev = [0, 0]
            h_avg = [0, 0]
            h_dev = [0, 0]
        # Plot isotherm
        ax[0].errorbar(p, q_avg, yerr=q_dev,
                       marker ="o",
                       color= plotcolor[gas],
                       label=plotlabel[gas])
        ax[1].errorbar(h_avg, q_avg, xerr=h_dev,
                       marker ="o",
                       color= plotcolor[gas],)
        ax[0].legend(loc='upper left')
        ax[0].set_xlim([-1,pmax+1])
        ax[0].set_ylim([-1,41])
        ax[1].set_xlim([-51,0+1])
        #fig.savefig(dir_out+"/"+structure_label+".png",dpi=300,bbox_inches='tight')
    # plt.show()
    return fig
