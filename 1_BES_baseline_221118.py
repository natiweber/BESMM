# -*- coding: utf-8 -*-
"""
Created on Wed Jun  9 18:01:49 2021

@author: Natalia
"""

# load required packages 
#import itertools
import pandas as pd

import matplotlib.pyplot as plt
plt.style.use('ggplot')

import ixmp
import message_ix

from message_ix.utils import make_df

mp = ixmp.Platform("default", jvmargs=["-Xms800m", "-Xmx8g"])
# %% start
model = "MESSAGEix-BR"
scen = "baseline"
scenario = message_ix.Scenario(mp, model, scen, version = 'new')

history = [2020]
horizon = [2030, 2040, 2050, 2060, 2070, 2080, 2090, 2100]
scenario.add_horizon(
    year= history + horizon,
    firstmodelyear=horizon[0]
)

country = 'Brazil'
scenario.add_spatial_sets({'country': country})

# visualizing the set
scenario.set('map_spatial_hierarchy')

nodes = ['South', 'North', 'Northeast', 'Southeast']
space_level = 'province'
scenario.add_set('lvl_spatial', space_level)
for node in nodes:
    scenario.add_set('node', node)
    scenario.add_set('map_spatial_hierarchy', [space_level, node, country])

scenario.set('map_spatial_hierarchy')

scenario.add_set("commodity", ["electricity", "water_1", "water_2", "water_3", "water_4", "water_5", "water_6",
                              "water_7", "water_8", "water_9", "water_10", "water_11", "water_12"])
scenario.add_set("level", ["primary" , "secondary", "final"])
scenario.add_set('mode', ['n-to-ne', 'ne-to-n', 'n-to-se', 'se-to-n', 
                          'ne-to-se', 'se-to-ne', 'se-to-s', 's-to-se', 'M1'])
scenario.set("mode")

scenario.add_par("interestrate", horizon, value=0.08, unit='-') #EPE

# residential demand
elec_growth = pd.Series([1.34, 1.77, 2.31, 3.17, 3.71, 4.26, 4.8, 5.42], #ssp2-45
                        index=pd.Index(horizon, name='Time'))
#elec_growth.plot(title='Electricity Demand Growth')

plants = [
    "bio_ppl",
    "gas_ppl",
    "wind_ppl_on",
    "wind_ppl_off",
    "coal_ppl",
    "nuc_ppl",
    "oil_ppl",
    "solar_pv_ppl"
]

north_hydro = ["hydro_4", "hydro_8", "hydro_9"]
northeast_hydro = ["hydro_3"]
southeast_hydro = ["hydro_1", "hydro_5", "hydro_6", "hydro_7",
                "hydro_10", "hydro_12"]
south_hydro = ["hydro_2", "hydro_11"]

north_res = [ "river4", "river8", "river9"]
northeast_res = ["river3"]
southeast_res = ["river1", "river5", "river6", "river7", "river10", "river12" ]
south_res = ["river2", "river11"]

north_wat = [ "water_supply_4", "water_supply_8", "water_supply_9"]
northeast_wat = ["water_supply_3"]
southeast_wat = ["water_supply_1", "water_supply_5", "water_supply_6", "water_supply_7", "water_supply_10", "water_supply_12" ]
south_wat = ["water_supply_2", "water_supply_11"]

final_energy_techs = ["grid1", "grid2", "grid3", "grid4", "grid_n", "grid_ne", "grid_se", "grid_s"]


technologies = plants + north_hydro + northeast_hydro + southeast_hydro + south_hydro + north_res + northeast_res + southeast_res + south_res + final_energy_techs + north_wat + northeast_wat + southeast_wat + south_wat

scenario.add_set("technology", technologies)

# %% Adding electricity demand
# Data can be defined in a dictionary or imported from Excel (input-data.xlsx)
demand_per_year = {
        'South': 11.67, # electricity demand GWh BEN year 2019
        'North': 5.57,
        'Northeast': 11.05,
        'Southeast': 39.55,
        }

# Loop over nodes
for node, dem in demand_per_year.items():
    demand_data = pd.DataFrame({
            'node': node,
            'commodity': 'electricity',
            'level': 'final',
            'year': horizon,
            'time': 'year',
            'value': dem * elec_growth, #cenário expansão crescimento da demanda de 3.45%a.a.
            'unit': 'GWa',
        })
    scenario.add_par("demand", demand_data)


elec_demand = sum(demand_per_year.values())
elec_growth = elec_demand * elec_growth
elec_growth.plot(title='Demand')

year_df = scenario.vintage_and_active_years()
vintage_years, act_years = year_df['year_vtg'], year_df['year_act']

[x for x in scenario.par_list() if 'mode' in scenario.idx_sets(x)]

# %% 1) North
lifetimes = {
    "hydro_4": 100, "hydro_8": 100, "hydro_9": 100,  "bio_ppl": 20, "gas_ppl": 20, "wind_ppl_on": 20, 
    "wind_ppl_off": 20,  "coal_ppl": 30, "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "grid1": 30, "grid_n": 30, "river4":1000, "river8":1000, "river9":1000, "water_supply_4":1000,
    "water_supply_8":1000, "water_supply_9":1000,
}
# Adding technical lifetime
base_technical_lifetime_n = {
    'node_loc': 'North',
    'year_vtg': horizon,
    'unit': 'y',
}

for tec, val in lifetimes.items():
    df_n = make_df(base_technical_lifetime_n, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_n)

# Adding input and output
base_input_n1 = {
    'node_loc': 'North',
    'node_origin': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-ne',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_n1 = {
    'node_loc': 'North',
    'node_dest': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-ne',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_n2 = {
    'node_loc': 'North',
    'node_origin': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-n',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_n2 = {
    'node_loc': 'North',
    'node_dest': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-n',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


#grids

grid_efficiency = 1/0.85
grid_out_n1 = make_df(base_output_n1, technology='grid1', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_n1)

grid_in_n1 = make_df(base_input_n1, technology='grid1', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_n1)

grid_out_n2 = make_df(base_output_n2, technology='grid1', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_n2)

grid_in_n2 = make_df(base_input_n2, technology='grid1', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_n2)


# internal grid in the region

input_n = {
    'node_loc': 'North',
    'node_origin': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_n = {
    'node_loc': 'North',
    'node_dest': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


grid_eff = 1/0.9
grid_out_n = make_df(output_n, technology='grid_n', commodity='electricity', 
                   level='final', value=1.0)
scenario.add_par('output', grid_out_n)

grid_in_n = make_df(input_n, technology='grid_n', commodity='electricity',
                  level='secondary', value=grid_eff)
scenario.add_par('input', grid_in_n)


#primary to secondary for hydro_ppl

n_hydro_out = {"hydro_4": 1,
           "hydro_8": 1,
           "hydro_9": 1}

for h_plant, val in n_hydro_out.items():
    h_plant_out_n = make_df(output_n, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value= val, unit="GWa")

    # Removing extra years based on lifetime 
    condition = h_plant_out_n['year_act'] < h_plant_out_n['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n = h_plant_out_n.loc[condition] 

    # Removing extra years based on lifetime
    condition = h_plant_out_n['year_act'] < h_plant_out_n['year_vtg'] + lifetimes[h_plant]
    h_plant_out_n = h_plant_out_n.loc[condition]

    scenario.add_par('output', h_plant_out_n)
    
n_hydro_out_2 =  {"hydro_4": 1558.6,
              "hydro_8": 1317.0,
              "hydro_9": 4898.5}
    
for h_plant, val in n_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_n_2 = make_df(output_n, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_n_2['year_act'] < h_plant_out_n_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_n_2 = h_plant_out_n_2.loc[condition]
    
    scenario.add_par('output', h_plant_out_n_2)
    
n_hydro_in = {"hydro_4": 1558.6,
              "hydro_8": 1317.0,
              "hydro_9": 4898.5}
    
for h_plant, val in n_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_n = make_df(input_n, technology= h_plant, commodity= wat, 
                   level='primary', value= 1, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = h_plant_in_n['year_act'] < h_plant_in_n['year_vtg'] + lifetimes[h_plant] 

    # Removing extra years based on lifetime
    condition = h_plant_in_n['year_act'] < h_plant_in_n['year_vtg'] + lifetimes[h_plant]

    h_plant_in_n = h_plant_in_n.loc[condition]
    scenario.add_par('input', h_plant_in_n)
    
for river in north_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_n = make_df(output_n, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = river_out_n['year_act'] < river_out_n['year_vtg'] + lifetimes[river] 
    river_out_n = river_out_n.loc[condition] 

    # Removing extra years based on lifetime
    condition = river_out_n['year_act'] < river_out_n['year_vtg'] + lifetimes[river]
    river_out_n = river_out_n.loc[condition]

    scenario.add_par('output', river_out_n)

# secondary to final to water_supply

n_water_out = {"water_supply_4": 1558.6,
              "water_supply_8": 1317.0,
              "water_supply_9": 4898.5}

for w_supply, val in n_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_n = make_df(output_n, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_out_n['year_act'] < w_supply_out_n['year_vtg'] + lifetimes[w_supply] 
    w_supply_out_n = w_supply_out_n.loc[condition] 

    # Removing extra years based on lifetime
    condition = w_supply_out_n['year_act'] < w_supply_out_n['year_vtg'] + lifetimes[w_supply]
    w_supply_out_n = w_supply_out_n.loc[condition]

    scenario.add_par('output', w_supply_out_n)

n_water_in = {"water_supply_4": 1558.6,
              "water_supply_8": 1317.0,
              "water_supply_9": 4898.5}
    
for w_supply, val in n_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_n = make_df(input_n, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_in_n['year_act'] < w_supply_in_n['year_vtg'] + lifetimes[w_supply] 

    # Removing extra years based on lifetime
    condition = w_supply_in_n['year_act'] < w_supply_in_n['year_vtg'] + lifetimes[w_supply]

    w_supply_in_n = w_supply_in_n.loc[condition]
    scenario.add_par('input', w_supply_in_n)
    
#secondary to useful e_tecs

for tech in plants:
     tech_out_n = make_df(output_n, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")

     # Removing extra years based on lifetime 
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + lifetimes[tech] 
     tech_out_n = tech_out_n.loc[condition] 
     scenario.add_par('output', tech_out_n)

# Adding technical lifetime 

     # Removing extra years based on lifetime
     condition = tech_out_n['year_act'] < tech_out_n['year_vtg'] + lifetimes[tech]
     tech_out_n = tech_out_n.loc[condition]
     scenario.add_par('output', tech_out_n)

base_capacity_factor_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_4": 0.8, #EPE
    "hydro_8": 0.8, #EPE
    "hydro_9": 0.8, #EPE
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_on": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "wind_ppl_off": 0.5,#IEA wind roadmapp 2019 
    "coal_ppl": 0.7,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75,
    "water_supply_4": 0.9, 
    "water_supply_8": 0.9, 
    "water_supply_9": 0.9,
    "grid1": 0.5,
    "grid_n": 0.7,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_n, technology=tec, value=val)
     # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    # Removing extra years based on lifetime
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec]
    df = df.loc[condition]
    scenario.add_par('capacity_factor', df)
    
base_capacity_n = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'North',
    'unit': 'GW',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
installed_capacity = 24.11 
thermal_capacity = 3.93 
hydro_capacity= 19.8
transmission_capacity = 44.079
   
#'wind_ppl': 1 / 10 / capacity_factor['wind_ppl'] / 2,

base_cap = {
    "hydro_4": 9.62/10, 
    "hydro_8": 11.03/10, 
    "hydro_9": 1.2/10, 
    "bio_ppl": thermal_capacity*0.38/10,  
    "gas_ppl": thermal_capacity*0.34/10,
    "wind_ppl_on": 0.33/10, 
    "wind_ppl_off": 0.001/10,
    "coal_ppl": thermal_capacity*0.08/10, 
    "nuc_ppl": 0/10, 
    "solar_pv_ppl": 0.05,
    "oil_ppl": thermal_capacity*0.2/10,
    "grid1": transmission_capacity/10,
    "grid_n": transmission_capacity/10,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_n, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

river_capacity_n = {
    'year_vtg': [2020],
    'time': 'year',
    'node_loc': 'North',
    'unit': 'm^3/a',
}

base_cap = {
    "water_supply_4": 250000,
    "water_supply_8": 129000,
    "water_supply_9": 39000,
}

for tec, val in base_cap.items():
    df = make_df(river_capacity_n, technology=tec, value=val, unit= 'm^3/a')
    scenario.add_par('historical_new_capacity', df)  

# %% Adding costs

base_inv_cost_n = {
    'node_loc': 'North',
    'year_vtg': horizon,
    'unit': 'USD/GW',
}

# Adding a new unit to the library
mp.add_unit('USD/GW')    

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_4": 1352.*1E6, #EPE mean value for UHE
    "hydro_8": 1352.*1E6, #EPE mean value for UHE
    "hydro_9": 1352.*1E6,#EPE mean value for UHE
    "bio_ppl": 1200.*1E6,#EPE 
    "gas_ppl": 900*1E6, #EPE mean value
    "wind_ppl_on": 1200*1E6,#EPE mean value
    "wind_ppl_off": 230*1E6,#EPE mean value
    "coal_ppl": 2500*1E6, #EPE
    "nuc_ppl": 5000*1E6,#EPE
    "solar_pv_ppl":1100*1E6, #min value in EPE, max value is 1350
    "oil_ppl": 1100*1E6,
    "river4": 0.01, #EPE mean value for UHE
    "river8": 0.01, #EPE mean value for UHE
    "river9": 0.01,
    "water_supply_4": 0.01, #EPE mean value for UHE
    "water_supply_8": 0.01, #EPE mean value for UHE
    "water_supply_9": 0.01,
    'grid1': 1000*1E6,
    'grid_n': 359*1E6,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_n, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'USD/GW',
}


# in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M costs
# based on the size of the plant, e.g. lightning, labor, scheduled maintenance, etc.)

costs = {
    "hydro_4": 50/3.9*1E6, #EPE
    "hydro_8": 50/3.9*1E6, #EPE 
    "hydro_9": 50/3.9*1E6,#EPE 
    "bio_ppl": 90/3.9*1E6, #EPE
    "gas_ppl": 220*1E6,#EPE
    "wind_ppl_on": 100/3.9*1E6,#EPE
    "wind_ppl_off": 100/3.9*1E6,#EPE
    "coal_ppl": 100*1E6,#EPE
    "nuc_ppl": 110*1E6, #EPE
    "solar_pv_ppl":20/3.87*1E6, #EPE
    "oil_ppl": 220*1E6,
    'grid1':  36*1E6,
    'grid_n': 36*1E6,
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_n, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants

var_cost_n = {
    'node_loc': 'North',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'USD/GWa',
}

costs = {
    "gas_ppl": 25*1E6, #EPE mean value
    "coal_ppl": 30*1E6, #EPE
    "oil_ppl": 35*1E6,
}

for tec, val in costs.items():
    df = make_df(var_cost_n, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity

### 1.1) North baseline and growth parameters
base_activity_n1 = {
    'node_loc': 'North',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}
base_activity_n2 = {
    'node_loc': 'North',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 1.823
hydro_act = 7.527
#old activity basen on 2019 BEN
old_activity = {
    "hydro_4": 0.5*9.6, 
    "hydro_8": 0.5*11.03, 
    "hydro_9": 0.5*1.2, 
    "bio_ppl": 0.02,  
    "gas_ppl": 0.01,
    "wind_ppl_on": 0.2, 
    "wind_ppl_off": 0.001, 
    "coal_ppl": 0.1, 
    "nuc_ppl": 0., 
    "solar_pv_ppl": 0.001,
    "oil_ppl": 1.7,
}

for tec, val in old_activity.items():
    df = make_df(base_activity_n1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    df = make_df(base_activity_n2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    

# base_growth_n = {
#     'node_loc': 'North',
#     'year_act': horizon,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "bio_ppl": 0.1, 
#     "wind_ppl_on": 0.2,
#     "wind_ppl_off": 0.2,
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.02,
#     "coal_ppl": 0.0,
#     "oil_ppl": 0.0,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_n, technology=tec, value=val) 
#     scenario.add_par('growth_activity_up', df)

# growth_technologies = {
#     "bio_ppl": -0.05, 
#     "gas_ppl": -0.05,
#     "wind_ppl": 0.,
#     "nuc_ppl": -0.1,
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_n, technology=tec, value=val) 
#     scenario.add_par('growth_activity_lo', df)
    
# cap_growth_n = {
#     'node_loc': 'North',
#     'year_vtg': history,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "hydro_4": 0.,
#     "hydro_8": 0.,
#     "hydro_9": 0.,
#     "bio_ppl": 0.1, 
#     "wind_ppl_on": 0.1,
#     "wind_ppl_off": 0.1, 
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.05,
#     "coal_ppl": 0.05,
#     "oil_ppl": 0.05,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_n, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_up', df)

# growth_technologies = {
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.0,
#     "wind_ppl": 0.0,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_n, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_lo', df)
    
## Bound activity
    
   
new_activity_n = {'hydro_4': 9.6,
                'hydro_8': 11.03,
               'hydro_9': 1.2,
                 }


base_cap = {
    'node_loc': 'North',
    'year_act': horizon,
    'time': 'year',
    'unit': 'GWa',
}


for tec, val in new_activity_n.items():
    df = make_df(base_cap, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)
    

  

# %% 2) Northeast baseline

lifetimes = {
    "hydro_3": 100,  "bio_ppl": 20, "gas_ppl": 20, "wind_ppl_on": 20,
    "wind_ppl_off": 20, "coal_ppl": 30, "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "river3":1000, "water_supply_3":1000,  "grid2": 30, "grid_ne": 30, 
}

base_input_ne1 = {
    'node_loc': 'Northeast',
    'node_origin': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_ne1 = {
    'node_loc': 'Northeast',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'ne-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_ne2 = {
    'node_loc': 'Northeast',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-ne',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_ne2 = {
    'node_loc': 'Northeast',
    'node_dest': 'Northeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-ne',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


#grids

grid_efficiency = 1/0.85
grid_out_ne1 = make_df(base_output_ne1, technology='grid2', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_ne1)

grid_in_ne1 = make_df(base_input_ne1, technology='grid2', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_ne1)

grid_out_ne2 = make_df(base_output_ne2, technology='grid2', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_ne2)

grid_in_ne2 = make_df(base_input_ne2, technology='grid2', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_ne2)

# internal grid in the region

input_ne = {
    'node_loc': 'Northeast',
    'node_origin': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_ne = {
    'node_loc': 'Northeast',
    'node_dest': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

input_ne = {
    'node_loc': 'Northeast',
    'node_origin': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_ne = {
    'node_loc': 'Northeast',
    'node_dest': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

grid_eff = 1/0.9
grid_out_ne = make_df(output_ne, technology='grid_ne', commodity='electricity', 
                   level='final', value=1.0)
scenario.add_par('output', grid_out_ne)

grid_in_ne = make_df(input_ne, technology='grid_ne', commodity='electricity',
                  level='secondary', value=grid_eff)
scenario.add_par('input', grid_in_ne)

#primary to secondary for hydro_ppl

ne_hydro_out = {"hydro_3": 1.,
            }
# REE 3

for h_plant, val in ne_hydro_out.items():
    h_plant_out_ne = make_df(output_ne, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_ne['year_act'] < h_plant_out_ne['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne = h_plant_out_ne.loc[condition] 
    scenario.add_par('output', h_plant_out_ne)

ne_hydro_out_2 =   {"hydro_3": 595.1,
            } 
    
for h_plant, val in ne_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_ne_2 = make_df(output_ne, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_ne_2['year_act'] < h_plant_out_ne_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_ne_2 = h_plant_out_ne_2.loc[condition]
    
    scenario.add_par('output', h_plant_out_ne_2)
    
ne_hydro_in = {"hydro_3": 595.1,
            }    

for h_plant, val in ne_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_ne = make_df(input_ne, technology= h_plant, commodity= wat, 
                   level='primary', value=1, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_in_ne['year_act'] < h_plant_in_ne['year_vtg'] + lifetimes[h_plant] 
    h_plant_in_ne = h_plant_in_ne.loc[condition]
    scenario.add_par('input', h_plant_in_ne)
    
for river in northeast_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_ne = make_df(output_ne, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/a")
    # Removing extra years based on lifetime 
    condition = river_out_ne['year_act'] < river_out_ne['year_vtg'] + lifetimes[river] 
    river_out_ne = river_out_ne.loc[condition] 
    scenario.add_par('output', river_out_ne)
    
# secondary to final to water_supply

ne_water_out = {"water_supply_3": 595.1,
              }

for w_supply, val in ne_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_ne = make_df(output_ne, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_out_ne['year_act'] < w_supply_out_ne['year_vtg'] + lifetimes[w_supply] 
    w_supply_out_ne = w_supply_out_ne.loc[condition] 

    # Removing extra years based on lifetime
    condition = w_supply_out_ne['year_act'] < w_supply_out_ne['year_vtg'] + lifetimes[w_supply]
    w_supply_out_ne = w_supply_out_ne.loc[condition]

    scenario.add_par('output', w_supply_out_ne)



ne_water_in = {"water_supply_3": 595.1,
              }
    
for w_supply, val in ne_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_ne = make_df(input_ne, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_in_ne['year_act'] < w_supply_in_ne['year_vtg'] + lifetimes[w_supply] 

    # Removing extra years based on lifetime
    condition = w_supply_in_ne['year_act'] < w_supply_in_ne['year_vtg'] + lifetimes[w_supply]

    w_supply_in_ne = w_supply_in_ne.loc[condition]
    scenario.add_par('input', w_supply_in_ne)

#secondary to useful e_tecs

for tech in plants:
     tech_out_ne = make_df(output_ne, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
      # Removing extra years based on lifetime 
     condition = tech_out_ne['year_act'] < tech_out_ne['year_vtg'] + lifetimes[tech] 
     tech_out_ne = tech_out_ne.loc[condition]
     scenario.add_par('output', tech_out_ne)

base_technical_lifetime_ne = {
    'node_loc': 'Northeast',
    'year_vtg': horizon,
    'unit': 'y',
}


for tec, val in lifetimes.items():
    df_ne = make_df(base_technical_lifetime_ne, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_ne)

base_capacity_factor_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_3": 0.8  ,#EPE 
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_on": 0.47,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "wind_ppl_off": 0.53,
    "coal_ppl": 0.7,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75, #EPE
    "water_supply_3": 0.9,
    "grid2": 0.5,
    "grid_ne": 0.7,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_ne, technology=tec, value=val)
    # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)
    
base_capacity_ne = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'Northeast',
    'unit': 'GW',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
installed_capacity = 32.36 
thermal_capacity = 7.33 
transmission_capacity = 22.068
base_cap = {
    "hydro_3": 8.3/10, 
    "bio_ppl": thermal_capacity*0.38/10,  
    "gas_ppl": thermal_capacity*0.34/10,
    "wind_ppl_on": 13./10, 
    "wind_ppl_off": 0.01/10, 
    "coal_ppl": thermal_capacity*0.08/10, 
    "nuc_ppl": 0./10, 
    "solar_pv_ppl": 1.4/5,
    "oil_ppl": thermal_capacity*0.2/10,
    "grid2": transmission_capacity/10,
    "grid_ne": transmission_capacity/10,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_ne, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?

river_capacity_ne = {
    'year_vtg': [2020],
    'time': 'year',
    'node_loc': 'Northeast',
    'unit': 'm^3/a',
}

base_cap = {
   "water_supply_3": 180000,
}

for tec, val in base_cap.items():
    df = make_df(river_capacity_ne, technology=tec, value=val, unit= 'm^3/a')
    scenario.add_par('historical_new_capacity', df)  


    
# %% Adding costs

base_inv_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': horizon,
    'unit': 'USD/GW',
}


# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_3": 1352.*1E6,#EPE mean value for UHE
    "bio_ppl": 1200.*1E6,#EPE 
    "gas_ppl": 900*1E6, #EPE mean value
    "wind_ppl_on": 1200*1E6,#EPE mean value
    "wind_ppl_off": 230*1E6,#EPE mean value
    "coal_ppl": 2500*1E6, #EPE
    "nuc_ppl": 5000*1E6,#EPE
    "solar_pv_ppl":1100*1E6, #min value in EPE, max value is 1350
    "oil_ppl": 1100*1E6,
    'grid2':  1000*1E6,
    "river3": 0.01,
    "water_supply_3": 0.01,
    'grid_ne': 359*1E6,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_ne, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'USD/GW',
}

# in $ / kW / year (every year a fixed quantity is destinated to cover part of the O&M costs
# based on the size of the plant, e.g. lightning, labor, scheduled maintenance, etc.)

costs = {
    "hydro_3": 50/3.9*1E6,#EPE
    "bio_ppl": 90/3.9*1E6, #EPE
    "gas_ppl": 220*1E6,#EPE
    "wind_ppl_on": 100/3.9*1E6,#EPE
    "wind_ppl_off": 100/3.9*1E6,#EPE
    "coal_ppl": 100*1E6,#EPE
    "nuc_ppl": 110*1E6, #EPE
    "solar_pv_ppl":20/3.87*1E6, #EPE
    "oil_ppl": 220*1E6,
    'grid2':  36*1E6,
    'grid_ne': 36*1E6,
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_ne, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants

var_cost_ne = {
    'node_loc': 'Northeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'USD/GWa',
}

costs = {
    "gas_ppl": 25*1E6, #EPE mean value
    "coal_ppl": 30*1E6, #EPE
    "oil_ppl": 35*1E6,
}

for tec, val in costs.items():
    df = make_df(var_cost_ne, technology=tec, value=val)
    scenario.add_par('var_cost', df)
    

# %% Acitvity and Capacity

### 2.2) Northeast base and growth

base_activity_ne1 = {
    'node_loc': 'Northeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}
base_activity_ne2 = {
    'node_loc': 'Northeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 2.06
#old activity basen on 2019 BEN
old_activity = {
    "hydro_3": 0.5*3.1, 
    "bio_ppl": 0.1,  
    "gas_ppl": 0.0002,
    "wind_ppl_on": 5.6, 
    "wind_ppl_off": 0.01, 
    "coal_ppl": 0.3, 
    "nuc_ppl": 0., 
    "solar_pv_ppl": 0.5,
    "oil_ppl": 1.1,
}

for tec, val in old_activity.items():
    df = make_df(base_activity_ne1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    df = make_df(base_activity_ne2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

# base_growth_ne = {
#     'node_loc': 'Northeast',
#     'year_act': horizon,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "bio_ppl": 0.05, 
#     "wind_ppl_on": 0.08,
#     "wind_ppl_off": 0.08, 
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.02,
#     "coal_ppl": 0.0,
#     "oil_ppl": 0.0,
# }


# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_ne, technology=tec, value=val) 
#     scenario.add_par('growth_activity_up', df)

# growth_technologies = {
#     "bio_ppl": -0.05, 
#     "gas_ppl": -0.05,
#     "wind_ppl": 0.,
#     "nuc_ppl": -0.1,
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_ne, technology=tec, value=val) 
#     scenario.add_par('growth_activity_lo', df)
    
# cap_growth_ne = {
#     'node_loc': 'Northeast',
#     'year_vtg': history,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "hydro_3": 0.0, 
#     "bio_ppl": 0.1, 
#     "wind_ppl_on": 0.15,
#     "wind_ppl_off": 0.15,
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.05,
#     "coal_ppl": 0.05,
#     "oil_ppl": 0.05,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_ne, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_up', df)

# growth_technologies = {
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.0,
#     'wind_ppl': 0.0,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_ne, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_lo', df)

## Bound activity

new_activity_ne = {'hydro_3': 8.3,
                   
}


base_act = {
    'node_loc': 'Northeast',
    'year_act': horizon,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

for tec, val in new_activity_ne.items():
    df = make_df(base_act, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)
    



# %% 3) Southeast baseline

lifetimes = {
    "hydro_1": 100, "hydro_5": 100, "hydro_6": 100, "hydro_7": 100,
    "hydro_10": 100, "hydro_12": 100,
    "bio_ppl": 20, "gas_ppl": 20, "wind_ppl_on": 20, "wind_ppl_off": 20,  "coal_ppl": 30,
    "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "grid3": 30, "grid_se": 30, "river1":1000,  "river5":1000, "river6":1000,"river7":1000,
   "river10":1000,  "river12":1000, "water_supply_1":1000,  "water_supply_5":1000, 
   "water_supply_6":1000,"water_supply_7":1000, "water_supply_10":1000,  "water_supply_12":1000,
}

base_input_se1 = {
    'node_loc': 'Southeast',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-n',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_se1 = {
    'node_loc': 'Southeast',
    'node_dest': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-n',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_se2 = {
    'node_loc': 'Southeast',
    'node_origin': 'North',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_se2 = {
    'node_loc': 'Southeast',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'n-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

#grids

grid_efficiency = 1/0.85
grid_out_se1 = make_df(base_output_se1, technology='grid3', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_se1)

grid_in_se1 = make_df(base_input_se1, technology='grid3', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_se1)

grid_out_se2 = make_df(base_output_se2, technology='grid3', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_se2)

grid_in_se2 = make_df(base_input_se2, technology='grid3', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_se2)

# internal grid in the region

input_se = {
    'node_loc': 'Southeast',
    'node_origin': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_se = {
    'node_loc': 'Southeast',
    'node_dest': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# internal grid in the region

grid_eff = 1/0.9
grid_out_se = make_df(output_se, technology='grid_se', commodity='electricity', 
                   level='final', value=1.0)
scenario.add_par('output', grid_out_se)

grid_in_se = make_df(input_se, technology='grid_se', commodity='electricity',
                  level='secondary', value=grid_eff)
scenario.add_par('input', grid_in_se)

# hydro techs

input_se = {
    'node_loc': 'Southeast',
    'node_origin': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_se = {
    'node_loc': 'Southeast',
    'node_dest': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


se_hydro_out = {"hydro_1": 1,
"hydro_5": 1.,
"hydro_6": 1., 
"hydro_7": 1.,
"hydro_10": 1., 
"hydro_12": 1.,
}

for h_plant, val in se_hydro_out.items():
    h_plant_out_se = make_df(output_se, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_se['year_act'] < h_plant_out_se['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se = h_plant_out_se.loc[condition]
    scenario.add_par('output', h_plant_out_se)
    
se_hydro_out_2 = {"hydro_1": 456.0,
"hydro_5": 968.0,
"hydro_6": 3793.4, 
"hydro_7": 1205.3,
"hydro_10": 560.6, 
"hydro_12": 1004.9,
}

    
for h_plant, val in se_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_se_2 = make_df(output_se, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_se_2['year_act'] < h_plant_out_se_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_se_2 = h_plant_out_se_2.loc[condition]
    scenario.add_par('output', h_plant_out_se_2)
    
se_hydro_in = {"hydro_1": 456.0,
"hydro_5": 968.0,
"hydro_6": 3793.4, 
"hydro_7": 1205.3,
"hydro_10": 560.6, 
"hydro_12": 1004.9,
}

for h_plant, val in se_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_se = make_df(input_se, technology= h_plant, commodity= wat, 
                   level='primary', value=1, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_in_se['year_act'] < h_plant_in_se['year_vtg'] + lifetimes[h_plant] 
    h_plant_in_se = h_plant_in_se.loc[condition]
    scenario.add_par('input', h_plant_in_se)
    
for river in southeast_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_se = make_df(output_se, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/a")
    # Removing extra years based on lifetime 
    condition = river_out_se['year_act'] < river_out_se['year_vtg'] + lifetimes[river] 
    river_out_se = river_out_se.loc[condition]
    scenario.add_par('output', river_out_se)
   
# secondary to final to water_supply

se_water_out = {"water_supply_1": 456.0,
                "water_supply_5": 968.0,
                "water_supply_6": 3793.4, 
                "water_supply_7": 1205.3,
                "water_supply_10": 560.6, 
                "water_supply_12": 1004.9,
                 }

for w_supply, val in se_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_se = make_df(output_se, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_out_se['year_act'] < w_supply_out_se['year_vtg'] + lifetimes[w_supply] 
    w_supply_out_se = w_supply_out_se.loc[condition] 

    # Removing extra years based on lifetime
    condition = w_supply_out_se['year_act'] < w_supply_out_se['year_vtg'] + lifetimes[w_supply]
    w_supply_out_se = w_supply_out_se.loc[condition]

    scenario.add_par('output', w_supply_out_se)

se_water_in = {"water_supply_1": 456.0,
               "water_supply_5": 968.0,
               "water_supply_6": 3793.4, 
               "water_supply_7": 1205.3,
               "water_supply_10": 560.6, 
               "water_supply_12": 1004.9,
              }
    
for w_supply, val in se_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_se = make_df(input_se, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_in_se['year_act'] < w_supply_in_se['year_vtg'] + lifetimes[w_supply] 

    # Removing extra years based on lifetime
    condition = w_supply_in_se['year_act'] < w_supply_in_se['year_vtg'] + lifetimes[w_supply]

    w_supply_in_se = w_supply_in_se.loc[condition]
    scenario.add_par('input', w_supply_in_se)

#secondary to useful e_tecs

for tech in plants:
     tech_out_se = make_df(output_se, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_se['year_act'] < tech_out_se['year_vtg'] + lifetimes[tech] 
     tech_out_se = tech_out_se.loc[condition]
     scenario.add_par('output', tech_out_se)


base_technical_lifetime_se = {
    'node_loc': 'Southeast',
    'year_vtg': horizon,
    'unit': 'y',
}


for tec, val in lifetimes.items():
    df_se = make_df(base_technical_lifetime_se, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_se)

base_capacity_factor_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_1": 0.8, #EPE
    "hydro_5": 0.8,
    "hydro_6": 0.8,
    "hydro_7": 0.8,
    "hydro_10": 0.8,
    "hydro_12": 0.8,     
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_on": 0.435,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "wind_ppl_off": 0.435,
    "coal_ppl": 0.7,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75, #EPE
    "water_supply_1": 0.9,
    "water_supply_5": 0.9,
    "water_supply_6": 0.9,
    "water_supply_7": 0.9,
    "water_supply_10": 0.9,
    "water_supply_12": 0.9,
    "grid3": 0.5,
    "grid_se": 0.7,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_se, technology=tec, value=val)
     # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)
    
base_capacity_se = {
    'year_vtg': history,
    'time': 'year',
    'node_loc': 'Southeast',
    'unit': 'GW',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
installed_capacity = 86.61 
thermal_capacity = 20.71 
hydro_capacity = 63.2/6
transmission_capacity = 83.096
base_cap = {
    "hydro_1": 6.4/10, 
    "hydro_5": 14./10, 
    "hydro_6": 7.3/10, 
    "hydro_7": 3.2/10,
    "hydro_10": 27.6/10,
    "hydro_12": 2.4/10,
    "bio_ppl": thermal_capacity*0.38/10,  
    "gas_ppl": thermal_capacity*0.34/10,
    "wind_ppl_on": 0.03/10,
    "wind_ppl_off": 0.0001/10,
    "coal_ppl": thermal_capacity*0.08/10, 
    "nuc_ppl": 1.99/10, 
    "solar_pv_ppl": 1,
    "oil_ppl": thermal_capacity*0.2/10,
    "grid2": transmission_capacity/10,
    "grid_se": transmission_capacity/10,
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_se, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?
    
river_capacity_se = {
    'year_vtg': [2020],
    'time': 'year',
    'node_loc': 'Southeast',
    'unit': 'm^3/a',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]

base_cap = {
    "water_supply_1": 44000, #sum of season water inflow in 2020
    "water_supply_5": 50000,
    "water_supply_6": 388000,
    "water_supply_7": 26000,
    "water_supply_10": 138000,
    "water_supply_12": 32000,
}

for tec, val in base_cap.items():
    df = make_df(river_capacity_se, technology=tec, value=val, unit= 'm^3/a')
    scenario.add_par('historical_new_capacity', df)   
    
# %% Adding costs

base_inv_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': horizon,
    'unit': 'USD/GW',
}

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_1": 1352.*1E6,
    "hydro_5": 1352.*1E6,
    "hydro_6": 1352.*1E6,
    "hydro_7": 1352.*1E6,
    "hydro_10": 1352.*1E6,
    "hydro_12": 1352.*1E6,#EPE mean value for UHE
    "bio_ppl": 1200.*1E6,#EPE 
    "gas_ppl": 900*1E6, #EPE mean value
    "wind_ppl_on": 1200*1E6,#EPE mean value
    "wind_ppl_off": 230*1E6,
    "coal_ppl": 2500*1E6, #EPE
    "nuc_ppl": 5000*1E6,#EPE
    "solar_pv_ppl":1100*1E6, #min value in EPE, max value is 1350
    "oil_ppl": 1100*1E6,
    'grid3':  1000*1E6,
    "river1": 0.01,
    "river5": 0.01,
    "river6": 0.01,
    "river7": 0.01,
    "river10": 0.01,
    "river12": 0.01,
    "water_supply_1": 0.01,
    "water_supply_5": 0.01,
    "water_supply_6": 0.01,
    "water_supply_7": 0.01,
    "water_supply_10": 0.01,
    "water_supply_12": 0.01,
    'grid_se': 462*1E6,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_se, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'USD/GW',
}

costs = {
    "hydro_1": 50/3.9*1E6,
    "hydro_5": 50/3.9*1E6,
    "hydro_6": 50/3.9*1E6,
    "hydro_7": 50/3.9*1E6,
    "hydro_10": 50/3.9*1E6,
    "hydro_12": 50/3.9*1E6,    
    "bio_ppl": 90/3.9*1E6, #EPE
    "gas_ppl": 220*1E6,#EPE
    "wind_ppl_on": 100/3.9*1E6,#EPE
    "wind_ppl_off": 100/3.9*1E6,#EPE
    "coal_ppl": 100*1E6,#EPE
    "nuc_ppl": 110*1E6, #EPE
    "solar_pv_ppl":20/3.87*1E6, #EPE
    "oil_ppl": 220*1E6,
    'grid3':  36*1E6,
    'grid_se': 36*1E6,
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_se, technology=tec, value=val)
    scenario.add_par('fix_cost', df)
    
### Adding variable cost = fuel cost to thermal power plants

var_cost_se = {
    'node_loc': 'Southeast',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'USD/GWa',
}

costs = {
    "gas_ppl": 25*1E6, #EPE mean value
    "coal_ppl": 30*1E6, #EPE
    "oil_ppl": 35*1E6,
    "nuc_ppl": 40*1E6,
}

for tec, val in costs.items():
    df = make_df(var_cost_se, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity

### 3.1) Southeast base and growth

base_activity_se1 = {
    'node_loc': 'Southeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_se2 = {
    'node_loc': 'Southeast',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 6.12
hydro_act = 29.72/6
#old activity basen on 2019 BEN
old_activity = {
    "hydro_1": 0.5*6.4, 
    "hydro_5": 0.5*14, 
    "hydro_6": 0.5*7.3, 
    "hydro_7": 0.5*3.2,
    "hydro_10": 0.5*27.6,
    "hydro_12": 0.5*2.4,
    "bio_ppl": 2.7,  
    "gas_ppl": 0.005,
    "wind_ppl_on":0.006,
     "wind_ppl_off":0.00001,
    "coal_ppl": 0.007, 
    "nuc_ppl":1.6, 
    "solar_pv_ppl":0.2,
    "oil_ppl": 2.8,
}

for tec, val in old_activity.items():
    df = make_df(base_activity_se1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

for tec, val in old_activity.items():
    df = make_df(base_activity_se2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

# base_growth_se = {
#     'node_loc': 'Southeast',
#     'year_act': horizon,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "bio_ppl": 0.05, 
#     "wind_ppl_on": 0.2, 
#     "wind_ppl_off": 0.2,
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.02,
#     "coal_ppl": 0.0,
#     "oil_ppl": 0.0,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_se, technology=tec, value=val) 
#     scenario.add_par('growth_activity_up', df)

# growth_technologies = {
#       "bio_ppl": -0.05, 
#     "gas_ppl": -0.05,
#     "wind_ppl": 0.,
#     "nuc_ppl": -0.1,
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_se, technology=tec, value=val) 
#     scenario.add_par('growth_activity_lo', df)
    
# cap_growth_se = {
#     'node_loc': 'Southeast',
#     'year_vtg': history,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "hydro_1": 0.,
#     "hydro_5": 0.,
#     "hydro_6": 0.,
#     "hydro_7": 0.,
#     "hydro_10": 0.,
#     "hydro_12": 0.,     
#     "bio_ppl": 0.1, 
#     "wind_ppl_on": 0.05,
#     "wind_ppl_off": 0.005,
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.05,
#     "coal_ppl": 0.05,
#     "oil_ppl": 0.05,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_se, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_up', df)

# growth_technologies = {
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.0
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_se, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_lo', df)
    
## Bound activity


new_activity_se = { "hydro_1": 6.4,
    "hydro_5": 14.,
    "hydro_6": 7.3,
    "hydro_7": 3.2,
    "hydro_10": 27.6,
    "hydro_12": 2.4, 
    
}

base_act = {
    'node_loc': 'Southeast',
    'year_act': horizon,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

for tec, val in new_activity_se.items():
    df = make_df(base_act, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)
    

# %% 4) South baseline

lifetimes = {
    "hydro_2": 100, "hydro_11": 100,  "bio_ppl": 20, "gas_ppl": 20, "wind_ppl_on": 20, 
    "wind_ppl_off": 20,  "coal_ppl": 30, "nuc_ppl": 60,  "solar_pv_ppl":20,  "oil_ppl": 20,
    "grid4": 30, "grid_s": 30, "river2":1000,  "river11":1000, "water_supply_2":1000,  
    "water_supply_11":1000,
}

base_input_s1 = {
    'node_loc': 'South',
    'node_origin': 'South',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 's-to-se',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_s1 = {
    'node_loc': 'South',
    'node_dest': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 's-to-se',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

base_input_s2 = {
    'node_loc': 'South',
    'node_origin': 'Southeast',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-s',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

base_output_s2 = {
    'node_loc': 'South',
    'node_dest': 'South',
    'commodity': 'electricity',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'se-to-s',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


#grids

grid_efficiency = 1/0.85
grid_out_s1 = make_df(base_output_s1, technology='grid4', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_s1)

grid_in_s1 = make_df(base_input_s1, technology='grid4', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_s1)

grid_out_s2 = make_df(base_output_s2, technology='grid4', commodity='electricity', 
                   level='secondary', value=1.0)
scenario.add_par('output', grid_out_s2)

grid_in_s2 = make_df(base_input_s2, technology='grid4', commodity='electricity',
                  level='secondary', value=grid_efficiency)
scenario.add_par('input', grid_in_s2)

#internal grid in the region

input_s = {
    'node_loc': 'South',
    'node_origin': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_s = {
    'node_loc': 'South',
    'node_dest': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}

# internal grid in the region

grid_eff = 1/0.9
grid_out_s = make_df(output_s, technology='grid_s', commodity='electricity', 
                   level='final', value=1.0)
scenario.add_par('output', grid_out_s)

grid_in_s = make_df(input_s, technology='grid_s', commodity='electricity',
                  level='secondary', value=grid_eff)
scenario.add_par('input', grid_in_s)

input_s = {
    'node_loc': 'South',
    'node_origin': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_origin': 'year',
    'unit': '-',
}

output_s = {
    'node_loc': 'South',
    'node_dest': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'time_dest': 'year',
    'unit': '-',
}


#primary to secondary for hydro_ppl

s_hydro_out = {"hydro_2": 1.,
           "hydro_11": 1.,
}

for h_plant, val in s_hydro_out.items():
    h_plant_out_s = make_df(output_s, technology= h_plant, commodity= 'electricity', 
                   level='secondary', value=val, unit="GWa")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_s['year_act'] < h_plant_out_s['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s = h_plant_out_s.loc[condition]
    scenario.add_par('output', h_plant_out_s)

s_hydro_out_2 = {"hydro_2": 431.4,
                  "hydro_11": 457.4,
                  }

    
for h_plant, val in s_hydro_out_2.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_out_s_2 = make_df(output_s, technology= h_plant, commodity= wat, 
                   level='secondary', value=val, unit="m^3/a")
    
    # Removing extra years based on lifetime 
    condition = h_plant_out_s_2['year_act'] < h_plant_out_s_2['year_vtg'] + lifetimes[h_plant] 
    h_plant_out_s_2 = h_plant_out_s_2.loc[condition]
    scenario.add_par('output', h_plant_out_s_2)
    
s_hydro_in = {"hydro_2": 431.4,
           "hydro_11": 457.4,
}

for h_plant, val in s_hydro_in.items():
    wat = 'water_' + h_plant.split('hydro_')[1]  
    h_plant_in_s = make_df(input_s, technology= h_plant, commodity= wat, 
                   level='primary', value=1, unit="m^3/a")
    # Removing extra years based on lifetime 
    condition = h_plant_in_s['year_act'] < h_plant_in_s['year_vtg'] + lifetimes[h_plant] 
    h_plant_in_s = h_plant_in_s.loc[condition]
    scenario.add_par('input', h_plant_in_s)
    
for river in south_res:
    riv = 'water_' + river.split('river')[1]  
    river_out_s = make_df(output_s, technology= river, commodity= riv, 
                   level='primary', value=val, unit="m^3/a")
    # Removing extra years based on lifetime 
    condition = river_out_s['year_act'] < river_out_s['year_vtg'] + lifetimes[river] 
    river_out_s = river_out_s.loc[condition]
    scenario.add_par('output', river_out_s)

# secondary to final to water_supply

s_water_out = {"water_supply_2": 431.4,
                "water_supply_11": 457.4,
              }

for w_supply, val in s_water_out.items():
    wat = 'water_' + w_supply.split('water_supply_')[1] 
    w_supply_out_s = make_df(output_s, technology= w_supply, commodity= wat, 
                   level='final', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_out_s['year_act'] < w_supply_out_s['year_vtg'] + lifetimes[w_supply] 
    w_supply_out_s = w_supply_out_s.loc[condition] 

    # Removing extra years based on lifetime
    condition = w_supply_out_s['year_act'] < w_supply_out_s['year_vtg'] + lifetimes[w_supply]
    w_supply_out_s = w_supply_out_s.loc[condition]

    scenario.add_par('output', w_supply_out_s)

se_water_in = {"water_supply_2": 431.4,
                "water_supply_11": 457.4,
              }
    
for w_supply, val in se_water_in.items():
    wat = 'water_' + w_supply.split('water_supply_')[1]  
    w_supply_in_s = make_df(input_s, technology= w_supply, commodity= wat, 
                   level='secondary', value= val, unit="m^3/a")

    # Removing extra years based on lifetime 
    condition = w_supply_in_s['year_act'] < w_supply_in_s['year_vtg'] + lifetimes[w_supply] 

    # Removing extra years based on lifetime
    condition = w_supply_in_s['year_act'] < w_supply_in_s['year_vtg'] + lifetimes[w_supply]

    w_supply_in_s = w_supply_in_s.loc[condition]
    scenario.add_par('input', w_supply_in_s)

#secondary to useful e_tecs

for tech in plants:
     tech_out_s = make_df(output_s, technology=tech, commodity='electricity', 
                   level='secondary', value=1., unit="GWa")
     # Removing extra years based on lifetime 
     condition = tech_out_s['year_act'] < tech_out_s['year_vtg'] + lifetimes[tech] 
     tech_out_s = tech_out_s.loc[condition]
     scenario.add_par('output', tech_out_s)
    
base_technical_lifetime_s = {
    'node_loc': 'South',
    'year_vtg': horizon,
    'unit': 'y',
}


for tec, val in lifetimes.items():
    df_s = make_df(base_technical_lifetime_s, technology=tec, value=val)
    scenario.add_par('technical_lifetime', df_s)

base_capacity_factor_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'time': 'year',
    'unit': '-',
}

capacity_factor = {
    "hydro_2": 0.8,#EPE 
    "hydro_11": 0.8,#EPE 
    "bio_ppl": 0.33, #EPE
    "gas_ppl": 0.75,#EPE 56% of gas_ppl are combined cycle
    "wind_ppl_on": 0.4,#EPE 0.4 in South and Southeast and 0.47 in North and Northeast
    "wind_ppl_off": 0.43,
    "coal_ppl": 0.7,#EPE
    "nuc_ppl": 0.85, #EPE - eff 33%
    "solar_pv_ppl":0.3,
    "oil_ppl": 0.75, #EPE
    "water_supply_2": 0.9, 
    "water_supply_11": 0.9,
    "grid4": 0.5,
    "grid_s": 0.7,
}

for tec, val in capacity_factor.items():
    df = make_df(base_capacity_factor_s, technology=tec, value=val)
    # Removing extra years based on lifetime 
    condition = df['year_act'] < df['year_vtg'] + lifetimes[tec] 
    df = df.loc[condition] 
    scenario.add_par('capacity_factor', df)
    
base_capacity_s = {
    'year_vtg': [2020],
    'time': 'year',
    'node_loc': 'South',
    'unit': 'GW',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]
installed_capacity = 23.27 
thermal_capacity = 4.22 
transmission_capacity = 98.514
base_cap = {
    "hydro_2": 6.9/10,
    "hydro_11": 7.3/10,
    "bio_ppl": thermal_capacity*0.38/10,  
    "gas_ppl": thermal_capacity*0.34/10,
    "wind_ppl_on": 2.02/10, 
    "wind_ppl_off": 0.0001/10, 
    "coal_ppl": thermal_capacity*0.08/10, 
    "nuc_ppl": 0./10, 
    "solar_pv_ppl": 0.04,
    "oil_ppl": thermal_capacity*0.2/10,
    "grid4": transmission_capacity/10,
    "grid_s": transmission_capacity/10,
   
}

for tec, val in base_cap.items():
    df = make_df(base_capacity_s, technology=tec, value=val, unit= 'GW')
    scenario.add_par('historical_new_capacity', df) #fixed_capacity or fixed_new_capacity?
    
river_capacity_s = {
    'year_vtg': [2020],
    'time': 'year',
    'node_loc': 'South',
    'unit': 'm^3/a',
}

#base capacity [GW] of the BES in 2019 according to ONS historical operation for each subsystem [North, Northeast, SE/MW, South]

base_cap = {
     "water_supply_2": 28000,
    "water_supply_11": 26000,
}

for tec, val in base_cap.items():
    df = make_df(river_capacity_s, technology=tec, value=val, unit= 'm^3/a')
    scenario.add_par('historical_new_capacity', df)   
    
# %% Adding costs

base_inv_cost_s = {
    'node_loc': 'South',
    'year_vtg': horizon,
    'unit': 'USD/GW',
}

# in $ / kW (specific investment cost) dollar price in 2015 R$ 3,87 source: https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-227/topico-456/NT%20PR%20007-2018%20Premissas%20e%20Custos%20Oferta%20de%20Energia%20El%C3%A9trica.pdf
costs = {
    "hydro_2": 1352.*1E6,#EPE mean value for UHE
    "hydro_11": 1352.*1E6,
    "bio_ppl": 1200.*1E6,#EPE 
    "gas_ppl": 900*1E6, #EPE mean value
    "wind_ppl_on": 1200*1E6,#EPE mean value
    "wind_ppl_off": 230*1E6,#EPE mean value
    "coal_ppl": 2500*1E6, #EPE
    "nuc_ppl": 5000*1E6,#EPE
    "solar_pv_ppl":1100*1E6, #min value in EPE, max value is 1350
    "oil_ppl": 1100*1E6,
    'grid4':  1000*1E6,
    "river2": 0.01, 
    "river11": 0.01,
    "water_supply_2": 0.01*1E6, 
    "water_supply_11": 0.01*1E6,
    'grid_s': 462*1E6,
}

for tec, val in costs.items():
    df = make_df(base_inv_cost_s, technology=tec, value=val)
    scenario.add_par('inv_cost', df)

base_fix_cost_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'unit': 'USD/GW',
}

#fix cost divided by 3.9 are in reais and it is divided by Cotação média do dólar (US$) em dez/2015: R$ 3,8729 (the same used in the EPE NOTA TÉCNICA PR 07/18)

costs = {
    "hydro_2": 50/3.9*1E6,#EPE
    "hydro_11": 50/3.9*1E6,#EPE
    "bio_ppl": 90/3.9*1E6, #EPE
    "gas_ppl": 220*1E6,#EPE
    "wind_ppl_on": 100/3.9*1E6,#EPE
    "wind_ppl_off": 100/3.9*1E6,#EPE
    "coal_ppl": 100*1E6,#EPE
    "nuc_ppl": 110*1E6, #EPE
    "solar_pv_ppl":20/3.87*1E6, #EPE
    "oil_ppl": 22*1E6,
    'grid4':  36*1E6,
    'grid_s': 36*1E6,
}

for tec, val in costs.items():
    df = make_df(base_fix_cost_s, technology=tec, value=val)
    scenario.add_par('fix_cost', df)

### Adding variable cost = fuel cost to thermal power plants

var_cost_s = {
    'node_loc': 'South',
    'year_vtg': vintage_years,
    'year_act': act_years,
    'mode': 'M1',
    'time': 'year',
    'unit': 'USD/GWa',
}

costs = {
    "gas_ppl": 25*1E6, #EPE mean value
    "coal_ppl": 30*1E6, #EPE
    "oil_ppl": 35*1E6,
}

for tec, val in costs.items():
    df = make_df(var_cost_s, technology=tec, value=val)
    scenario.add_par('var_cost', df)


# %% Acitvity and Capacity
### 4.1) South base and growth

base_activity_s1 = {
    'node_loc': 'South',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

base_activity_s2 = {
    'node_loc': 'South',
    'year_act': history,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

thermal_act = 1.22
#old activity based on 2019 BEN
old_activity = {
    "hydro_2": 0.5*6.9,
    "hydro_11": 0.5*7.3,
    "bio_ppl": 0.1,  
    "gas_ppl": 0.001,
    "wind_ppl_on": 0.7, 
    "wind_ppl_off": 0.0001, 
    "coal_ppl": 0.8, 
    "nuc_ppl": 0.0, 
    "solar_pv_ppl": 0.01,
    "oil_ppl": 0.05,
}

for tec, val in old_activity.items():
    df = make_df(base_activity_s1, technology=tec, value=val)
    scenario.add_par('historical_activity', df)
    df = make_df(base_activity_s2, technology=tec, value=val)
    scenario.add_par('historical_activity', df)

    
# base_growth_s = {
#     'node_loc': 'South',
#     'year_act': horizon,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "bio_ppl": 0.05, 
#     "wind_ppl_on": 0.2, 
#     "wind_ppl_off": 0.2, 
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.02,
#     "coal_ppl": 0.0,
#     "oil_ppl": 0.0,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_s, technology=tec, value=val) 
#     scenario.add_par('growth_activity_up', df)

# growth_technologies = {
#     "bio_ppl": -0.05, 
#     "gas_ppl": -0.05,
#     "wind_ppl": 0.,
#     "nuc_ppl": -0.1,
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(base_growth_s, technology=tec, value=val) 
#     scenario.add_par('growth_activity_lo', df)
    
# cap_growth_s = {
#     'node_loc': 'South',
#     'year_vtg': history,
#     'time': 'year',
#     'unit': '-',
# }

# growth_technologies = {
#     "hydro_2": 0.0, 
#     "hydro_11": 0.0, 
#     "bio_ppl": 0.1, 
#     "wind_ppl_on": 0.2,
#     "wind_ppl_off": 0.05, 
#     "solar_pv_ppl":0.2,
#     'gas_ppl': 0.05,
#     "coal_ppl": 0.05,
#     "oil_ppl":0.05,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_s, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_up', df)

# growth_technologies = {
#     "coal_ppl": -0.1,
#     "solar_pv_ppl":0.0,
#     "oil_ppl":-0.1,
# }

# for tec, val in growth_technologies.items():
#     df = make_df(cap_growth_s, technology=tec, value=val) 
#     scenario.add_par('growth_new_capacity_lo', df)

## Bound activity

new_activity_s = { "hydro_2": 6.9,
                  "hydro_11": 7.3,
                   }

base_act = {
    'node_loc': 'South',
    'year_act': horizon,
    'mode': 'M1',
    'time': 'year',
    'unit': 'GWa',
}

for tec, val in new_activity_s.items():
    df = make_df(base_act, technology=tec, value=val)
    scenario.add_par('bound_total_capacity_up', df)



# %% solving the model

## Commit the datastructure and solve the model

#from message_ix import log

#log.info('version number prior to commit: {}'.format(scenario.version))

scenario.commit(comment='Brazilian_base')

#log.info('version number prior committing to the database: {}'.format(scenario.version))

scenario.solve()
scenario.var('OBJ')['lvl']
scenario.set_as_default()
scenario.version
#scenario.to_excel('BES_baseline_new.xlsx')

# %% Plotting Results

#import pyam
from ixmp.reporting import configure
import pyam
from message_ix.reporting import Reporter
#import os
import matplotlib.pyplot as plt
configure(units={'replace': {'-': 'GWa'}})

rep = Reporter.from_scenario(scenario)

# plotting years
plotyrs = [x for x in set(scenario.set('year')) if x >= scenario.firstmodelyear]

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
rename = {'bio_ppl': 'biomass',
          'coal_ppl': 'coal',
          'gas_ppl': 'natural gas',
          'oil_ppl': 'diesel',
          'solar_pv_ppl': 'solar',
          'wind_ppl_on': 'wind_on',
          'wind_ppl_off': 'wind_off',
          'nuc_ppl': 'nuclear',
          'turb_sphs_4': 'sphs_norte',
          'turb_sphs_8': 'sphs_belo_monte',
          'turb_sphs_9': 'sphs_amazonas',
          'hydro_4': 'hydro_norte',
          'hydro_8': 'hydro_sul',
          'hydro_9': 'hydro_iguaçu',
          }
#elec.plot.bar(stacked=True)
ax = plt.gca()
h, lgs = ax.get_legend_handles_labels()
ax.legend(labels=[rename[x.split("secondary|")[1]] for x in lgs], bbox_to_anchor=(1.04,1), loc="upper left")
plt.tight_layout()
plt.ylabel("GWa")
plt.show()

### Northeast
elec = elec_gen.filter(region=['Northeast'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
rename = {'bio_ppl': 'biomass',
          'coal_ppl': 'coal',
          'gas_ppl': 'natural gas',
          'oil_ppl': 'diesel',
          'solar_pv_ppl': 'solar',
          'wind_ppl_on': 'wind_on',
          'wind_ppl_off': 'wind_off',
          'nuc_ppl': 'nuclear',
          'hydro_3': 'hydro_northeast',
          }
#elec.plot.bar(stacked=True)
ax = plt.gca()
h, lgs = ax.get_legend_handles_labels()
ax.legend(labels=[rename[x.split("secondary|")[1]] for x in lgs], bbox_to_anchor=(1.04,1), loc="upper left")
plt.tight_layout()
plt.ylabel("GWa")
plt.show()

### Southeast

elec = elec_gen.filter(region=['Southeast'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
rename = {'bio_ppl': 'biomass',
          'coal_ppl': 'coal',
          'gas_ppl': 'natural gas',
          'oil_ppl': 'diesel',
          'solar_pv_ppl': 'solar',
          'wind_ppl_on': 'wind_on',
          'wind_ppl_off': 'wind_off',
          'nuc_ppl': 'nuclear',
          'turb_sphs_1': 'sphs_sudeste',
          'turb_sphs_5': 'sphs_itaipu',
          'turb_sphs_6': 'sphs_madeira',
          'turb_sphs_7': 'sphs_teles_pires',
          'turb_sphs_10': 'sphs_parana',
          'turb_sphs_12': 'sphs_paranapanema',
          'hydro_1': 'hydro_sudeste',
          'hydro_5': 'hydro_itaipu',
          'hydro_6': 'hydro_madeira',
          'hydro_7': 'hydro_teles_pires',
          'hydro_10': 'hydro_parana',
          'hydro_12': 'hydro_paranapanema',
          }
#elec.plot.bar(stacked=True)
ax = plt.gca()
h, lgs = ax.get_legend_handles_labels()
ax.legend(labels=[rename[x.split("secondary|")[1]] for x in lgs], bbox_to_anchor=(1.04,1), loc="upper left")
plt.tight_layout()
plt.ylabel("GWa")
plt.show()

### South

elec = elec_gen.filter(region=['South'], variable='Electricity Generation|secondary|*', year=plotyrs)
elec.plot.bar(stacked=True)
rename = {'bio_ppl': 'biomass',
          'coal_ppl': 'coal',
          'gas_ppl': 'natural gas',
          'oil_ppl': 'diesel',
          'solar_pv_ppl': 'solar',
          'wind_ppl_on': 'wind_on',
          'wind_ppl_off': 'wind_off',
          'nuc_ppl': 'nuclear',
          'turb_sphs_2': 'sphs_sul',
          'turb_sphs_11': 'sphs_iguaçu',
          'hydro_2': 'hydro_sul',
          'hydro_11': 'hydro_iguaçu',
          }
#elec.plot.bar(stacked=True)
ax = plt.gca()
h, lgs = ax.get_legend_handles_labels()
ax.legend(labels=[rename[x.split("secondary|")[1]] for x in lgs], bbox_to_anchor=(1.04,1), loc="upper left")
plt.tight_layout()
plt.ylabel("GWa")
plt.show()

#### new pltting

from pyam.plotting import OUTSIDE_LEGEND

elec = elec_gen.filter(variable='Electricity Generation|secondary|hydro*', year=plotyrs)
elec.plot(legend=OUTSIDE_LEGEND['bottom'])
plt.ylabel("GWa")

#mp.close_db()



      
