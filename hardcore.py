import networkx as nx
import numpy as np
import pickle
import json
import ast
import time

G = nx.DiGraph()


basecost_Unit = [15, 100, 1100, 12000, 130000, 1400000, 20000000,330000000]
baseproduction = [0.1, 1, 8, 47, 260, 1400,7800,44000]


def UpgradeCost(currentState, ident):
    return np.ceil(basecost_Unit[ident]*(1.15**(currentState[ident]+1)-1.15**currentState[ident])/0.15)


def ProductionRate(sourceState):
    pr = 0
    for i in range(len(baseproduction)):
        pr += baseproduction[i]*sourceState[i]
    return float(pr)


def Weight(cost, PR):
    return cost/PR


def AddNode(G, state,  oldCost,newCost, PR):
    G.add_node(str(state), DoSuccessors = True, allTimeBaked=int(oldCost+newCost))
    G.add_edge(str(state), 'end', weight = (1e6-(oldCost+newCost))/PR)


def AddNodesAndEdges(G,state, newState, i, upperLimit):
    PR = ProductionRate(state)
    oldCost = G.nodes[str(state)]["allTimeBaked"]
    newCost = UpgradeCost(state, i)
    weight = Weight(newCost, PR)
    if weight<(1e6-(oldCost+newCost))/PR and weight<upperLimit:
        AddNode(G, newState, oldCost ,newCost, PR)
        G.add_edge(str(state), str(newState), weight = weight)
        

def AddSuccessors(G, state, upperLimit):
    for i in range(len(state)):
        newState = list(state)
        newState[i] = newState[i]+1
        AddNodesAndEdges(G, state, newState, i, upperLimit)
    G.nodes[str(state)].pop('DoSuccessors')
    G.nodes[str(state)].pop('allTimeBaked')

def main():
    zero = [1]+[0]*9
    G.add_node(str(zero), state=zero, DoSuccessors = True, allTimeBaked=15)
    G.add_node('end' )
    upperLimit= 42*60 
    #record by simulation 49 min with range 100 and no grandmas
    start = time.time()
    for i in range(2):
        start_loop = time.time()
        for name in list(G.nodes):
            if G.nodes[name].get('DoSuccessors'):
                AddSuccessors(G, ast.literal_eval(name), upperLimit)
        print('Iteration', i, 'Nodes:', len(G.nodes))
        print('Iteration', i, 'Edges:', len(G.edges))
        end_loop = time.time()
        print(end_loop-start_loop)
    end = time.time()
    print('Full time:', end-start)
    shortest_path = nx.shortest_path(G, source=str(zero), target='end', weight ='weight', method='dijkstra') #'bellman-ford', 'dijkstra'
    print(shortest_path)
    print(len(shortest_path))
    sum = 0
    for i in range(len(shortest_path)-1):
        sum += G.edges[shortest_path[i],shortest_path[i+1]]['weight']
    print(sum/60)



if __name__ == "__main__":
    main()
