import networkx as nx
import numpy as np
import pickle
import json
import ast
import time
import matplotlib.pyplot as plt


basecost_Unit = [15, 100, 1100, 12000, 130000, 1.4e6, 20e6, 330e6]
baseproduction = [0.1, 1, 8, 47, 260, 1400, 7800, 44000]


def SaveRun(text):
    f = open("runs", "a+")
    f.write(text)


def UpgradeCost(currentState, ident):
    return np.ceil(
        basecost_Unit[ident]
        * (1.15 ** (currentState[ident] + 1) - 1.15 ** currentState[ident])
        / 0.15
    )


def ProductionRate(sourceState):
    pr = 0
    for i in range(len(baseproduction)):
        pr += baseproduction[i] * sourceState[i]
    return float(pr)


def UpgradePossible(currentState, ident):
    return True


def Weight(cost, PR):
    return cost / PR


def AddNode(G, state, oldCost, newCost, PR):
    G.add_node(str(state), DoSuccessors=True, allTimeBaked=int(oldCost + newCost))


def AddNodesAndEdges(G, state, newState, i, upperLimit):
    PR = ProductionRate(state)
    oldCost = G.nodes[str(state)]["allTimeBaked"]
    newCost = UpgradeCost(state, i)
    weight = Weight(newCost, PR)
    oldShortestT = np.round(G.nodes[str(state)]["shortestTime"], 10)
    newShortestT = np.round(oldShortestT + weight, 10)
    if weight < (1e9 - (oldCost + newCost)) / PR and weight < upperLimit:
        AddNode(G, newState, oldCost, newCost, PR)
        if G.nodes[str(newState)].get("shortestTime"):
            if G.nodes[str(newState)]["shortestTime"] > newShortestT:
                G.nodes[str(newState)]["shortestTime"] = newShortestT
                G.remove_edge(*list(G.in_edges(str(newState)))[0])
                G.add_edge(str(state), str(newState), weight=weight)
        else:
            G.nodes[str(newState)]["shortestTime"] = newShortestT
            G.add_edge(str(state), str(newState), weight=weight)
        timeUntilEnd = G.nodes[str(newState)]["shortestTime"] + np.round(
            (1e9 - (oldCost + newCost)) / PR, 10
        )
        if timeUntilEnd < G.nodes["end"]["shortestTime"]:
            G.nodes["end"]["shortestTime"] = timeUntilEnd
            G.remove_edge(*list(G.in_edges("end"))[0])
            G.add_edge(str(newState), "end", weight=(1e9 - (oldCost + newCost)) / PR)


def AddSuccessors(G, state, upperLimit):
    for i in range(len(state)):
        newState = list(state)
        if UpgradePossible(state, i):
            newState[i] = newState[i] + 1
            AddNodesAndEdges(G, state, newState, i, upperLimit)
    G.nodes[str(state)].pop("DoSuccessors")
    G.nodes[str(state)].pop("allTimeBaked")
    G.nodes[str(state)].pop("shortestTime")


def killOrLive(G, upperLimit):
    for name in list(G.nodes):
        if G.nodes[name].get("DoSuccessors"):
            if G.nodes[name]["shortestTime"] > upperLimit:
                G.remove_node(name)
            else:
                AddSuccessors(G, ast.literal_eval(name), upperLimit)


def killDeadEnd(G):
    counter = 10000
    while counter >= 9999:
        counter = 0
        for name in list(G.nodes):
            if not G.nodes[name].get("DoSuccessors") and name != "end":
                if G.out_degree[name] == 0:
                    G.remove_node(name)
                    counter += 1
        print("Dead ends killed:", counter)


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
    zero = [1] + [0] * 7
    G.add_node(str(zero), DoSuccessors=True, allTimeBaked=15, shortestTime=0)
    G.add_node("end", shortestTime=1e11)
    G.add_edge(str(zero), "end", weight=1e10)
    upperLimit = 12.5 * 60 * 60
    numberNodes = [2]
    timesList = []
    
    # record by simulation 41.5 min with range 90, this is a problem

    start = time.time()
    for i in range(iterations):
        bestTime = G.nodes["end"]["shortestTime"]
        start_loop = time.time()

        killOrLive(G, upperLimit)

        killDeadEnd(G)

        print("Iteration", i, "Nodes:", len(G.nodes))
        print("Time:", G.nodes["end"]["shortestTime"] / 60 /60, "hours")
        numberNodes.append(len(G.nodes))
        if G.nodes["end"]["shortestTime"] / 60 / 60 < 16:
            timesList.append(G.nodes["end"]["shortestTime"] / 60 / 60)
        plotting(numberNodes, timesList)
            
        shortest_path_len = pathLen(G, zero)
        shortest_path = fullPath(G, zero)
        printIntermediateSolution(shortest_path_len, shortest_path)
        end_loop = time.time()
        print(end_loop - start_loop)
        if bestTime == G.nodes["end"]["shortestTime"]:
            print("It doesn't get better!")
            break
    end = time.time()
    print("Full time:", end - start)

    output = defineOutput(iterations, G, start, shortest_path_len, shortest_path, end)

    print(output)
    SaveRun(output)
    print("\a")
    input("Press Enter to continue...")


if __name__ == "__main__":
    main(100)
