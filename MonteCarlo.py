import random 
import matplotlib.pyplot as plt


def picknumber(x, y):
    return random.randint(x, y)


buildings = [1, 0, 0, 0, 0]  # Cursor, Grandma, Farm, Mine, Factory
# Cursor, Grandma, Farm, Mine, Factory
upgrades = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0]]


def propose_purchase(buildings, upgrades):
    randomnumber = picknumber(0, 16)
    if randomnumber <5:
        buildings[randomnumber]=buildings[randomnumber]+1
 
    else:
        if randomnumber <9:
            upgrades[0][randomnumber-5]=upgrades[0][randomnumber-5]+1
        elif randomnumber <12:
            upgrades[1][randomnumber-9]=upgrades[1][randomnumber-9]+1
        elif randomnumber <15:
            upgrades[2][randomnumber-12]=upgrades[2][randomnumber-12]+1
        elif randomnumber <17:
            upgrades[3][randomnumber-15]=upgrades[3][randomnumber-15]+1
        else:
            print("error")

    return buildings, upgrades






print(propose_purchase(buildings, upgrades))
