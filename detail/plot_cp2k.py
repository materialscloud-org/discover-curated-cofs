import pandas as pd


def get_startindex(l):
    '''Take a list of steps and decide starting indices (and final number of steps).'''
    start_indices = []
    for i in range(len(l)):
        if i == 0:
            start_indices.append(0)
        else:
            if l[i] <= l[i - 1]:
                start_indices.append(i)
    start_indices.append(len(l))
    return start_indices


def plot_energy_steps(dftopt_out, structure_label, version):
    """Plot the total energy graph."""
    from bokeh.plotting import figure, show, output_notebook
    import bokeh.models as bmd

    if version == 1:  # dftopt_out is a SinglefileData
        with dftopt_out.open() as f:
            df = pd.read_csv(f, sep=' ')

        steps = df['#step'].tolist()
        energy = df['energy(eV/atom)'].tolist()

        # Take min and max, neglecting spikes
        min_energy = +9999.
        max_energy = -9999.
        spike_thr = 2.  #Ha
        for i in range(len(energy)):
            if i==0 or i==len(energy)-1 or \
               abs(energy[i]-energy[i-1])+abs(energy[i]-energy[i+1]) < spike_thr:
                if energy[i] < min_energy:
                    min_energy = energy[i]
                if energy[i] > max_energy:
                    max_energy = energy[i]

        energy_shifted = [(x - min_energy) for x in energy]

        tooltips = [
            ("Step", "@index"),
            ("Energy", "@energy eV/atom"),
        ]
        hover = bmd.HoverTool(tooltips=tooltips)
        TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

        data = bmd.ColumnDataSource(data=dict(energy=energy_shifted, index=range(len(energy_shifted))))

        p = figure(
            tools=TOOLS,  #title='Robust cell optimization of: '+ structure_label,
            height=350,
            width=550)
        p.xaxis.axis_label = 'Steps'
        p.yaxis.axis_label = 'Energy (ev/atom)'

        startindex = get_startindex(steps)
        startindex = [s - 1 for s in startindex]
        if len(startindex) > 2:  #Print only Stage1_CellOpt
            p.add_layout(bmd.BoxAnnotation(left=startindex[1], right=startindex[2], fill_alpha=0.2, fill_color='red'))
        if len(startindex) > 3:  #Print also Stage2_MD
            p.add_layout(bmd.BoxAnnotation(left=startindex[2], right=startindex[3], fill_alpha=0.2,
                                           fill_color='orange'))
        if len(startindex) > 4:  #Print also Stage3_CellOpt
            p.add_layout(bmd.BoxAnnotation(left=startindex[3], right=startindex[4], fill_alpha=0.2, fill_color='green'))
        #print energy profile
        p.line('index', 'energy', source=data, line_color='blue')
        p.circle('index', 'energy', source=data, line_color='blue', size=3)

    if version >= 2:  # dftopt_out is a Dict
        units = 'eV'
        ha2u = {'eV': 27.211399}

        out_dict = dftopt_out.get_dict()

        tooltips = [("Step (total)", "@index"), ("Step (stage)", "@step"), ("Energy", "@energy eV/atom"),
                    ("Energy (dispersion)", "@dispersion_energy_au Ha"), ("SCF converged", "@scf_converged"),
                    ("Cell A", "@cell_a_angs Angs"), ("Cell Vol", "@cell_vol_angs3 Angs^3"),
                    ("MAX Step", "@max_step_au Bohr"), ("Pressure", "@pressure_bar bar")]
        hover = bmd.HoverTool(tooltips=tooltips)
        TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

        natoms = out_dict['natoms']
        values = [x / natoms * ha2u[units] for x in out_dict['step_info']['energy_au']]
        values = [x - min(values) for x in values]

        data = bmd.ColumnDataSource(data=dict(
            index=range(len(values)),
            step=out_dict['step_info']['step'],
            energy=values,
            dispersion_energy_au=out_dict['step_info']['dispersion_energy_au'],
            scf_converged=out_dict['step_info']['scf_converged'],
            cell_a_angs=out_dict['step_info']['cell_a_angs'],
            cell_vol_angs3=out_dict['step_info']['cell_vol_angs3'],
            max_step_au=out_dict['step_info']['max_step_au'],
            pressure_bar=out_dict['step_info']['pressure_bar'],
        ))

        p = figure(tools=TOOLS, title='Energy profile of the DFT minimization', height=350, width=550)

        p.xgrid.grid_line_color = None
        p.xaxis.axis_label = 'Steps'
        p.yaxis.axis_label = 'Energy ({}/atom)'.format(units)

        # Colored background
        colors = ['red', 'orange', 'green', 'yellow', 'cyan', 'pink', 'palegreen']
        start = 0
        for i, steps in enumerate(out_dict['stage_info']['nsteps']):
            end = start + steps
            p.add_layout(bmd.BoxAnnotation(left=start, right=end, fill_alpha=0.2, fill_color=colors[i]))
            start = end

        # Trace line and markers
        p.line('index', 'energy', source=data, line_color='blue')
        p.circle('index', 'energy', source=data, line_color='blue', size=3)

    return p
