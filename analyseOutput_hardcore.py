import ast
import hardcore as m
import datetime

basecost_Unit = [15, 100, 1100, 12000, 130000, 1.4e6, 2e7, 3.3e8]
baseproduction = [0.1, 1, 8, 47, 260, 1400, 7800, 44000]

def OpenPath():
    f = open("path_hardcore", "r+")
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
    path = OpenPath()
    updates = getUpdateOrder(path)
    sumUpgradeCosts = 0
    t = 0
    for i in range(len(updates)+1):
        print(path[i])
        if i == len(updates):
            upgradeCost = 1e9 - sumUpgradeCosts
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
