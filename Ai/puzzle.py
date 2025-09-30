from collections import deque

def solve(start):
    goal = "123456780"
    q = deque([(start, [])])
    seen = {start}
    while q:
        s, path = q.popleft()
        if s == goal: return path + [s]
        i = s.index("0")
        for d in (-3, 3, -1, 1):
            j = i + d
            if 0 <= j < 9 and not (i%3==0 and d==-1) and not (i%3==2 and d==1):
                l = list(s); l[i], l[j] = l[j], l[i]
                n = ''.join(l)
                if n not in seen:
                    seen.add(n)
                    q.append((n, path+[s]))

p = input("Enter 9-digit puzzle (0=blank): ")
steps = solve(p)
for s in steps:
    print(s[:3], s[3:6], s[6:], sep="\n"); print()
print("Moves:", len(steps)-1)