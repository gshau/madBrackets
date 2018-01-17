
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
import numpy as np

dbname = 'ncaabb'
username = 'gshau' # change this to your username
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))


def loadTourney(year):
    df=pd.read_sql('SELECT * FROM tourney_team_'+str(year), engine,index_col='index')
    return df

def loadTeamData(year):
    df=pd.read_sql('SELECT * FROM team_data_'+str(year), engine,index_col='index')
    return df

def getYears():
    df=pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';", engine)
    yearList=sorted(np.unique(np.array([int(tn.split('_')[-1]) if 'team' in tn else 0 for tn in df.table_name.values])),reverse=True)[:-1]
    return yearList



class Tournament:
    def __init__(self,teamList):
        self.teamList = np.array(teamList)
        self.nTeams = len(teamList)
#         self.teamDict =


    def getPairings(self,teamList):
        pairings=[]
        for iteam in range(len(teamList)/2):
            pairings.append([teamList[2*iteam],teamList[2*iteam+1]])
        return pairings

    def setModel(self,model):
        self.model = model

    def predictGame(self,game):
        outcome = model(game[0].properties,game[1].properties)
        return outcome

    def simulate(self,probThr):

        teamList = self.teamList
        nTeamRemain = len(teamList)
        nRound = 1
        teamLists={}
        teamLists[nRound]=teamList
        while nTeamRemain > 1:
            pairs = self.getPairings(teamList)
            teamList=[]
            for p in pairs:
#                 print('Pair: ',p[0].name, p[1].name,nTeamRemain)
                prob = self.predictGame(p)
                if prob > probThr():
                    teamList.append(p[0])
                else:
                    teamList.append(p[1])
            nRound+=1
            teamLists[nRound]=teamList
            nTeamRemain = len(teamList)

        return teamLists


class Team:
    def __init__(self,name,properties):
        self.name=name
        self.properties=properties
