
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import numpy as np
from sklearn.externals import joblib


dbname = 'ncaabb'
username = 'gshau'
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

features = joblib.load('features.pkl')
features = [f.replace('%','') for f in features]

featuresNamed = features+['name','fullName']

def loadFromDB(year,dbName='team_data'):
    try:
        df=pd.read_sql('SELECT * FROM '+dbName+'_'+str(year), engine,index_col='index')
    except:
        print('Could not find teams in database')
        return None
    if dbName == 'team_data':
        return df[featuresNamed]
    return df

def getYears():
    df=pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';", engine)
    yearList=sorted(np.unique(np.array([int(tn.split('_')[-1]) if 'team' in tn else 0 for tn in df.table_name.values])),reverse=True)[:-1]
    return yearList




def logit(x):
    return 1./(1.+np.exp(-x))

def logitInv(x):
    return -np.log((1.-x)/x)

class Tournament:
    def __init__(self,year=2017,regionOrder=None):
        self.year = year
        self.teamData=loadFromDB(self.year,dbName='team_data')
        self.teamNamesInTourney = loadFromDB(self.year,dbName='tourney_team')
        self.tourneyGames = loadFromDB(self.year,dbName='tourney_games')


        if regionOrder:
            self.regionOrder=regionOrder
        else:
            regionOrder=[]
            finalFourOrder=self.tourneyGames[self.tourneyGames['round']==5][['name_1','name_2']].values.flatten()
            for teamName in finalFourOrder:
                regionOrder.append(self.teamNamesInTourney[self.teamNamesInTourney.teamName==teamName].regionName.values[0])
            self.regionOrder=regionOrder


        teamOrder=[]
        for regionName in self.regionOrder:
            teamOrder.append(self.teamNamesInTourney[self.teamNamesInTourney.regionName==regionName].teamName.values)
        self.teamOrder=np.array(teamOrder).flatten()

        teamList=[]
        for teamName in self.teamOrder:
            properties = self.teamData[self.teamData.name==teamName][features]
            teamList.append(Team(teamName,properties))

        self.teamList = np.array(teamList)
        self.nTeams = len(teamList)

        self.initBracket()

        clf = joblib.load('model.pkl')
        self.setModel(clf)

        self.scaler = joblib.load('scaler.pkl')

    def initBracket(self):

        games=self.tourneyGames[['name_1','name_2','round','region','outcome']]
        bracket=dict([(i,[]) for i in np.arange(1,8)])
        for region in self.regionOrder:
            regionGames = games[games.region==region]
            for rnd in np.arange(1,5):
                gamesInRound = regionGames[regionGames['round']==rnd]
                for game in gamesInRound.itertuples():
                    bracket[rnd].append(game.name_1)
                    bracket[rnd].append(game.name_2)
        region='national'
        regionGames = games[games.region==region]
        for rnd in np.arange(5,7):
            gamesInRound = regionGames[regionGames['round']==rnd]
            for game in gamesInRound.itertuples():
                bracket[rnd].append(game.name_1)
                bracket[rnd].append(game.name_2)

        outcome=gamesInRound.iloc[0]['outcome']
        bracket[7]=[gamesInRound.values[0][1-outcome]]

        self.bracketOutcome = bracket

    def getPairings(self,teamList):
        pairings=[]
        if len(teamList)==0:
            return pairings
        for iteam in np.arange(int(len(teamList)/2)):
            pairings.append([teamList[2*iteam],teamList[2*iteam+1]])
        return pairings

    def setModel(self,model):
        self.model = model

    def predictGame(self,game):
        teamA=game[0].properties
        teamB=game[1].properties

        vec = teamA.values-teamB.values
        vecScaled = self.scaler.transform(vec)
        outcome=logit(self.model.coef_.dot(vecScaled.T)[0][0])

        return outcome

    def simulate(self,simLevel='favorite',scaleFactor=1):
        '''Simulate tournament:
        simLevel = simulation type - favorite vs. random
        scaleFactor = scale probability dispersion:
            if < 1 : Predictions of rare events become more likely
            if > 1 : Predictions of rare events become less likely'''
        teamList = self.teamList
        nTeamRemain = len(teamList)
        nRound = 1
        teamLists={}
        teamNameLists={}
        entropyLists={}
        teamLists[nRound]=teamList
        teamNameLists={1: [t.name for t in teamList]}
        while nTeamRemain > 1:
            pairs = self.getPairings(teamList)
            teamList=[]
            teamNameList=[]
            entropyList=[]
            for p in pairs:
                prob = self.predictGame(p)
                if simLevel=='favorite':
                    probThr = 0.5
                else:
                    probThr = np.random.rand()
                if scaleFactor != 1:
                    prob = logit(scaleFactor*logitInv(prob))
                if prob > probThr:
                    teamList.append(p[0])
                    teamNameList.append(p[0].name)
                    entropyList.append(prob*np.log(prob))
                else:
                    teamList.append(p[1])
                    teamNameList.append(p[1].name)
                    entropyList.append((1.-prob)*np.log(1.-prob))
            nRound+=1
            teamLists[nRound]=teamList
            teamNameLists[nRound]=teamNameList
            entropyLists[nRound]=entropyList
            nTeamRemain = len(teamList)

        self.entropyLists=entropyLists
        self.teamLists = teamLists
        self.teamNameLists = teamNameLists


        return teamNameLists


class Team:
    def __init__(self,name,properties):
        self.name=name
        self.properties=properties

def compareBrackets(refBracket,newBracket,pointsByRound):
    points=0
    for iround in refBracket.keys():
        if iround==1:
            continue
        points+=len(set(newBracket[iround]) & set(refBracket[iround]))*pointsByRound[iround]
    return points

class Pool:
    def __init__(self,tourney,poolSize=15,pointSystem=None,payoutPct=[.7,.2,.1],risk=0.3,entryFee=1):
        self.tourney = tourney
        self.poolSize = poolSize
        if pointSystem is None:
            pointSystem=dict([(i+2, 2**i) for i in np.arange(6)])
        self.pointSystem = pointSystem

        self.payoutPct = payoutPct
        self.risk = risk
        self.entryFee = entryFee

    def getTourneySets(self,ntourney=400,scaleFactor=1):
        self.tourneys=[self.tourney.simulate(simLevel='random',scaleFactor=scaleFactor) for ntourney in range(ntourney)]
        joblib.dump(self.tourneys,'tourneys_'+str(self.tourney.year)+'.pkl')

        print('Save: Tournament length: ',len(self.tourneys))


    def loadTourneySets(self):
        self.tourneys=joblib.load('tourneys_'+str(self.tourney.year)+'.pkl')
        print('Load: Tournament length: ',len(self.tourneys))




    def getGoodBracket(self,useRealBracket=False,verbose=False):

        payout=[0,0]
        # while (payout[0] < 1) | (payout[1] < 1):
        self.simulatePool(useRealBracket=useRealBracket,verbose=verbose,nrep=2000)
        payout = self.summary['expPayout']


    def simulatePool(self,useRealBracket=False,verbose=True,nrep=100):
        placements1=[]
        placements2=[]
        favBracket=self.tourney.simulate()
        self.favEntropy = self.tourney.entropyLists.copy()
        newBracket=self.tourney.simulate(simLevel='random',scaleFactor=1./self.risk)
        self.newEntropy = self.tourney.entropyLists.copy()
        ranks=np.zeros((self.poolSize+2,self.poolSize+2))
        pointList1=[]
        pointList2=[]
        for rep in range(nrep):
            if useRealBracket:
                refBracket = self.tourney.bracketOutcome
            else:
                refBracket=np.random.choice(self.tourneys,replace=True)
            poolPoints=[]
            randSel=np.random.randint(0,len(self.tourneys),self.poolSize)
            for irandBracket in randSel:
                bracket=self.tourneys[irandBracket] #np.random.choice(self.tourneys,replace=True)
                points=compareBrackets(refBracket,bracket,self.pointSystem)
                poolPoints.append(points)
            poolPoints=np.array(poolPoints)

            points1=compareBrackets(refBracket,favBracket,self.pointSystem)
            points2=compareBrackets(refBracket,newBracket,self.pointSystem)

            pointList1.append(points1)
            pointList2.append(points2)

            poolPoints1=np.append(poolPoints,points2)
            poolPoints2=np.append(poolPoints,points1)

            points2

            place1=(poolPoints1>points1).sum()
            place2=(poolPoints2>points2).sum()

            ranks[place1,place2]+=1

            placements1.append(place1)
            placements2.append(place2)
        placements1=np.array(placements1)
        placements2=np.array(placements2)

        vals1,bins=np.histogram(placements1,bins=range(self.poolSize),normed=True);
        vals2,bins=np.histogram(placements2,bins=range(self.poolSize),normed=True);
        payout=np.zeros(self.poolSize-1)
        payout[:len(self.payoutPct)]=self.payoutPct
        payout1 = np.nansum((vals1*payout*self.entryFee*self.poolSize))
        payout2 = np.nansum((vals2*payout*self.entryFee*self.poolSize))
        if verbose:
            print('Bracket 1:')
            print('Bracket points: ',np.mean(pointList1))
            print('Placement odds: ',vals1[:5])
            # print(vals1,vals2,payout,self.entryFee,self.poolSize)
            print('Expected payout: ',payout1)
            print('Bracket 2:')
            print('Bracket points: ',np.mean(pointList2))
            print('Placement odds: ',vals2[:5])
            print('Expected payout: ',payout2)

        norm = ranks.sum()
        bustPCT= ranks[3:,3:].sum()/norm

        self.summary = {}

        self.summary['favBracket']=favBracket
        self.summary['newBracket']=newBracket

        self.summary['poolPoints']=np.array([poolPoints1,poolPoints2]).T

        self.summary['expPayout']=np.array([payout1, payout2]).T
        self.summary['expPlace']=np.array([vals1, vals2]).T
        self.summary['ranks']=ranks
        self.summary['bustPCT']=bustPCT
