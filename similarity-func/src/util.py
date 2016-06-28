import numpy as np
from collections import defaultdict

import config as cfg

def getRecallRankDict(pop, data, dataDict):
    # Get refERENCE and remAINING idx
    refAndRemIdxDict = defaultdict(tuple)
    for classIdx,classData in dataDict.iteritems():
        nSample = len(classData)
        nRef = int( cfg.nRefPerClassInPercentage/100.0 * nSample )
        refIdxList = np.random.randint(0,nSample, size=nRef)
        remIdxList = [idx for idx in range(nSample) if idx not in refIdxList]

        refAndRemIdxDict[classIdx] = (refIdxList,remIdxList)

    # 
    popStr = [expandFuncStr( str(i) ) for i in pop]
    recallRankDict = defaultdict(tuple)
    for i in popStr:
        recallRankDict[i] = (1.0,True)

    return recallRankDict
    
    # # Get Recall Matrix along with some other fitness
    # nIndividual = len(pop); nClass = len(dataDict)
    # medianRecallMat = np.zeros( (nIndividual,nClass) )

    # for individualIdx,individual in enumerate(pop):
    #     for classIdx, classData in dataDict.iteritems():
    #         refIdxList = refAndRemIdxDict[classIdx][0]
    #         nRecallList = [] # from all refIdx of this class

    #         for refIdx in refIdxList:
    #             refStringIdx = classData[refIdx]
    #             refString = data[refStringIdx]

    #             # Compute simScore for each pair of (ref, rem)
    #             simScoreList = [] # each element contains 3-tuple of (simScore, refClassLabel, remClassLabel)
    #             for remClassIdx, refAndRemIdx in refAndRemIdxDict.iteritems():
    #                 remIdxList = refAndRemIdx[1]
    #                 for remIdx in remIdxList:
    #                     remStringIdx = dataDict[remClassIdx][remIdx]
    #                     remString = data[remStringIdx]

    #                     individualStr = expandFuncStr(individual)
    #                     simScore = util.getSimScore(refString,remString,individualStr)
    #                     simScoreList.append( (simScore,classIdx,remClassIdx) )

    #             # Sort simScoreList based descending order of SimScore
    #             sortedSimScoreListIdx = sorted(range(len(simScoreList)), key=lambda k: simScoreList[k][0],reverse=True)

    #             nTop = int(cfg.nTopInPercentage/100.0 * len(sortedSimScoreListIdx))
    #             sortedSimScoreListIdx = sortedSimScoreListIdx[0:nTop]

    #             # Get the number of recall/tp
    #             nRecall = 0
    #             for i in sortedSimScoreListIdx:
    #                 refClass = simScoreList[i][1]
    #                 remClass = simScoreList[i][2]
    #                 if (refClass==remClass):
    #                     nRecall += 1
    #             nRecallList.append(nRecall) # Add true positive value for this class for this refIdx.

    #         median = np.median(nRecallList) # Calculate median of nRecall of this class from all refIdx
    #         medianRecallMat[individualIdx][classIdx] = median

    # # Get median recall Ranking Matrix and recallFitness (agnostic to iid)
    # medianRecallRankMat = np.zeros( (nIndividual, nClass) )
    # for i in range(nClass):
    #     medRecall = medianRecallMat[:,i] # from all individuals of this class
    #     sortedMedRecallIdx = sorted(range(nIndividual), key=lambda k: medRecall[k],reverse=True)# descending

    #     rankList = []
    #     for j in range(nIndividual):
    #         rank = sortedMedRecallIdx.index(j)
    #         rankList.append(rank)

    #     medianRecallRankMat[:,i] = rankList

    # recallFitnessList = []
    # for i in range(nIndividual):
    #     recallFitness = np.average(medianRecallRankMat[i,:]) * -1.0 # inversed as we maximize the Fitness
    #     recallFitnessList.append(recallFitness)

    # # Test i.i.d (independent and identically distributed)
    # # with H0 = two rank lists are independent
    # # Thus id p-value is less than a threshold then we accept H0
    # # If H0 is accepted, then we can average the rank
    # pValueList = []
    # for i in range(nClass-1):
    #     for j in range(i+1,nClass):
    #         x1 = medianRecallRankMat[:, i]
    #         x2 = medianRecallRankMat[:, j]

    #         tau, pval = stats.kendalltau(x1, x2)
    #         pValueList.append(pval)

    # independent = False
    # if np.average(pValueList) <= cfg.pValueAcceptance:
    #     independent = True

    # return (independent, recallFitnessList)

def getSimScore(x1,x2,funcStr):
    a = getFeatureA(x1,x2); b = getFeatureB(x1,x2)
    c = getFeatureC(x1,x2); d = getFeatureD(x1,x2)

    return eval(funcStr)

def inRange(simScore):
    return (simScore>0.0 and simScore<=1.0)

def computeGram(X, funcStr):
    print 'computeGram with ', funcStr
    shape = (len(X),len(X))
    gram = np.zeros(shape)

    for i, x1 in enumerate(X):
        for j,x2 in enumerate(X[i:]):
            a = getFeatureA(x1,x2); b = getFeatureB(x1,x2)
            c = getFeatureC(x1,x2); d = getFeatureD(x1,x2)

            simScore = getSimScore(x1,x2,funcStr)
            assert simScore>0.0 
            assert simScore<=1.0

            gram[i][j] = gram [j][i] = simScore

    return gram

def expandFuncStr(istr):
    expansionDict = {'add': 'np.add', 'sub': 'np.subtract', 'mul': 'np.multiply',
                     'pDiv': 'protectedDiv', 'min': 'np.minimum', 'max': 'np.maximum' }

    fstr = istr
    for key, d in expansionDict.iteritems():
        fstr = fstr.replace(key,d)

    return fstr

def tanimotoStr():
    return 'pDiv(a, add(a, add(b, c)))'

# def forbesStr():
#     return 'div(sub(mul(add(add(a, b), add(c, d)), a), mul(add(a, b), add(a, c)),sub(mul(add(add(a, b), add(c, d)), min(add(a, b), add(a, c)),mul(add(a, b), add(a, c)))'

def tanimoto(pset, min_, max_, type_=None):
    def condition(height, depth):
        return depth == height

    if type_ is None:
        type_ = pset.ret

    expr = []
    lsTerm = pset.terminals[type_]
    lsPrim = pset.primitives[type_]

    expr.append(lsPrim[3])
    expr.append(lsTerm[0])
    expr.append(lsPrim[0])
    expr.append(lsTerm[0])
    expr.append(lsPrim[0])
    expr.append(lsTerm[1])
    expr.append(lsTerm[2])

    return expr

# def forbes(pset, min_, max_, type_=None):
#     def condition(height, depth):
#         return depth == height

#     if type_ is None:
#         type_ = pset.ret

#     expr = []
#     lsTerm = pset.terminals[type_]
#     lsPrim = pset.primitives[type_]

#     expr.append(lsPrim[3])
#     expr.append(lsPrim[1])
#     expr.append(lsPrim[2])
#     expr.append(lsPrim[0])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[1])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[2])
#     expr.append(lsTerm[3])
#     expr.append(lsTerm[0])
#     expr.append(lsPrim[2])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[1])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[2])

#     expr.append(lsPrim[1])
#     expr.append(lsPrim[2])
#     expr.append(lsPrim[0])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[1])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[2])
#     expr.append(lsTerm[3])
#     expr.append(lsPrim[4])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[1])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[2])
#     expr.append(lsPrim[2])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[1])
#     expr.append(lsPrim[0])
#     expr.append(lsTerm[0])
#     expr.append(lsTerm[2])

#     return expr

def protectedDiv(left, right):
    with np.errstate(divide='ignore',invalid='ignore'):
        x = np.divide(left, right)
        if isinstance(x, np.ndarray):
            x[np.isinf(x)] = 1
            x[np.isnan(x)] = 1
        elif np.isinf(x) or np.isnan(x):
            x = 1
    return x

def pow(x):
    return np.power(x, 2)

def powhalf(x):
    return np.power(x, 0.5)

def loadData(datapath):
    data = np.loadtxt(datapath, delimiter=',')

    dataDict = defaultdict(list)
    for idx, datum in enumerate(data):
        classIdx = int(datum[0]) # the first element _must_ be classIdx
        dataDict[classIdx].append(idx) # contain only the idx

    dataFeature = []
    for idx,x in enumerate(data):
        subdataFeature = []
        for idx2,x2 in enumerate(data):
            featureDict = {}
            featureDict['a'] = getFeatureA(x,x2)
            featureDict['b'] = getFeatureB(x,x2)
            featureDict['c'] = getFeatureC(x,x2)
            featureDict['d'] = getFeatureD(x,x2)
            subdataFeature.append(featureDict)
        dataFeature.append(subdataFeature)
    
    return (data,dataDict,dataFeature)

def getFeatureA(s1,s2):
    return np.inner(s1, s2)

def getFeatureB(s1,s2):
    return np.inner(s1, 1-s2)

def getFeatureC(s1,s2):
    return np.inner(1-s1, s2)

def getFeatureD(s1,s2):
    return np.inner(1-s1, 1-s2)

def isConverged(pop):
    maxFitnessVal = np.max([ind.fitness.values[0] for ind in pop])
    
    converged = False
    if maxFitnessVal > cfg.convergenceThreshold:
        converged = True

    return converged
