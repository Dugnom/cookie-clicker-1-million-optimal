import random


def picknumber(x, y):
    return random.randint(x, y)


buildings = [1, 0, 0, 0, 0]  # Cursor, Grandma, Farm, Mine, Factory
# Cursor, Grandma, Farm, Mine, Factory
upgrades = [[0, 0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0], []]


def propose_purchase(buildings, ugrades):
    randomnumber = picknumber(0, 16)
    if randomnumber <5:
        buildings[randomnumber]=buildings[randomnumber]+1
    return buildings


print(propose_purchase(buildings, upgrades))
