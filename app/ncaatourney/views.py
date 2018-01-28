from flask import render_template, request
from ncaatourney import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import numpy as np
import psycopg2

import model

user='gshau'
host='localhost'
dbname = 'ncaabb'
username = 'gshau' # change this to your username

engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

years = model.getYears()

year=2017
pointsByRound=[1,2,4,8,16,32]
poolSizes=np.arange(5,101,5)

@app.route('/')
# @app.route('/index')
@app.route('/year/<int:year>')
def index(year=2017):
        tourney = model.Tournament(year=year)
        bracket=tourney.simulate()

        initialBracket={1: bracket[1], 2: ['']*32, 3: ['']*16, 4: ['']*8, 5: ['']*4, 6: ['']*2, 7: ['']*1}
        risk = 0.4
        poolSize=25
        return render_template("bracket.html",
           risk=risk,
           poolSizes=poolSizes,
           poolSize=poolSize,
           newBracket=initialBracket,
           firstBracket=initialBracket,
           secondBracket=initialBracket,
           bracketOutcome=tourney.bracketOutcome,
           year = year, years = years,
           payout=[0,0,0,0],
           ptile0=[0,0,0,0],
           ptile1=[0,0,0,0],
           bustPCT = '1',
           points=[0,0])

@app.route('/actualBracket/<int:year>')
def actualBracket(year=2017):
    tourney = model.Tournament(year=year)
    return render_template("bracket_template.html",
       bracket=tourney.bracketOutcome, year = year, years = years)


@app.route('/')
@app.route('/year/<int:year>')
def generate(year=2017,risk=0.3,poolSize=25):
    tourney = model.Tournament(year=year)
    bracket=tourney.simulate()
    poolList=[]
    pool=model.Pool(tourney,poolSize=poolSize,risk=risk,payoutPct=[.7,.2,.1])
    pool.loadTourneySets()

    pool.getGoodBracket(verbose=True)
    pointBackTest1=model.compareBrackets(pool.summary['favBracket'],pool.tourney.bracketOutcome,pool.pointSystem)
    pointBackTest2=model.compareBrackets(pool.summary['newBracket'],pool.tourney.bracketOutcome,pool.pointSystem)

    return render_template("bracket.html",risk=risk,
       poolSizes=poolSizes,poolSize=poolSize,
       newBracket=pool.summary['newBracket'],
       firstBracket=pool.summary['favBracket'],
       secondBracket=pool.summary['newBracket'],
       # bracketOutcome={},
       bracketOutcome = pool.tourney.bracketOutcome,
       year = year, years = years,
       payout=list(pool.summary['expPayout'].tolist()),
       ptile0=list(pool.summary['expPlace'][:,0].tolist()),
       ptile1=list(pool.summary['expPlace'][:,1].tolist()),
       bustPCT = pool.summary['bustPCT'],
       points=[pointBackTest1,pointBackTest2])


@app.route('/set_parms', methods=['GET', 'POST'])
def setParms():
    data = request.args
    # print(data)
    riskLevel = float(data['risk'])#0.4
    print('RL: ',riskLevel)
    year = int(data['year'])
    poolSize = int(data['poolSize'])
    if poolSize > poolSizes.max():
        poolSize = poolSizes.max()
    return generate(year,risk=riskLevel,poolSize=poolSize)


@app.route('/contact')
def contact():
    return render_template("contact.html")

# @app.route('/pointSystem')
# def pointSystem():
#     return render_template("point_system.html")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

# @app.errorhandler(500)
# def page_not_found(error):
#     return render_template('/')
