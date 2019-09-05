import random
import matplotlib.pyplot as plt
import copy
import numpy as np

#upgrade_conditions:
cursor_upgrade_conditions = [1,1,10,25]
grandma_upgrade_conditions = [1,5,25]
farm_upgrade_conditions = [1,5,25]
mine_upgrade_conditions = [1,5]

#building_base_prices:
building_base_price = [15,1e2,11e2,12e3,13e4]

#upgrade_prices
cursor_upgrade_prices = [100,500,1e4,1e5]
grandma_upgrade_prices = [1e3,5e3,5e4]
farm_upgrade_prices = [11e3, 55e3, 55e4]
mine_upgrade_prices = [12e4, 6e5]

#base_building_production_bonus
base_building_production_rate = [0.1,1,8,47,260]

#upgrade_effekt:
#always *2, only for cursor upgrade 4 +0.1 on all base productions

def picknumber(x, y):
    return random.randint(x, y)



def propose_purchase(buildings_1, upgrades_1):
    randomnumber = picknumber(0, 16)
    buildings_0 = copy.copy(buildings_1)
    upgrades_0 = copy.deepcopy(upgrades_1)
    if randomnumber < 5:
        buildings_1[randomnumber] = buildings_1[randomnumber]+1
    elif randomnumber < 9:
        upgrades_1[0][randomnumber-5] = upgrades_1[0][randomnumber-5]+1
    elif randomnumber < 12:
        upgrades_1[1][randomnumber-9] = upgrades_1[1][randomnumber-9]+1
    elif randomnumber < 15:
        upgrades_1[2][randomnumber-12] = upgrades_1[2][randomnumber-12]+1
    elif randomnumber < 17:
        upgrades_1[3][randomnumber-15] = upgrades_1[3][randomnumber-15]+1
    else:
        print("error")
    return buildings_1, upgrades_1, buildings_0, upgrades_0, randomnumber


def check_possibility(buildings_1, upgrades_1):
    x = True
    while x == True:
        buildings_1, upgrades_1, buildings_0, upgrades_0, randomnumber = propose_purchase(buildings_1, upgrades_1)
        if randomnumber<5:
            x = False
            return buildings_1, upgrades_1, randomnumber
        elif 4<randomnumber<9 and buildings_1[0]>0 and upgrades_1[0][randomnumber-5]<2 and buildings_0[0] >= cursor_upgrade_conditions[randomnumber-5]:
            x = False
            return buildings_1, upgrades_1, randomnumber
        elif 8<randomnumber<12 and buildings_1[1]>0 and upgrades_1[1][randomnumber-9]<2 and buildings_0[1] >= grandma_upgrade_conditions[randomnumber-9]:
            x = False
            return buildings_1, upgrades_1, randomnumber
        elif 11<randomnumber<15 and buildings_1[2]>0 and upgrades_1[2][randomnumber-12]<2 and buildings_0[2] >= farm_upgrade_conditions[randomnumber-12]:
            x = False
            return buildings_1, upgrades_1, randomnumber
        elif 14<randomnumber<17 and buildings_1[3]>0 and upgrades_1[3][randomnumber-15]<2 and buildings_0[3] >= mine_upgrade_conditions[randomnumber-15]:
            x = False
            return buildings_1, upgrades_1, randomnumber
        else:
            x = True
            
def check_current_costs(buildings_1, upgrades_1, upgradenumber):

    if upgradenumber<5:
        a = buildings_1[upgradenumber]-1 # current number of buildings 
        b = buildings_1[upgradenumber] # proposed number of buildings
        costs = (building_base_price[upgradenumber]*(1.15**(b)-1.15**(a)))/0.15
    elif 4<upgradenumber<9:
        a = upgrades_1[0][upgradenumber-5]-1 # current number of upgrades
        b = upgrades_1[0][upgradenumber-5] # proposed number of upgrades
        costs = (cursor_upgrade_prices[upgradenumber-5]*(1.15**(b)-1.15**(a)))/0.15
    elif 8<upgradenumber<12:
        a = upgrades_1[1][upgradenumber-9]-1 # current number of upgrades
        b = upgrades_1[1][upgradenumber-9] # proposed number of upgrades
        costs = (cursor_upgrade_prices[upgradenumber-9]*(1.15**(b)-1.15**(a)))/0.15
    elif 11<upgradenumber<15:
        a = upgrades_1[2][upgradenumber-12]-1 # current number of upgrades
        b = upgrades_1[2][upgradenumber-12] # proposed number of upgrades
        costs = (cursor_upgrade_prices[upgradenumber-12]*(1.15**(b)-1.15**(a)))/0.15
    elif 14<upgradenumber<17:
        a = upgrades_1[3][upgradenumber-15]-1 # current number of upgrades
        b = upgrades_1[3][upgradenumber-15] # proposed number of upgrades
        costs = (cursor_upgrade_prices[upgradenumber-14]*(1.15**(b)-1.15**(a)))/0.15
    return np.ceil(costs)

def production_rate(buildings, upgrades):

    production_cursor = (buildings[0]*base_building_production_rate[0]+upgrades[0][3]*0.1*(np.sum(buildings)-buildings[0])*2**(np.sum(upgrades[0])-upgrades[0][3])
    production_grandma = (buildings[1]*base_building_production_rate[1])*2(np.sum(upgrades[1]))
    production_farm =(buildings[2]*base_building_production_rate[2])*2(np.sum(upgrades[2]))
    production_mine =(buildings[3]*base_building_production_rate[3])*2(np.sum(upgrades[3]))
    production_factory = buildings[4]*base_building_production_rate[4]
    cookie_production_rate = production_cursor+production_grandma+production_farm+production_mine

    return cookie_production_rate #=cpr


def main():
    buildings = [1, 0, 0, 0, 0]  # Cursor, Grandma, Farm, Mine, Factory
    upgrades = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0]] # Cursor, Grandma, Farm, Mine, Factory
    
    print(buildings,upgrades)
    for i in range(100):
        #print(i)
        buildings,upgrades, randomnumber=check_possibility(buildings,upgrades)
        costs = check_current_costs(buildings,upgrades,randomnumber)
        cpr= production_rate(buildings,upgrades)
        print(buildings, upgrades, costs, cpr)
main()
