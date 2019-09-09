import matplotlib.pyplot as plt
import numpy as np

file = open("ccSolutions","r")

times = []

for information in file:
    zeile = information.split(";")
    time = zeile[0]
    times.append(float(time))

shortest_time = min(times)

print((shortest_time))

    


