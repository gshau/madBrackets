# Mad-Brackets!  
This repository contains both the exploratory analysis and web-app (under server) for Mad-Brackets!, a tool for choosing March Madness brackets that attempts to minimize risk based on machine learning of historical tournament data.  Project created as a Fellow at the Insight Data Science remote program 2018-A.  

#### The Mad-Brackets! site is now live <a href="http://mad-brackets.com">here</a>!



## This repo contains several exploratory Jupyter notebooks and the evolving web application.  

Brief summary of these notebooks:
- pullNCAAData_*: various scripts for web-scraping sports-reference.com and kenpom.com
- tournamentScraper: Scraping of NCAA tournament games
- initMadBrackets: initialize postgresql database from scraped data
- teamAnalysis: exploratory analysis of team features
- gameAnalysis: prediction of games with various models.  
- fitDispersionPicks: fit prediction of games to survival odds in ESPN bracket challenge
- modelTesting: Testbed for creating model
- appModelTesting: test-bed for interfacing with model used on web app


Currently a work in progress!
