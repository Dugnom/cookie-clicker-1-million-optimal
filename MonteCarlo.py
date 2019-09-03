import random
import matplotlib.pyplot as plt


def picknumber(x, y):
    return random.randint(x, y)




def propose_purchase(buildings_0, upgrades_0):
    randomnumber = picknumber(0, 16)
    if randomnumber < 5:
        buildings_0[randomnumber] = buildings_0[randomnumber]+1
    elif randomnumber < 9:
        upgrades_0[0][randomnumber-5] = upgrades_0[0][randomnumber-5]+1
    elif randomnumber < 12:
        upgrades_0[1][randomnumber-9] = upgrades_0[1][randomnumber-9]+1
    elif randomnumber < 15:
        upgrades_0[2][randomnumber-12] = upgrades_0[2][randomnumber-12]+1
    elif randomnumber < 17:
        upgrades_0[3][randomnumber-15] = upgrades_0[3][randomnumber-15]+1
    else:
        print("error")

    return buildings_0, upgrades_0, randomnumber


def check_possibility(buildings_0, upgrades_0):
    notFound = True
    while notFound:
        buildings_1, upgrades_1, randomnumber = propose_purchase(buildings_0.copy(), upgrades_0.copy())
        if randomnumber<5:
            notFound =  False
        elif randomnumber<9:
            notFound =  False
        elif randomnumber<12 and buildings_0[1]>0:
            notFound =  False
        elif randomnumber<15 and buildings_0[2]>0:
            notFound =  False
        elif randomnumber<17 and buildings_0[3]>0:
            notFound =  False
        else:
            notFound =  True
    return buildings_1, upgrades_1

buildings = [1, 0, 0, 0, 0]  # Cursor, Grandma, Farm, Mine, Factory
# Cursor, Grandma, Farm, Mine, Factory
upgrades = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0]]

for i in range(10):
    print(i)
    print(buildings, upgrades)

    buildings,upgrades=check_possibility(buildings,upgrades)