import random
d = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
p = [0, 1, 2, 3]

def find(p):
    return d[p[0]][p[1]] + d[p[1]][p[2]] + d[p[2]][p[3]] + d[p[3]][p[0]]

best = p[:]
short = find(p)

for i in range(10000):
    a = random.randint(0, 3)
    b = random.randint(0, 3)
    p[a], p[b] = p[b], p[a]

    now = find(p)

    if now < short:
        best = p[:]
        short = now
    else:
        p[a], p[b] = p[b], p[a]

print("Path:", best)
print("Distance:", short)