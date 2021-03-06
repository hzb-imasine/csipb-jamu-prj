import time
import json
import yaml
import MySQLdb
import pickle
import dbcrawler_util as util
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib2 import urlopen
from datetime import datetime

def main():
    #################
    plantCompoundDict = None
    # plantCompoundDict = parseKnapsack()
    fpath = '/home/tor/robotics/prj/csipb-jamu-prj/dataset/knapsack/20161003/knapsack_jsp_plant_vs_compound_2016-10-04_16:34:06.468234.pkl'  
    with open(fpath, 'rb') as handle:
        plantCompoundDict = pickle.load(handle)

    # insertPlants(plantCompoundDict.keys())

    ################
    insertPlantVsCompound(plantCompoundDict)
    db.close()

def parseKnapsack():
    # get the seed plant list
    seedPlantListFPaths = ['/home/tor/robotics/prj/csipb-jamu-prj/dataset/knapsack/20161003/ijah_jamu_plants.lst']

    seedPlantList = []
    for fp in seedPlantListFPaths:
        with open(fp) as infile:        
            idx = 0
            for line in infile:
                idx += 1
                print 'parsing idx=', idx, 'of', fp
                line = line.strip()
                words = line.split()

                if len(words)==3:
                    pass
                elif len(words)==4:
                    pass

                name = ' '.join(words)
                seedPlantList.append(name)

    # crawl knapsack
    BASE_URL = 'http://kanaya.naist.jp/knapsack_jsp/result.jsp?sname=organism&word='
    plantCompoundDict = defaultdict(list)
    now = datetime.now()

    for idx,p in enumerate(seedPlantList):
        idx += 1
        print 'crawling idx=', idx, 'of', len(seedPlantList)

        url = BASE_URL + p
        # print 'crawling url=', url

        html = urlopen(url).read()
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", "sortable d1")
        table = table.find_all('tr')

        compoundData = dict()
        for i,row in enumerate(table):
            datum = []
            cols = row.find_all('td', 'd1')
            for pos,col in enumerate(cols):
                datum.append(str(col.get_text()))

            if len(datum)==6:
                comKnapsackId = datum[0]
                comCasId = datum[1]
                comName = datum[2]
                comFormula = datum[3]
                plantName = datum[5]
                
                plantNameWords = plantName.split()
                if len(plantNameWords)>1:
                    plantNameWords = plantNameWords[0:2]
                    plantName = ' '.join(plantNameWords)
                    plantName = plantName.capitalize()

                    compoundDatum = ( comKnapsackId, comCasId, comName, comFormula )

                    existingCom = [ c[0] for c in plantCompoundDict[plantName]]
                    if comKnapsackId not in existingCom:
                        plantCompoundDict[plantName].append( compoundDatum )

    jsonFpath = outDir+'/knapsack_jsp_plant_vs_compound_'+str(now.date())+'_'+str(now.time())+'.json'
    with open(jsonFpath, 'w') as f:
        json.dump(plantCompoundDict, f, indent=2, sort_keys=True)

    pklFpath = outDir+'/knapsack_jsp_plant_vs_compound_'+str(now.date())+'_'+str(now.time())+'.pkl'
    with open(pklFpath, 'wb') as f:
        pickle.dump(plantCompoundDict, f)

    return plantCompoundDict

def insertPlants(plantList):
    nPlant = len(plantList)
    for idx, p in enumerate(plantList):
        plaId = str(idx+1)
        plaId = plaId.zfill(8)
        plaId = '"'+'PLA'+plaId+'"'
        print 'inserting ', plaId, 'of', str(nPlant)

        plaName = '"'+p+'"'

        qf = 'INSERT INTO plant (pla_id,pla_name) VALUES ('
        qm = plaId+','+plaName
        qr = ')'
        q = qf+qm+qr
        util.mysqlCommit(q)

def insertPlantVsCompound(plantCompoundDict):
    pc = plantCompoundDict
    src = 'knapsack.kanaya.naist.jp'
    log = []; logFpath = outDir+'/insertPlantVsCompound.log'

    n = len(pc); idx = 0; 
    for p,v in pc.iteritems():
        idx += 1

        qf = 'SELECT pla_id FROM plant WHERE pla_name ='
        qm = '"'+p+'"'
        qr = ''
        q = qf+qm+qr
        plaIdR = util.mysqlCommit(db,cursor,q); 

        comList = list( set([c[0] for c in v]) )
        for c in comList:
            msg = 'inserting '+ p+ ' vs '+ c+ ' idx= '+ str(idx)+ ' of '+ str(n)
            print msg

            qf = 'SELECT com_id FROM compound WHERE com_knapsack_id ='
            qm = '"' + c + '"'
            qr = ''
            q = qf+qm+qr
            comIdR = util.mysqlCommit(db,cursor,q); 

            if plaIdR!=None and comIdR!=None:
                plaId = plaIdR[0]
                comId = comIdR[0]

                insertVals = [plaId,comId,src]
                insertVals = ['"'+i+'"' for i in insertVals]

                qf = 'INSERT INTO plant_vs_compound (pla_id,com_id,source) VALUES ('
                qm = ','.join(insertVals)
                qr = ')'
                q = qf+qm+qr
                util.mysqlCommit(db,cursor,q)
            else:
                log.append('FAIL: '+msg)

    with open(logFpath,'w') as f:
        for i in log:
            f.write(str(i)+'\n')

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
    