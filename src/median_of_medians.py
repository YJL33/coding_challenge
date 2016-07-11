"""
Implement of "median of medians" algorithm

L: list of numbers
"""
def select(L):
    if len(L) <= 10:
        L.sort()
        return L[int(len(L)/2)]         # Here doesn't work for length = even
    S = []
    lIndex = 0
    while lIndex+5 < len(L)-1:
        S.append(L[lIndex:lIndex+5])
        lIndex += 5
    S.append(L[lIndex:])
    meds = []
    for subList in S:
        #print(subList)
        meds.append(select(subList))
    L2 = select(meds)
    L1 = L3 = []
    for i in L:
        if i < L2:
            L1.append(i)
        if i > L2:
            L3.append(i)
    if len(L) < len(L1):
        return select(L1)
    elif len(L) > len(L1) + 1:
        return select(L3)
    else:
        return L2