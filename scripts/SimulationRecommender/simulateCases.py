import random

def testRandomizeCase(x, y):
    assert type(x) == list
    assert len(x) == len(y)


def randomizeCase(x,y,n):
    random.seed(a=1)
    output = []
    for _ in range(50):
        a = random.sample(x, n)
        b = random.sample(y, n)
        output.append((a,b))
    return(output)

p1 = ['a','b','c', 'd', 'e']
p2 = [True,True,True, False, False]
t = randomizeCase(p1, p2, 5)

print t[0]
print t[1]
print t[2]
