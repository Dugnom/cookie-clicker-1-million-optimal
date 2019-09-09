import matplotlib.pyplot as plt

list2 = []
with open("ccSolutions") as f:
    for row in f:
        list2.append(row.split(";")[0])

print(min(list2))

plt.hist(list2, 1000)
plt.show()
