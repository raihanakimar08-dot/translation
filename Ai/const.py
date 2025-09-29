import itertools
colors={"red","blue","green"}
adjacent={('A','B'),('B','C'),('A','C')}
variables={'A','B','C'}
for assignment in itertools.product(colors,repeat=3):
    mapping=dict(zip(variables,assignment))
    if all(mapping[x] != mapping[y]for x,y in adjacent):
        print(mapping)
