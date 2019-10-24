import networkx as nx
import numpy as np
import ast
import time
import psycopg2 as sql
import os


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
                mult *= effect_Upgrade[i][j]
            pr += baseproduction[i]*sourceState[i]*mult
    return float(pr)


def UpgradePossible(currentState, ident):
    if ident == 0 and currentState[ident] < 30 and UpgradeCost(currentState, ident) < UpgradeCost(currentState, ident+5):
        return True
    elif ident == 1 and currentState[ident] < 30 and UpgradeCost(currentState, ident) < UpgradeCost(currentState, ident+5):
        return True
    elif ident == 2 and currentState[ident] < 30 and UpgradeCost(currentState, ident) < UpgradeCost(currentState, ident+5):
        return True
    elif ident == 3 and currentState[ident] < 20 and UpgradeCost(currentState, ident) < UpgradeCost(currentState, ident+5):
        return True
    elif ident == 4 and currentState[ident] < 2 and UpgradeCost(currentState, ident) < UpgradeCost(currentState, ident+5):
        return True
    elif ident < 5:
        return False
    else:
        if (len(prerequisites_Upgrade[ident-5]) > currentState[ident]+1) and (prerequisites_Upgrade[ident-5][currentState[ident]] <= currentState[ident-5]):
            return True
        else:
            return False


def Weight(cost, PR):
    return cost/PR


def SQLAddNode(con, oldState, state, oldCost, newCost, PR, shortestTime, weight):
        cur = con.cursor()

        cur.execute("SELECT shortestTime FROM nodes WHERE name ='"+ str(state)+"'")
        data = cur.fetchone()
        if not data:
            sql_command = "INSERT INTO nodes VALUES('" + \
                str(state)+"',TRUE,"+str(oldCost+newCost)+","+str(shortestTime)+")"
            cur.execute(sql_command)
            cur.close()
            SQLCorrectEdges(con, oldState, state, weight)
            cur = con.cursor()
        elif data[0]  > shortestTime: 
            sql_command = "UPDATE nodes SET shortestTime="+str(shortestTime)+ " WHERE name='"+str(state)+"'"
            cur.execute(sql_command)
            cur.close()
            SQLCorrectEdges(con, oldState, state, weight)
            cur = con.cursor()
        elif data[0] < shortestTime:
            shortestTime = data[0]
        
        cur.execute("SELECT shortestTime FROM nodes WHERE name ='end'")
        knownEndtime = cur.fetchone()
        if knownEndtime[0]>(1e6-(oldCost+newCost))/PR + shortestTime:
            cur.execute("DELETE FROM edges WHERE target = 'end'")
            sql_command = "INSERT INTO edges VALUES('" + \
                str(state) + \
                    "', 'end',"+ str((1e6-(oldCost+newCost))/PR)+")"
            cur.execute(sql_command)
            cur.execute("UPDATE nodes SET shortestTime="+str((1e6-(oldCost+newCost))/PR + shortestTime)+ "WHERE name = 'end'")
            cur.close()
        con.commit()
        

def SQLCorrectEdges(con, goodOldState, goodNewState, weight):
    cur = con.cursor()

    cur.execute("DELETE FROM edges WHERE target = '"+ str(goodNewState)+"'")
    sql_command = "INSERT INTO edges VALUES('" + \
        str(goodOldState)+"','" + \
        str(goodNewState)+"',"+ str(weight)+")"
    cur.execute(sql_command)
    cur.close()
    

def AddNodesAndEdges(state, newState, i, upperLimit, con):    
    PR = ProductionRate(state)
    cur = con.cursor()
    cur.execute("SELECT allTimeBaked FROM nodes WHERE name = '"+str(state)+"'")
    oldCost = cur.fetchone()[0]
    newCost = UpgradeCost(state, i)
    weight = Weight(newCost, PR)
    cur.execute("SELECT shortestTime FROM nodes WHERE name = '"+str(state)+"'")
    oldShortestT = cur.fetchone()[0]
    newShortestT = oldShortestT + weight
    if weight < (1e6-(oldCost+newCost))/PR and weight < upperLimit:
        SQLAddNode(con, state, newState, oldCost, newCost, PR, newShortestT, weight)

def AddSuccessors(state, upperLimit, con):
    for i in range(len(state)):
        newState = list(state)
        if UpgradePossible(state, i):
            newState[i] = newState[i]+1
            AddNodesAndEdges(state, newState, i, upperLimit, con)

def killOrLive(con, upperLimit):
    cur = con.cursor()
    cur.execute("DELETE FROM nodes WHERE doSuccessors = TRUE and shortestTime >"+str(upperLimit))
    cur.execute("DELETE FROM nodes WHERE doSuccessors = FALSE and name != 'end' AND name NOT IN (SELECT source FROM edges)")
    cur.execute("DELETE FROM edges WHERE target NOT IN (SELECT name FROM nodes)")
    #cur.execute("DELETE FROM edges WHERE target NOT IN (SELECT source FROM edges)")
    con.commit()
    
    cur.execute("SELECT name FROM nodes WHERE doSuccessors = TRUE")
    liste = cur.fetchall()
    for name in liste:
        AddSuccessors(ast.literal_eval(name[0]), upperLimit, con)

def connectSQL(con):

    cursor = con.cursor()
    cursor.execute("""DROP TABLE nodes;""")
    cursor.execute("""DROP TABLE edges;""")

    sql_command = """
    CREATE TABLE nodes (
        name TEXT PRIMARY KEY, 
        doSuccessors BOOLEAN,
        allTimeBaked INTEGER,
        shortestTime REAL
    ) ; """

    cursor.execute(sql_command)

    sql_command = """
    CREATE TABLE edges (
        source TEXT,
        target TEXT,
        weight REAL
    ) ; """

    cursor.execute(sql_command)

    con.commit()
    #connection.close()

def SQLGetConnection():
    connection = sql.connect(user="postgres",password = "postgres",database="postgres",host="127.0.0.1", port="5432")
    cursor = connection.cursor()
    # Print PostgreSQL Connection properties
    print ( connection.get_dsn_parameters(),"\n")
    # Print PostgreSQL version
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("You are connected to - ", record,"\n")
    return connection

def SQLSetStart(con, zero):
    cur = con.cursor()
    cur.execute("INSERT INTO nodes VALUES('" + str(zero)+"',TRUE,"+str(15)+", 0)")
    cur.execute("INSERT INTO nodes VALUES( 'end' ,FALSE,"+str(1e6)+","+str(1e7)+")")
    con.commit()



def main(iterations):

    zero = [1]+[0]*9

    upperLimit = 42*60
    # record by simulation 49 min with range 100 and no grandmas
    #best bruteforce 45 min,montacarlo.py
    start = time.time()
    con = SQLGetConnection()
    connectSQL(con)  # only needed if no db created yet
    SQLSetStart(con, zero)
    fulltime = 0
    for i in range(iterations):
        start_loop = time.time()
        #G= letBestLive(G, zero, upperLimit)

        killOrLive(con, upperLimit)
        print('Decided to kill the node or do the successors')
        print(i)
        cur = con.cursor()
        cur.execute("SELECT shortestTime FROM nodes WHERE name = 'end'")
        newFulltime = cur.fetchone()[0]
        print(newFulltime/60)

        #killDeadEnd(G) ##not yet implemented in SQL
        #print('Checked for dead ends and killed the nodes')

        cur.execute("SELECT * FROM nodes")
        allNodes = cur.fetchall()
        print('Iteration', i, 'Nodes:', len(allNodes))
        cur.execute("SELECT * FROM edges")
        allEdges = cur.fetchall()
        print('Iteration', i, 'Edges:', len(allEdges))
        end_loop = time.time()
        print(end_loop-start_loop)
        if fulltime == newFulltime:
            print('No more need to buy things')
            break
        fulltime =newFulltime
    end = time.time()
    print('Worked for:', end-start, 'seconds')
    print('Full run time:',fulltime/60, 'minutes')
    f = open("solution", "a")
    f.write(str(fulltime) +"\n")
    target = 'end'
    for i in range(iterations+1):
        print(iterations+1-i, target)
        f.write(target +"\n")
        cur = con.cursor()
        cur.execute("SELECT source FROM edges WHERE target='"+target+"'")
        target = cur.fetchone()[0]
    f.write(target +"\n")

    #os.system("shutdown -s -t 10")
if __name__ == "__main__":
    main(10)
