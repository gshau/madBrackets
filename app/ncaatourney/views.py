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
    viewData = fetchTeam(year)
    return render_template("bracket_template.html",
       data = viewData, year = year, years = years)
