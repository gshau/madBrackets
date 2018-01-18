from flask import render_template, request
from ncaatourney import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

import model

user='gshau'
host='localhost'
dbname='birth_db'

dbname = 'ncaabb'
username = 'gshau' # change this to your username
engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

year='2017'
years = model.getYears()

pointsByRound=[1,2,4,8,16,32]

def fetchTeam(year):
    df=model.loadTourney(year)

    viewData={}
    regions=df.regionName.unique()
    viewData['regionList']=[regions[iregion] for iregion in [0, 3, 1, 2]]
    viewData['teamNames']=[[tname for tname in df[df.regionName==regions[iregion]].teamName.values] for iregion in [0, 3, 1, 2]]
    viewData['seeds']=[seed for seed in df[df.regionName==regions[0]].seed.values]
    viewData['nTeams']=len(viewData['teamNames'])
    return viewData

@app.route('/')
@app.route('/index')
@app.route('/year/<int:year>')
def index(year=2017):
        tourney = model.initializeTourney(year=year)
        bracket=tourney.simulate()
        viewData = fetchTeam(year)

        initialBracket={1: bracket[1], 2: ['']*32, 3: ['']*16, 4: ['']*8, 5: ['']*4, 6: ['']*2, 7: ['']*1}

        # print(bracket)
        return render_template("bracket_template.html",
           data = viewData, bracket=initialBracket, year = year, years = years)


@app.route('/populate/<int:year>')
def populate(year=2017):
    tourney = model.initializeTourney(year=year)
    bracket=tourney.simulate()
    viewData = fetchTeam(year)
    # print(bracket)
    return render_template("bracket_template.html",
       data = viewData, bracket=bracket, year = year, years = years)

@app.route('/generate/<int:year>')
def generate(year=2017):
    tourney = model.initializeTourney(year=year)
    bracket=tourney.simulate()
    viewData = fetchTeam(year)
    favBracket,newBracket,payout1,payout2=model.simulatePool(tourney,poolSize=25,entry=1,scaleFactor=0.3,payoutPct=[.7,.2,.1])
    # print(newBracket)
    return render_template("second_bracket_template.html",
       data = viewData, bracket=newBracket, year = year, years = years, payout=[round(payout1,2),round(payout2,2)])
