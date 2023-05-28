# -*- coding: utf-8 -*-
"""
This script adds the parametrization of water flows and bounds. The input data
should be provided through an Excel file (no hardcoded data here in python)

"""
import pandas as pd
import os
from itertools import product
path_files = (r'C:\Users\Natalia\GitKraken\Brazil\Brazilian Electrical system models')

os.chdir(path_files)


# A function for adding water supply technologies
def add_water(sc, setup_file):

    # 1) Loading data from Excel
    xls = pd.ExcelFile(setup_file)
    setup = xls.parse('water')
    demand = xls.parse('water_demand').set_index('time')
    inflow = xls.parse('water_inflow').set_index('time')
    setup = setup.loc[setup['active'] == 'yes']
    setup = setup.set_index('technology')

    # 2) Adding required sets for water technologies
    sc.check_out()
    model_yrs = [int(x) for x in sc.set('year') if int(x) >= sc.firstmodelyear]
    
    # Water technologies
    water_tecs = list(set(setup.index))
    sc.add_set('technology', water_tecs)
    
    # Water levels
    water_lvls = list(set(setup['output_level'].dropna())
                      ) + list(set(setup['input_level'].dropna()))
    sc.add_set('level', water_lvls)
    
    # Water commodities
    water_coms = list(set(setup['output_commodity'].dropna())
                      ) + list(set(setup['input_commodity'].dropna()))
    sc.add_set('commodity', water_coms)

    # 2) Adding required parameters for water technologies
    for tec in water_tecs:
        node_locs = setup.loc[tec, 'node_loc'].split("/")
        node_dests = setup.loc[tec, 'node_dest'].split("/")

        # adding parameter output
        tec_from = setup.loc[tec, 'tec_from']
        for node1, node2 in zip(node_locs, node_dests):
            df = sc.par('output', {'technology': tec_from, 'node_loc': node1})
            df_new = df.copy()
            df_new['technology'] = tec
            df_new['commodity'] = setup.loc[tec, 'output_commodity']
            df_new['node_dest'] = node2
            df_new['value'] = 1
            df_new['level'] = setup.loc[tec, 'output_level']
            sc.add_par('output', df_new)

        # adding parameter input
        if not pd.isna(setup.loc[tec, 'input_level']):
            node_orgs = setup.loc[tec, 'node_origin'].split(",")
            for node1, node2 in zip(node_locs, node_orgs):
                df = sc.par('input', {'technology': tec_from,
                                      'node_loc': node1})
                df_new = df.copy()
                df_new['technology'] = tec
                df_new['commodity'] = setup.loc[tec, 'input_commodity']
                df_new['node_origin'] = node2
                df_new['value'] = 1
                df_new['level'] = setup.loc[tec, 'input_level']
                sc.add_par('input', df_new)
                
        print('- Parameters "input" and "output" configured for "{}".'.format(
            tec))

        # Adding upper bound on inflow (to limit inflow in some time slices)
        parname = 'bound_activity_up'
        times = inflow.index.tolist()
        cols = sc.idx_names(parname) + ['unit', 'value']
        df_up = pd.DataFrame(index=product(model_yrs, times),
                             columns=cols)

        for node in node_locs:
            if node + ',' + tec in inflow.columns:
                bounds = inflow[node + ',' + tec]
                df_up['technology'] = tec
                df_up['node_loc'] = node
                df_up['mode'] = df_new['mode'][0]
                df_up['year_act'] = [i[0] for i in df_up.index]
                df_up['time'] = [i[1] for i in df_up.index]
                df_up['unit'] = 'm^3/a' #changed the unit
                for ti in times:
                    up = bounds[ti]
                    slicer = [x for x in df_up.index if x[1] == ti]
                    df_up.loc[slicer, 'value'] = up

                sc.add_par(parname, df_up.reset_index(drop=True))
                
            print('- Water inflow for "{}" configured.'.format(tec))

        # Adding water demand
        coms = [x for x in sc.set('commodity') if 'water' in x] #alterei commodity
        if setup.loc[tec, 'demand_level'] == 'yes':
            for node in node_dests:
                df_dem = sc.par('demand', {'node': node,
                                           'commodity': coms})
                df_dem['commodity'] = setup.loc[tec, 'output_commodity']
                df_dem['level'] = setup.loc[tec, 'output_level']
                df_dem = df_dem.set_index('time')
                dem = demand[node + ',' + setup.loc[tec, 'output_commodity']] 
                for ti in times:
                    df_dem.loc[str(ti), 'value'] = dem[ti]

                df_dem = df_dem.reset_index().dropna()
                sc.add_par('demand', df_dem)
            print('- Water demand for "{}" configured.'.format(tec))

    sc.commit('')
    print('**** Water parameterization done successfully. *****')
    return water_tecs


# Correcting the ratio of water inflow to hydropower electricity output
def water_flow_ratio(sc, tecs=[], multiplier=1, only_demand=False): #changed here it was 1/900
    # Changing the mass flow of water based on electricity output
    # Assuming 900 m3/s =~ 1 GW capacity)
    sc.check_out()

    if not only_demand and tecs:
    # Fetching technologies of water inflow
        df = sc.par('bound_activity_up', {'technology': tecs})
        df['value'] *= multiplier
        sc.add_par('bound_activity_up', df)

    # Water demand flow
    coms = [x for x in sc.set('commodity') if 'water' in x]
    df = sc.par('demand', {'commodity': coms})
    df['value'] *= multiplier
    sc.add_par('demand', df)
    sc.commit('')


# Adding mapping sets of new parameters
def mapping_sets(sc, par_list=['relation_lower_time', 'relation_upper_time']):
    sc.check_out()
    for parname in par_list:
        setname = 'is_' + parname

        # initiating the sets
        idx_s = sc.idx_sets(parname)
        idx_n = sc.idx_names(parname)
        try:
            sc.set(setname)
        except:
            sc.init_set(setname, idx_sets=idx_s, idx_names=idx_n)
            print('- Set {} was initiated.'.format(setname))

        # emptying old data in sets
        df = sc.set(setname)
        sc.remove_set(setname, df)

        # adding data to the mapping sets
        df = sc.par(parname)
        if not df.empty:
            for i in df.index:
                d = df.loc[i, :].copy().drop(['value', 'unit'])
                sc.add_set(setname, d)

            print('- Mapping sets updated for "{}"'.format(setname))
    sc.commit('')

# %% Sample input data
if __name__  == '__main__':
    import message_ix
    import ixmp as ix
    from timeit import default_timer as timer
    from datetime import datetime

    mp = ix.Platform("default", jvmargs=["-Xms800m", "-Xmx8g"])


    model = 'MESSAGEix-BR'
    scen_ref = 'seasonality'
    version_ref = None

    filename = '3_water_scheme_new.xlsx'  # Name of the input Excel file
    
    water_com = ['water_1', 'water_2', 'water_3', 'water_4',
                 'water_5', 'water_6', 'water_7', 'water_8',
                 'water_9', 'water_10', 'water_11', 'water_12']  # water commodity (if to be excluded from solution)
    
    flow_correction = 1#/1000  # to correct water flow (m3/2) for each GW power
    solve = True         # if True, solving scenario at the end


    sc_ref = message_ix.Scenario(mp, model, scen_ref, version_ref)

    start = timer()
    sc = sc_ref.clone(model, 'water', keep_solution=False)

    #sc.check_out() #alterei aqui    
    setup_file = path_files + '\\' + filename

    # Adding water data
    water_tecs = add_water(sc, setup_file)

    # Correcting the ratio of water inflow to hydropower electricity output,
    # After importing from Excel
    if flow_correction:
        # Correcting flow for demand and for specific technologies (tecs)
        water_flow_ratio(sc, ['river1', 'river2', 'river3', 
                              'river4', 'river5', 'river6', 'river7',
                              'river8', 'river9', 'river10', 'river11', 'river12'], flow_correction)

    
    #sc.commit('')
    # Adding mapping sets of relations in time parameters
    mapping_sets(sc)

    end = timer()
    print('Elapsed time for adding storage and water setup:',
          int((end - start)/60),
          'min and', round((end - start) % 60, 2), 'sec.')

    # Solving the model
    if solve:
        case = sc.model + '__' + sc.scenario + '__v' + str(sc.version)
        print('Solving scenario "{}" in "{}" mode, started at {}, please wait.'
              '..!'.format(case, 'MESSAGE', datetime.now().strftime('%H:%M:%S')))
        start = timer()

        sc.solve(case=case)
        sc.set_as_default()
        # sc.to_excel('BES_water_05.01.xlsx')

        #sc.to_excel('3.BES_water_tecs.xlsx')
        end = timer()
        print('Elapsed time for solving scenario:', int((end - start)/60),
              'min and', round((end - start) % 60, 2), 'sec.')
        
# %% Plotting Results

#import pyam
from ixmp.reporting import configure
import pyam
from message_ix.reporting import Reporter
#import os
import matplotlib.pyplot as plt
configure(units={'replace': {'-': 'GWa'}})

rep = Reporter.from_scenario(sc)

# plotting years
plotyrs = [x for x in set(sc.set('year')) if x >= sc.firstmodelyear]

rep.set_filters(c = 'electricity')
elec = rep.full_key('out')
elec = elec.drop('yv','m','nd','hd','h')
elec_gen = rep.get(elec)
elec_gen


def collapse_callback(df):
    """Callback function to populate the IAMC 'variable' column."""
    df['variable'] = 'Electricity Generation|' + df['l']+ '|'+df['t']
    return df.drop(['t','l'], axis =1)

    
new_key = rep.convert_pyam(quantities=elec.drop('h', 'hd', 'm', 'nd', 'yv'),
                           rename=dict(nl="region", ya="year"),
                           collapse=collapse_callback)
    

    
df_elec = rep.get(new_key)
df_elec.data.unit = 'GWa'
df_elec.to_csv('electricity_bra.csv')

import pandas as pd
elec_gen = pd.read_csv("electricity_bra.csv")
elec_gen.columns 

elec_gen = pyam.IamDataFrame(data='electricity_bra.csv')

elec = elec_gen.filter(region=['North'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
plt.ylabel("GWa")

elec = elec_gen.filter(region=['Northeast'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
plt.ylabel("GWa")

elec = elec_gen.filter(region=['Southeast'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
plt.ylabel("GWa")

elec = elec_gen.filter(region=['South'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
plt.ylabel("GWa")


mp.close_db()
