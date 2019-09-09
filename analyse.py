import matplotlib.pyplot as plt

list2 = []
kleinsterwert =200
with open("ccSolutions") as f:
    for row in f:
        if kleinsterwert> float(row.split(";")[0]):
            kleinsterwert = float(row.split(";")[0])
        list2.append(kleinsterwert)

print(min(list2))
plt.plot(list2)
plt.show()