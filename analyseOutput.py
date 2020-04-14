import ast
import neverclick as m
import datetime

basecost_Unit = [15, 100, 1100, 12000, 130000]
cost_Upgrade = [
    [100, 500, 12000, 100000],
    [1000, 5000, 20000],
    [11000, 55000, 550000],
    [120000, 600000],
    [1300000],
]
prerequisites_Upgrade = [[1, 1, 10, 25], [1, 5, 25], [1, 5, 25], [1, 5], [1]]
effect_Upgrade = [[1, 2, 2, 2, 0.1], [1, 2, 2, 2], [1, 2, 2, 2], [1, 2, 2], [1, 2]]

baseproduction = [0.1, 1, 8, 47, 260]


def OpenPath():
    f = open("path2", "r+")
    flist = ast.literal_eval(f.read())
    listList = []
    for string in flist:
        if string != "end":
            listList.append(ast.literal_eval(string))
    return listList


def getUpdateOrder(path):
    updates=[]
    for i in range(len(path) - 1):
        for j in range(len(path[i])):
            if path[i][j] != path[i + 1][j]:
                updates.append(j)
    return updates

def main():
    goal = 300
    path = OpenPath()
    updates = getUpdateOrder(path)
    sumUpgradeCosts = 0
    t = 0
    for i in range(len(updates)+1):
        print(path[i])
        if i == len(updates):
            upgradeCost = goal - sumUpgradeCosts
        else:
            upgradeCost =m.UpgradeCost(path[i], updates[i])
        productionRate = m.ProductionRate(path[i])
        sumUpgradeCosts += upgradeCost
        print('Productionrate',productionRate)
        print('Upgradecost',upgradeCost)
        t += upgradeCost/productionRate
        print(datetime.timedelta(seconds=t))
    print(sumUpgradeCosts, t/60)



if __name__ == "__main__":
    main()
