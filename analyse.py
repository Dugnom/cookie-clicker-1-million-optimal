import matplotlib.pyplot as plt

list2 = []
with open("ccSolutions") as f:
    for row in f:
        list2.append(float(row.split()[0]))

print(min(list2))