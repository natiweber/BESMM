
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 09:59:13 2021

@author: Natalia
"""

import pandas as pd
import ixmp as ix
import message_ix
import itertools
from message_ix.utils import make_df
from matplotlib import pyplot as plt

# Loading modelling platform
mp = ix.Platform("default", jvmargs=["-Xms800m", "-Xmx8g"])

# %% Specifying model/scenario to be loaded from the database
model = 'MESSAGEix-BR'
scenario='baseline'
nodes = ['South', 'North', 'Northeast', 'Southeast']
base = message_ix.Scenario(mp, model, scenario= scenario)

#df = mp.scenario_list(default=False)
#df.loc[df['scenario']=='baseline']

#df = mp.scenario_list(default=False)
#df.loc[df['scenario']=='brazil_seasonal']

# Cloning a scenario for adding time steps
scen = base.clone(model, 'seasonality', keep_solution=False)
scen.check_out()

# Adding sub-annual time steps
time_steps = ['summer','autumn','winter', 'spring']
scen.add_set('time', time_steps)

# We can see the elements of the set
scen.set('time')

# Defining a new temporal level
time_level = 'season'
scen.add_set('lvl_temporal', time_level)

# Adding temporal hierarchy
for t in time_steps:
    scen.add_set('map_temporal_hierarchy', [time_level, t, 'year'])
    
# We can see the content of the set
scen.set('map_temporal_hierarchy')

# All parameters with at least one sub-annual time index
parameters = [p for p in scen.par_list() if 'time' in scen.idx_sets(p)]

# Those parameters with "time" index that are not empty in our model
[p for p in parameters if not scen.par(p).empty]

# Adding duration time
for t in time_steps:
    scen.add_par('duration_time', [t], 0.25, '-')
    
# A function for adding sub-annual data to a parameter
def yearly_to_season(scen, parameter, data, filters=None):
    if filters:
        old = scen.par(parameter, filters)
    else:
        old = scen.par(parameter)
    scen.remove_par(parameter, old)
    
    # Finding "time" related indexes
    time_idx = [x for x in scen.idx_names(parameter) if 'time' in x]
    for h in data.keys():
        new = old.copy()
        for time in time_idx:
            new[time] = h
        new['value'] = data[h] * old['value']
        scen.add_par(parameter, new)

# Before modifying, let's look at "demand" in baseline
scen.par('demand')

# Modifying demand for each season
demand_data = {'summer': 0.26, 'autumn': 0.253,'winter':0.237, 'spring':0.25}
yearly_to_season(scen, 'demand', demand_data)

# let's look at "demand" now
scen.par('demand')

# Modifying input and output parameters for each season
# output
fixed_data = {'summer': 1, 'autumn': 1,'winter':1, 'spring':1}
yearly_to_season(scen, 'output', fixed_data)

# input
yearly_to_season(scen, 'input', fixed_data)

# Modifying growth rates for each season
yearly_to_season(scen, 'growth_activity_lo', fixed_data)
yearly_to_season(scen, 'growth_activity_up', fixed_data)
yearly_to_season(scen, 'growth_new_capacity_lo', fixed_data)
yearly_to_season(scen, 'growth_new_capacity_up', fixed_data)

# Modifying capacity factor
# Let's get the yearly capacity factor of wind in the baseline scenario
cf_wind_on = scen.par('capacity_factor', {'technology': 'wind_ppl_on'})['value'].mean()
# Converting yearly capacity factor to seasonal
fixed_data = {'summer': 1, 'autumn': 1,'winter': 1, 'spring': 1}
cf_filters = {'technology': 'wind_ppl_on' }
yearly_to_season(scen, 'capacity_factor', fixed_data)

cf_wind_off = scen.par('capacity_factor', {'technology': 'wind_ppl_off'})['value'].mean()
# Converting yearly capacity factor to seasonal
fixed_data = {'summer': 1, 'autumn': 1,'winter': 1, 'spring': 1}
cf_filters = {'technology': 'wind_ppl_off' }
yearly_to_season(scen, 'capacity_factor', fixed_data)


cf_solar = scen.par('capacity_factor', {'technology': 'solar_pv_ppl'})['value'].mean()
 #Converting yearly capacity factor to seasonal
fixed_data = {'summer': 1, 'autumn': 1,'winter': 1, 'spring': 1}
cf_filters = {'technology': 'solar_pv_ppl'}
yearly_to_season(scen, 'capacity_factor', fixed_data)

cf_bio = scen.par('capacity_factor', {'technology': 'bio_ppl'})['value'].mean()
# Converting yearly capacity factor to seasonal
fixed_data = {'summer': 1, 'autumn': 1,'winter': 1, 'spring': 1}
cf_filters = {'technology': 'bio_ppl'}
yearly_to_season(scen, 'capacity_factor', fixed_data)


cf_filters = {'technology': ['nuc_ppl', 'gas_ppl', 'coal_ppl' ]}
yearly_to_season(scen, 'capacity_factor', fixed_data)

# Let's look at capacity factor in year 2100
scen.par('capacity_factor', {'year_act':2100, 'year_vtg':2100})

# Modifying historical activity 
hist_data = {'summer': 1, 'autumn': 1,'winter':1, 'spring':1}
yearly_to_season(scen, 'historical_activity', hist_data)

# Modifying variable cost
yearly_to_season(scen, 'var_cost', fixed_data)

scen.commit(comment='introducing seasonality')
scen.solve()
scen.set_as_default()



scen.var('OBJ')['lvl']
#scen.to_excel('BES_seasonal.xlsx')
scen.version

### Postprocessing and analyzing results
### Plotting results

# import pyam
# from ixmp.reporting import configure
# from message_ix.reporting import Reporter
# import os
# import matplotlib.pyplot as plt
# configure(units={'replace': {'-': 'GWa'}})

# rep = Reporter.from_scenario(scen)

# # plotting years
# plotyrs = [x for x in set(scen.set('year')) if x >= scen.firstmodelyear]

# rep.set_filters(c = 'electricity')
# elec = rep.full_key('out')
# elec = elec.drop('yv','m','nd', '')
# elec_gen = rep.get(elec)
# elec_gen
# elec_gen.to_csv('seas_bra.csv')

# rep.set_filters(c = 'electricity', hd = 'winter')
# elec = rep.full_key('out')
# elec = elec.drop('yv','m','nd','h')
# elec_gen = rep.get(elec)
# elec_gen


# def collapse_callback(df):
#     df['variable'] = 'Electricity Generation|' + df['l']+ '|'+df['t']
#     return df.drop(['t','l'], axis =1)

    
# new_key = rep.convert_pyam(quantities=elec.drop('h', 'm', 'nd', 'yv'),
#                            rename=dict(nl="region", ya="year"),
#                            collapse=collapse_callback)
    

    
# df_elec = rep.get(new_key)
# df_elec.data.unit = 'GWa'
# df_elec.to_csv('seas_bra.csv')


# elec_gen = pd.read_csv("seas_bra.csv")
# elec_gen.columns 

# elec_gen = pyam.IamDataFrame(data='seas_bra.csv', encoding='ISO-8859-1')

# elec = elec_gen.filter(region=['North'], variable='Electricity Generation|secondary|*', year=plotyrs)
# elec.plot.bar(stacked=True)

# elec = elec_gen.filter(variable='Electricity Generation|final|*', year=plotyrs)
# elec.plot(legend=True)