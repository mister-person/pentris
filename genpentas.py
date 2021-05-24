'''
this generates all n-ominos of size n
reflections and rotations count as the same
'''
from copy import copy
allpentas = []

i = input("how many squares? ")
try:
    N_OMINO = int(i)
except ValueError:
    N_OMINO = 5

class Coord(tuple):
    def __add__(self, x):
        l = []
        for i in range(len(self)):
            l.append(self[i] + x[i])
        return type(self)(l)

def tocoord(x):
    newx = []
    for thing in x:
        newx.append(Coord(thing))
    return newx

def drawshape(shape):
    shape = normalize(shape)
    for x in range(len(shape)):
        for y in range(len(shape) * 2):
            if(x == 0 and y - len(shape) == 0):
                if(Coord((0, 0)) in shape):
                    print("O", end="")
                else:
                    print("-", end="")
            elif(Coord((x, y - len(shape))) in shape):
                print("#", end="")
            else:
                print("`", end="")
        print()

def checklegal(shape):#lol this feels like cheating
    if(len(set(shape)) < len(shape)):
        return False
    return True

def checksimilar(shape1, shape2):
    if(shape1 == shape2):
        return True
    if(len(shape1) != len(shape2)):
        return False
    for x in range(len(shape2)):
        translated = copy(shape2)
        for i in range(len(translated)):
            translated[i] += (-shape2[x][0], -shape2[x][1])

        for block in shape1:#for else lol
            if block not in translated:
                break
        else:#executes if loop doesn't break
            return True
    return False

def rotate(shape, count=1):
    newshape = list(shape)
    for i in range(count):
        for j in range(len(newshape)):
            newshape[j] = Coord((newshape[j][1], -newshape[j][0]))
    return newshape

def reflect(shape, count=1):
    newshape = list(shape)
    for i in range(count):
        for j in range(len(newshape)):
            newshape[j] = Coord((newshape[j][0], -newshape[j][1]))
    return newshape

def normalize(penta):
    newpenta = list(penta[:])
    newpenta.sort()
    thingtoadd = (-newpenta[0][0], -newpenta[0][1])
    for i in range(len(newpenta)):
        newpenta[i] += thingtoadd
    return newpenta

def comp(penta1, penta2):
    return 1 if penta1 > penta2 else -1
    for i in range(len(penta1)):
        if(penta1[i] > penta2[i]):
            return 1
        elif(penta1[i] > penta2[i]):
            return -1
    return 0

def findrotation(penta):
    penta = normalize(penta)
    origpenta = penta
    newpenta = penta
    for rotation in range(4):
        newpenta = normalize(rotate(origpenta, rotation))
        if(comp(penta, newpenta) > 0):
            penta = newpenta
    #comment next 4 lines to stop counting reflections as the same
    for rotation in range(4):
        newpenta = normalize(rotate(reflect(origpenta), rotation))
        if(comp(penta, newpenta) > 0):
            penta = newpenta
    return penta

sides = (Coord((0, 1)), Coord((0, -1)), Coord((1, 0)), Coord((-1, 0)))
pentaset1 = { (Coord((0, 0)),) }
pentaset2 = set()

#while(len(pentaparts) > 0):
for x in range(N_OMINO - 1):
    for penta in pentaset1:
        for block in penta:
            for side in sides:
                newpenta = list(penta)
                newpenta.append(block + side)
                if(checklegal(newpenta)):
                    newpenta = tuple(findrotation(newpenta))
                    pentaset2.add(newpenta)
    pentaset1 = pentaset2
    pentaset2 = set()
    print("done round", x)

#pentas = pentaparts[:]
#for i in range(len(pentas)):
    #pentas[i] = tuple(pentas[i])
#
#print(len(pentas))
#pentas = list(set(pentas))#lol more cheating
pentas = list(pentaset1)

for i in range(len(pentas)):
    pentas[i] = list(pentas[i])

print(len(pentas))
'''
uniquepentas = []
count = 0
for penta in pentas:
    for penta2 in uniquepentas:
        if(checksimilar(penta, penta2)):
            break
    else:
        uniquepentas.append(penta)
    count += 1
    if count%100 == 0:
        print(count, "/", len(pentas), len(uniquepentas))

pentas = uniquepentas
'''
uniquepentas = []

'''
count = 0
uniqueset = set()
for penta in pentaset1:
    unique = True
    for rotation in range(4):
        if(tuple(normalize(rotate(penta, rotation))) in uniqueset):
            unique = False
    for rotation in range(4):
        if(tuple(normalize(rotate(reflect(penta), rotation))) in uniqueset):
            unique = False
    if(unique):
        uniqueset.add(penta)
    count += 1
    if count%1000 == 0:
        print(count, "/", len(pentas), len(uniqueset))

'''
'''
count = 0
for penta in pentas:
    for penta2 in uniquepentas:
        if(checksimilar(penta, rotate(penta2, 0))):
            break
        elif(checksimilar(penta, rotate(penta2, 1))):
            break
        elif(checksimilar(penta, rotate(penta2, 2))):
            break
        elif(checksimilar(penta, rotate(penta2, 3))):
            break
        elif(checksimilar(penta, rotate(reflect(penta2), 0))):
            break
        elif(checksimilar(penta, rotate(reflect(penta2), 1))):
            break
        elif(checksimilar(penta, rotate(reflect(penta2), 2))):
            break
        elif(checksimilar(penta, rotate(reflect(penta2), 3))):
            break
    else:
        uniquepentas.append(penta)
    count += 1
    if count%100 == 0:
        print(count, "/", len(pentas), len(uniquepentas))
'''

print("total: ", len(pentas))
for penta in sorted(list(pentas)):
    print(penta)
    drawshape(penta)
    a = input()
