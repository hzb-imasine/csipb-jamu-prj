### Experiment/Logging Config
seed = 0
testSize = 0.25

datasetName = 'jamu'
nMaxSampleEachClass = 100

xprmtDir = '/home/banua/xprmt'
datasetDir = '../data'
datasetPath = datasetDir+'/'+datasetName+'/'+datasetName+'.csv'
xprmtTag = datasetName

### DEAP GP Config
nIndividual = 100
nTanimotoIndividualInPercentage = 0
nMaxGen = 100 # not including the initial generation
pMut = 0.3
pCx = 0.5

treeMinDepth = 2
treeMaxDepth = 3
subtreeMinDepthMut = 1
subtreeMaxDepthMut = 1

nHOF = nIndividual
recallFitnessOnlyIfIndependent = False
# convergenceThreshold = -0.1

### fitness recall config
nRefPerClassInPercentage = 20
nTopInPercentage = 20

### KendallTauTest Config
maxKendallTauTestTrial = 3
pValueAcceptance = 0.05
