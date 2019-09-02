import networkx as nx
import numpy as np
import pickle
import json
import ast
import time

G = nx.DiGraph()


basecost_Unit = [15, 100, 1100, 12000, 130000]
cost_Upgrade = [[100, 500, 12000, 100000], [1000, 5000, 20000],
                [11000, 55000, 550000], [120000, 600000], [1300000]]
prerequisites_Upgrade = [[1, 1, 10, 25], [1, 5, 25], [1, 5, 25], [1, 5], [1]]
effect_Upgrade = [[1, 2, 2, 2, 0.1], [
    1, 2, 2, 2], [1, 2, 2, 2], [1, 2, 2], [1, 2]]

baseproduction = [0.1, 1, 8, 47, 260]


def SaveRun(text):
    f = open('runs', 'a+')
    f.write(text)


def UpgradeCost(currentState, ident):
    if ident < 5:
        return np.ceil(basecost_Unit[ident]*(1.15**(currentState[ident]+1)-1.15**currentState[ident])/0.15)
    else:
        return cost_Upgrade[ident-5][currentState[ident]]


def ProductionRate(sourceState):
    pr = 0
    for i in range(len(baseproduction)):
        mult = 1
        if i == 0 and sourceState[i+5] == 4:
            sum = 0
            for k in range(1, 4):
                sum += sourceState[k]
            mult = 8+effect_Upgrade[i][sourceState[i+5]]*sum
        else:
            for j in range(sourceState[i+5]):
                mult *= effect_Upgrade[i][j+1]
            pr += baseproduction[i]*sourceState[i]*mult
    return float(pr)


def UpgradePossible(currentState, ident):
    if ident == 0 and currentState[ident] < 30:
        return True
    elif ident == 1 and currentState[ident] < 30:
        return True
    elif ident == 2 and currentState[ident] < 30:
        return True
    elif ident == 3 and currentState[ident] < 20:
        return True
    elif ident == 4 and currentState[ident] < 2:
        return True
    elif ident < 5:
        return False
    else:
        if (len(prerequisites_Upgrade[ident-5]) > currentState[ident]) and (prerequisites_Upgrade[ident-5][currentState[ident]] <= currentState[ident-5]):
            return True
        else:
            return False


def Weight(cost, PR):
    return cost/PR


def AddNode(G, state,  oldCost, newCost, PR):
    G.add_node(str(state), DoSuccessors=True,
               allTimeBaked=int(oldCost+newCost))
    G.add_edge(str(state), 'end', weight=(1e6-(oldCost+newCost))/PR)


def AddNodesAndEdges(G, state, newState, i, upperLimit):
    PR = ProductionRate(state)
    oldCost = G.nodes[str(state)]["allTimeBaked"]
    newCost = UpgradeCost(state, i)
    weight = Weight(newCost, PR)
    oldShortestT= G.nodes[str(state)]['shortestTime']
    newShortestT= oldShortestT + weight
    if weight < (1e6-(oldCost+newCost))/PR and weight < upperLimit:
        AddNode(G, newState, oldCost, newCost, PR)
        G.add_edge(str(state), str(newState), weight=weight)
        if G.nodes[str(newState)].get('shortestTime'):
            if G.nodes[str(newState)]['shortestTime'] > newShortestT:
                G.nodes[str(newState)]['shortestTime'] = newShortestT
        else:
            G.nodes[str(newState)]['shortestTime'] = newShortestT


def AddSuccessors(G, state, upperLimit):
    for i in range(len(state)):
        newState = list(state)
        if UpgradePossible(state, i):
            newState[i] = newState[i]+1
            AddNodesAndEdges(G, state, newState, i, upperLimit)
    G.nodes[str(state)].pop('DoSuccessors')
    G.nodes[str(state)].pop('allTimeBaked')
    G.nodes[str(state)].pop('shortestTime')


def main(iterations):
    zero = [1]+[0]*9
    G.add_node(str(zero), DoSuccessors=True, allTimeBaked=15, shortestTime= 0)
    G.add_node('end')
    upperLimit = 42*60
    # record by simulation 49 min with range 100 and no grandmas
    start = time.time()
    for i in range(iterations):
        start_loop = time.time()
        for name in list(G.nodes):
            if G.nodes[name].get('DoSuccessors'):
                if G.nodes[name]['shortestTime'] > upperLimit:
                    G.remove_node(name)
                else:
                    AddSuccessors(G, ast.literal_eval(name), upperLimit)
        print('1. Did the new nodes')
        for name in list(G.nodes):
            if not G.nodes[name].get('DoSuccessors') and not name== 'end':
                if G.out_degree[name] == 1:
                    G.remove_node(name)
        print('3. Killed the useless nodes')

        print('Iteration', i, 'Nodes:', len(G.nodes))
        print('Iteration', i, 'Edges:', len(G.edges))
        end_loop = time.time()
        print(end_loop-start_loop)
    end = time.time()
    print('Full time:', end-start)
    shortest_path = nx.dijkstra_path(G, source=str(zero), target='end', weight='weight')  # 'bellman-ford', 'dijkstra'
    shortest_path_len = nx.dijkstra_path_length(G, source=str(zero), target='end', weight='weight')

    output = 'Steps: '+str(iterations)+',\nestimated time: ' + str(shortest_path_len/60) + ' min,\nprocessing time: ' + str(
        end-start)+' sec,\nnodes: ' + str(len(G.nodes))+',\nedges: ' + str(len(G.edges))+',\npath: ' + str(shortest_path)+'\n\n'

    print(output)
    SaveRun(output)
    print('\a')


if __name__ == "__main__":
    main(100)
