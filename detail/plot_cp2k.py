import pandas as pd

from detail.query import get_data_aiida

def get_startindex(l):
    '''Take a list of steps and decide starting indices (and final number of steps).'''
    start_indices=[]
    for i in range(len(l)):
        if i==0:
            start_indices.append(0)
        else:
            if l[i]<=l[i-1]:
                start_indices.append(i)
    start_indices.append(len(l))
    return start_indices

def plot_energy_steps(stepsfile, structure_label):
    """Plot the total energy graph."""
    df = pd.read_csv(stepsfile,sep=' ')

    steps = df['#step'].tolist()
    energy = df['energy(eV/atom)'].tolist()

    # Take min and max, neglecting spikes
    min_energy = +9999.
    max_energy = -9999.
    spike_thr = 2. #Ha
    for i in range(len(energy)):
        if i==0 or i==len(energy)-1 or \
           abs(energy[i]-energy[i-1])+abs(energy[i]-energy[i+1]) < spike_thr:
           if energy[i]<min_energy:
               min_energy = energy[i]
           if energy[i]>max_energy:
               max_energy = energy[i]

    energy_shifted= [ (x-min_energy) for x in energy ]

    from bokeh.plotting import figure, show, output_notebook
    import bokeh.models as bmd

    tooltips = [
        ("Step", "@index"),
        ("Energy", "@energy eV/atom"),
    ]
    hover = bmd.HoverTool(tooltips=tooltips)
    TOOLS = ["pan", "wheel_zoom", "box_zoom", "reset", "save", hover]

    data = bmd.ColumnDataSource(data=dict( energy=energy_shifted, index=range(len(energy_shifted)) ) )

    p = figure(tools=TOOLS, #title='Robust cell optimization of: '+ structure_label,
            height=350, width=550)
    p.xaxis.axis_label = 'Steps'
    p.yaxis.axis_label = 'Energy (ev/atom)'

    startindex=get_startindex(steps)
    startindex = [s-1 for s in startindex]
    if len(startindex) > 2: #Print only Stage1_CellOpt
        p.add_layout(bmd.BoxAnnotation(left=startindex[1], right=startindex[2], fill_alpha=0.2, fill_color='red'))
    if len(startindex) > 3: #Print also Stage2_MD
        p.add_layout(bmd.BoxAnnotation(left=startindex[2], right=startindex[3], fill_alpha=0.2, fill_color='orange'))
    if len(startindex) > 4: #Print also Stage3_CellOpt
        p.add_layout(bmd.BoxAnnotation(left=startindex[3], right=startindex[4], fill_alpha=0.2, fill_color='green'))
    #print energy profile
    p.line('index', 'energy', source=data, line_color='blue')
    p.circle('index', 'energy', source=data, line_color='blue', size=3)

    #output_notebook()
    #show(p)

    return p