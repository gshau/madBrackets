
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



def loadTourney(year):
    df=pd.read_sql('SELECT * FROM tourney_team_'+str(year), engine,index_col='index')
    return df

def loadTeamData(year):
    df=pd.read_sql('SELECT * FROM team_data_'+str(year), engine,index_col='index')
    df[featuresNamed]
    return df[featuresNamed]

def getYears():
    df=pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';", engine)
    yearList=sorted(np.unique(np.array([int(tn.split('_')[-1]) if 'team' in tn else 0 for tn in df.table_name.values])),reverse=True)[:-1]
    return yearList

def initializeTourney(year=2017):

    teamData=loadTeamData(year)
    teamNamesInTourney = loadTourney(year)
    teamNames=teamNamesInTourney.teamName.values
    teamList=[]
    for teamName in teamNames:
        properties = teamData[teamData.name==teamName][features]
        teamList.append(Team(teamName,properties))

    tourney=Tournament(teamList)
    clf = joblib.load('model.pkl')
    tourney.setModel(clf)
    return tourney

def logit(x):
    return 1./(1.+np.exp(-x))

def logitInv(x):
    return -np.log((1.-x)/x)


class Tournament:
    def __init__(self,teamList):
        self.teamList = np.array(teamList)
        self.nTeams = len(teamList)
#         self.teamDict =


    def getPairings(self,teamList):
        pairings=[]
        if len(teamList)==0:
            return pairings
        for iteam in np.arange(int(len(teamList)/2)):
            pairings.append([teamList[2*iteam],teamList[2*iteam+1]])
        return pairings

    def setModel(self,model):
        self.model = model
#         self.scaler = scaler

    def predictGame(self,game):

        teamA=game[0].properties
        teamB=game[1].properties
#         teamA.index=[0]
#         teamB.index=[0]

        vec = teamA.values-teamB.values
        outcome=logit(self.model.coef_.dot(vec.T))

        return outcome

    def simulate(self,simLevel='favorite',scaleFactor=1):

        teamList = self.teamList
        nTeamRemain = len(teamList)
        nRound = 1
        teamLists={}
        teamNameLists={}
        teamLists[nRound]=teamList
        teamNameLists={1: [t.name for t in self.teamList]}
        while nTeamRemain > 1:
            pairs = self.getPairings(teamList)
            teamList=[]
            teamNameList=[]
            for p in pairs:
                prob = self.predictGame(p)
                if simLevel=='favorite':
                    probThr = 0.5
                else:
                    probThr = np.random.rand()
                if scaleFactor != 1:
                    probThr = logit(scaleFactor*logitInv(probThr))
                if prob > probThr:
                    teamList.append(p[0])
                    teamNameList.append(p[0].name)
                else:
                    teamList.append(p[1])
                    teamNameList.append(p[1].name)
            nRound+=1
            teamLists[nRound]=teamList
            teamNameLists[nRound]=teamNameList
            nTeamRemain = len(teamList)

        return teamNameLists


class Team:
    def __init__(self,name,properties):
        self.name=name
        self.properties=properties


# class Game:
#     def __init__(self,team1,team2):

def compareBrackets(refBracket,newBracket,pointsByRound):
    points=0
    for iround in refBracket.keys():
        if iround==1:
            continue

        points+=len(set(newBracket[iround]) & set(refBracket[iround]))*pointsByRound[iround]
    return points

def simulatePool(tourney,poolSize=15,entry=1,scaleFactor=0.1,payoutPct=[.7,.2,.1]):
    tourneys=[tourney.simulate(simLevel='random') for ntourney in range(200)]

    pointsByRound=dict([(i+2, 2**i) for i in np.arange(6)])
    placement1=[]
    placement2=[]
    favBracket=tourney.simulate()
    newBracket=tourney.simulate(simLevel='random',scaleFactor=scaleFactor)
    ranks=np.zeros((poolSize+2,poolSize+2))
    for rep in range(poolSize*10):
        refBracket=np.random.choice(tourneys,replace=True)
        poolPoints=[]
        for poolBracket in range(poolSize):
            bracket=np.random.choice(tourneys,replace=True)
            points=compareBrackets(refBracket,bracket,pointsByRound)
            poolPoints.append(points)
        poolPoints=np.array(poolPoints)
        points1=compareBrackets(refBracket,favBracket,pointsByRound)

        points2=compareBrackets(refBracket,newBracket,pointsByRound)

        poolPoints1=np.append(poolPoints,points2)
        poolPoints2=np.append(poolPoints,points1)

        placement1.append((poolPoints1>points1).sum())
        placement2.append((poolPoints2>points2).sum())
        ranks[placement1,placement2]+=1
    placement1=np.array(placement1)
    placement2=np.array(placement2)

    # vals1,bins,patch=plt.hist(placement1,bins=range(max(placement1)),normed=True);
    # vals2,bins,patch=plt.hist(placement2,bins=range(max(placement2)),normed=True);
    vals1,bins=np.histogram(placement1,bins=range(max(placement1)),normed=True);
    vals2,bins=np.histogram(placement2,bins=range(max(placement2)),normed=True);
    payout=np.zeros(poolSize)
    payout[:len(payoutPct)]=payoutPct
    payout1 = (vals1*payout[:max(placement1)-1]*entry*poolSize).sum()
    payout2 = (vals2*payout[:max(placement2)-1]*entry*poolSize).sum()
    print('Bracket 1:')
    print('Placement odds: ',vals1[:5].cumsum())
    print('Expected payout: ',(vals1*payout[:max(placement1)-1]*entry*poolSize).sum()    )
    print('Bracket 2:')
    print('Placement odds: ',vals2[:5].cumsum())
    print('Expected payout: ',(vals2*payout[:max(placement2)-1]*entry*poolSize).sum()    )

    # plt.figure()
    # sns.jointplot(placement1,placement2,stat_func=None)
#     plt.imshow(ranks,origin='lower')
#     return placement1,placement2
    return(favBracket,newBracket,payout1,payout2)
#     print(ranks)
#     plt.hist(poolPoints,bins=np.arange(0,192,5));
#     return (vals1*payout[:max(placement1)-1]*entry*poolSize).sum()   ,vals1[:3].sum()
