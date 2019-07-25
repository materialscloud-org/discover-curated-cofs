""" Plots the process details
"""

def print_process(process_node):
    process_dict = process_node.get_dict()
    process_text = '''
### Minimal parasitic energy (PE): %.3f %s \
<br> Effective energy for the separation (Q<sup>eff</sup><sub>TOT</sub>): %.3f %s \
<br> Energy for the compression (W<sub>COMP</sub>): %.3f %s

### Desorption temperature (T<sub>d</sub>): %.3f %s \
<br> Desorption pressure (P<sub>d</sub>): %.3f %s \
<br> Final CO<sub>2</sub> concentration: %.3f %s

### Volumetric working capacity: %.3f %s \
<br> Gravimetric working capacity: %.3f %s
''' %(process_dict['PE'],
      process_dict['PE_units'],
      process_dict['Wcomp'],
      process_dict['Wcomp_units'],
      process_dict['Qt'],
      process_dict['Qt_units'],
      process_dict['Td'],
      process_dict['Td_units'],
      process_dict['Pd'],
      process_dict['Pd_units'],
      process_dict['Pur'],
      process_dict['Pur_units'],
      process_dict['WCv'],
      process_dict['WCv_units'],
      process_dict['WCg'],
      process_dict['WCg_units'],
    )
    return process_text
