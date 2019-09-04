import random
import matplotlib.pyplot as plt
import copy

def picknumber(x, y):
    return random.randint(x, y)


def safelist (buildings_1,upgrades_1):
    buildings_1, upgrades_1 = check_possibility(buildings_1, upgrades_1)
    if check_possibility(buildings_1, upgrades_1) == False #Wenn check_possibility einen negativen Wert ausspuckt soll die building Liste auf den ursprünglichen Wert springen
        buildings_1 = copy.copy(buildings_0)
        upgrades_1 = copy.copy(upgrades_0)
    else
        buildings_0 = copy.copy(buildings_1) #Wenn check_possibility einen positiven Wert ausspuckt soll sich die building Liste aktualisieren 
        upgrades_0 = copy.copy(updates_1)


def propose_purchase(buildings_1, upgrades_1):
    randomnumber = picknumber(0, 16)
    buildings_1, upgrades_1 = safelist (buildings_1,upgrades_1)
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
        buildings_1, upgrades_1, buildings_0, upgrades_0, randomnumber = propose_purchase(buildings_1, upgrades_1)
        print (buildings_0, upgrades_0, "buildings_0")
        if randomnumber<5:
            return buildings_1, upgrades_1
        elif randomnumber<9 and buildings_1[0]>0:
            return buildings_1, upgrades_1
        elif randomnumber<12 and buildings_1[1]>0:
            return buildings_1, upgrades_1
        elif randomnumber<15 and buildings_1[2]>0:
            return buildings_1, upgrades_1
        elif randomnumber<17 and buildings_1[3]>0:
            return buildings_1, upgrades_1
        else:
            return False #check possibility soll false ausspucken wenn es nicht geht
            



buildings = [1, 0, 0, 0, 0]  # Cursor, Grandma, Farm, Mine, Factory
# Cursor, Grandma, Farm, Mine, Factory
upgrades = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0]]

for i in range(10):
    print(i)
    print(buildings, upgrades)

    buildings,upgrades=check_possibility(buildings,upgrades)