import networkx as nx
import numpy as np
import ast
import time
import matplotlib.pyplot as plt


basecost_Unit = [15, 100, 1100, 12000, 130000]
cost_Upgrade = [
    [100, 500, 10000, 100000],
    [1000, 5000, 50000],
    [11000, 55000, 550000],
    [120000, 600000],
    [1300000],
]
prerequisites_Upgrade = [[1, 1, 10, 25], [1, 5, 25], [1, 5, 25], [1, 5], [1]]
effect_Upgrade = [[1, 2, 2, 2, 0.1], [1, 2, 2, 2], [1, 2, 2, 2], [1, 2, 2], [1, 2]]

baseproduction = [0.1, 1, 8, 47, 260]


def SaveRun(text):
    f = open("ergebnis", "r+")
    f.write(text)


def UpgradeCost(currentState, ident):
    if ident < 5:
        return np.ceil(
            basecost_Unit[ident]
            * (1.15 ** (currentState[ident] + 1) - 1.15 ** currentState[ident])
            / 0.15
        )
    elif ident == 10:
        return 55000
    elif ident == 11:
        return 600000
    else:
        return cost_Upgrade[ident - 5][currentState[ident]]


def ProductionRate(sourceState):
    pr = 0
    for i in range(len(baseproduction)):
        mult = 1
        if i == 1 and sourceState[10] == 1:
            mult *= 2
        if i == 1 and sourceState[11] == 1:
            mult *= 2
        if i == 2 and sourceState[10] == 1:
            mult += 0.01 * sourceState[1]
        if i == 3 and sourceState[11] == 1:
            mult += 0.01 * np.floor(sourceState[1] / 2)
        if i == 0 and sourceState[i + 5] == 4:
            print("KRASSES UPDATE")
            sum = 0
            for k in range(1, 4):
                sum += sourceState[k]
            mult = 8 + effect_Upgrade[i][sourceState[i + 5]] * sum
        else:
            for j in range(sourceState[i + 5] + 1):
                mult *= effect_Upgrade[i][j]
        pr += baseproduction[i] * sourceState[i] * mult
    return float(pr)


def UpgradePossible(currentState, ident):
    if ident == 0 and UpgradeCost(currentState, ident) < UpgradeCost(
        currentState, ident + 5
    ):
        return True
    elif ident == 1 and UpgradeCost(currentState, ident) < UpgradeCost(
        currentState, ident + 5
    ):
        return True
    elif ident == 2 and UpgradeCost(currentState, ident) < UpgradeCost(
        currentState, ident + 5
    ):
        return True
    elif ident == 3 and UpgradeCost(currentState, ident) < UpgradeCost(
        currentState, ident + 5
    ):
        return True
    elif ident == 4 and UpgradeCost(currentState, ident) < UpgradeCost(
        currentState, ident + 5
    ):
        return True
    elif ident < 5:
        return False
    elif ident < 10:
        if (len(prerequisites_Upgrade[ident - 5]) > currentState[ident] + 1) and (
            prerequisites_Upgrade[ident - 5][currentState[ident]]
            <= currentState[ident - 5]
        ):
            return True
        else:
            return False
    else:
        if (
            ident == 10
            and currentState[ident] == 0
            and currentState[1] > 0
            and currentState[2] > 14
        ):
            return True
        elif (
            ident == 11
            and currentState[ident] == 0
            and currentState[1] > 0
            and currentState[3] > 14
        ):
            return True
        else:
            return False


def Weight(cost, PR):
    return cost / PR


def AddNode(G, state, oldCost, newCost, PR):
    G.add_node(str(state), DoSuccessors=True, allTimeBaked=int(oldCost + newCost))


def AddNodesAndEdges(G, state, newState, i, upperLimit, goal):
    PR = ProductionRate(state)
    oldCost = G.nodes[str(state)]["allTimeBaked"]
    upCost = UpgradeCost(state, i)
    weight = Weight(upCost, PR)
    oldShortestT = np.round(G.nodes[str(state)]["shortestTime"], 10)
    newShortestT = np.round(oldShortestT + weight, 10)
    if weight < (goal - oldCost) / PR and weight < upperLimit:
        AddNode(G, newState, oldCost, upCost, PR)
        if G.nodes[str(newState)].get("shortestTime"):
            if G.nodes[str(newState)]["shortestTime"] > newShortestT:
                G.nodes[str(newState)]["shortestTime"] = newShortestT
                G.remove_edge(*list(G.in_edges(str(newState)))[0])
                G.add_edge(str(state), str(newState), weight=weight)
        else:
            G.nodes[str(newState)]["shortestTime"] = newShortestT
            G.add_edge(str(state), str(newState), weight=weight)
        timeUntilEnd = G.nodes[str(newState)]["shortestTime"] + np.round(
            (goal - (oldCost + upCost)) / PR, 10
        )
        if timeUntilEnd < G.nodes["end"]["shortestTime"]:
            G.nodes["end"]["shortestTime"] = timeUntilEnd
            G.remove_edge(*list(G.in_edges("end"))[0])
            G.add_edge(str(newState), "end", weight=(goal - (oldCost + upCost)) / PR)


def AddSuccessors(G, state, upperLimit, goal):
    for i in range(len(state)):
        newState = list(state)
        if UpgradePossible(state, i):
            newState[i] = newState[i] + 1
            AddNodesAndEdges(G, state, newState, i, upperLimit, goal)
    G.nodes[str(state)].pop("DoSuccessors")
    G.nodes[str(state)].pop("allTimeBaked")
    G.nodes[str(state)].pop("shortestTime")


def killOrLive(G, upperLimit, goal):
    for name in list(G.nodes):
        if G.nodes[name].get("DoSuccessors"):
            if G.nodes[name]["shortestTime"] > upperLimit:
                G.remove_node(name)
            else:
                AddSuccessors(G, ast.literal_eval(name), upperLimit, goal)


def killDeadEnd(G, givenHitList):
    counter = 0
    hitList = []
    print("Laenge der hitList", len(givenHitList))
    for name in list(givenHitList):
        if name in list(G.nodes):
            if not G.nodes[name].get("DoSuccessors") and name != "end":
                if G.out_degree[name] == 0:
                    hitList.extend(list(nx.ancestors(G, name)))
                    G.remove_node(name)
                    if name in hitList:
                        hitList.remove(name)
                    counter += 1
    print("Dead ends killed:", counter)
    hitList=list(set(hitList))
    if len(hitList) != 0:
        killDeadEnd(G, hitList)


def plotting(numberNodes, timesList):
    plt.ion()
    plt.subplot(211)
    plt.plot(numberNodes, "ro")
    plt.subplot(212)
    plt.plot(timesList, "bx")
    plt.show()
    plt.draw()
    plt.pause(0.001)


def fullPath(G, zero):
    return nx.dijkstra_path(G, source=str(zero), target="end", weight="weight")


def pathLen(G, zero):
    return nx.dijkstra_path_length(G, source=str(zero), target="end", weight="weight")


def defineOutput(iterations, G, start, shortest_path_len, shortest_path, end):
    return (
        "Steps: "
        + str(iterations)
        + ",\nestimated time: "
        + str(shortest_path_len / 60)
        + " min,\nprocessing time: "
        + str(end - start)
        + " sec,\nnodes: "
        + str(len(G.nodes))
        + ",\nedges: "
        + str(len(G.edges))
        + ",\npath: "
        + str(shortest_path)
        + "\n\n"
    )


def printIntermediateSolution(shortest_path_len, shortest_path):
    print(shortest_path_len / 60)
    print(shortest_path)
    # for state in shortest_path:
    #     if state != "end":
    #         print(state, ProductionRate(ast.literal_eval(state)))


def main(iterations):
    G = nx.DiGraph()
    zero = [1] + [0] * 11 #[5, 1] +[0]*10
    G.add_node(str(zero), DoSuccessors=True, allTimeBaked=15, shortestTime=0, testAncestry=True)
    G.add_node("end", shortestTime=1e8)
    G.add_edge(str(zero), "end", weight=1e7)
    upperLimit = 41.6 * 60
    numberNodes = [2]
    timesList = []
    goal = 1e6  # how many cookies should ba achieved all time?

    # record by simulation 41.5 min with range 90, this is a problem

    start = time.time()
    for i in range(iterations):
        bestTime = G.nodes["end"]["shortestTime"]
        start_loop = time.time()

        killOrLive(G, upperLimit, goal)
        
        killDeadEnd(G, G.nodes)

        print("Iteration", i, "Nodes:", len(G.nodes))
        print("Time:", G.nodes["end"]["shortestTime"] / 60, "minutes")
        numberNodes.append(len(G.nodes))
        if G.nodes["end"]["shortestTime"] / 60 < 150:
            timesList.append(G.nodes["end"]["shortestTime"] / 60)
        # plotting(numberNodes, timesList)

        shortest_path_len = pathLen(G, zero)
        shortest_path = fullPath(G, zero)
        printIntermediateSolution(shortest_path_len, shortest_path)
        end_loop = time.time()
        print(end_loop - start_loop)
        if bestTime == G.nodes["end"]["shortestTime"]:
            print("It doesn't get better!")
            break
        end = time.time()
        output = defineOutput(i, G, start, shortest_path_len, shortest_path, end)
        SaveRun(output)
    end = time.time()
    print("Full time:", end - start)

    print(output)
    SaveRun(output)
    print("\a")
    input("Press Enter to continue...")


if __name__ == "__main__":
    main(30)
