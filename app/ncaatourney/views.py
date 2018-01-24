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

years = model.getYears()
years=[2017,2016]
year=2017
pointsByRound=[1,2,4,8,16,32]


@app.route('/')
@app.route('/index')
@app.route('/year/<int:year>')
def index(year=2017):
        tourney = model.Tournament(year=year)
        bracket=tourney.simulate()

        initialBracket={1: bracket[1], 2: ['']*32, 3: ['']*16, 4: ['']*8, 5: ['']*4, 6: ['']*2, 7: ['']*1}

        # print(bracket)
        return render_template("bracket_template.html",
           bracket=initialBracket, year = year, years = years)


@app.route('/actualBracket/<int:year>')
def actualBracket(year=2017):
    tourney = model.Tournament(year=year)
    return render_template("bracket_template.html",
       bracket=tourney.bracketOutcome, year = year, years = years)


@app.route('/populate/<int:year>')
def populate(year=2017):
    tourney = model.Tournament(year=year)
    bracket=tourney.simulate()
    return render_template("bracket_template.html",
       bracket=bracket, year = year, years = years)

@app.route('/generate/<int:year>')
def generate(year=2017,risk=0.3):
    tourney = model.Tournament(year=year)
    bracket=tourney.simulate()
    poolList=[]
    pool=model.Pool(tourney,poolSize=25,risk=risk,payoutPct=[.6,.3,.1])
    pool.loadTourneySets()

    pool.getGoodBracket()

    newBracket = pool.summary['newBracket']

    return render_template("second_bracket_template.html",
       newBracket=pool.summary['newBracket'],
       bracket=pool.summary['newBracket'],
       firstBracket=pool.summary['favBracket'],
       year = year, years = years,
       payout=list(pool.summary['expPayout'].tolist()),
       ptile0=list(pool.summary['expPlace'][:,0].tolist()),
       ptile1=list(pool.summary['expPlace'][:,1].tolist()),
       bustPCT = pool.summary['bustPCT'])


@app.route('/set_risk', methods=['GET', 'POST'])
def setRisk():
    data = request.args
    # print(data)
    riskLevel = float(data['risk'])*0.2
    year = int(data['year'])
    # print(float(riskLevel)*0.1)
    return generate(year,risk=riskLevel)



@app.route('/pointSystem')
def pointSystem():
    return render_template("point_system.html")

@app.route('/poolSize')
def poolSize():
    return render_template("point_system.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
