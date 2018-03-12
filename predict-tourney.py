import csv
from operator import attrgetter

resultsDict = {}
teamsDict = {}
seedsDict = {}
regularSeasonResults = {}
yearTeamSeed = {}
# dataDir = '/vagrant/spark/data/'
# dataDir = '/Users/david/sila/marchmadness/data/'
dataDir = '/Users/david/Downloads/'

with open(dataDir+'RegularSeasonCompactResults.csv') as seasonResultsFile:
    seasonResultsReader = csv.reader(seasonResultsFile, delimiter=',')
    seasonResultsReader.next()
    for game in seasonResultsReader:
        year = game[0]
        daynum = int(game[1])
        wteam = game[2]
        wscore = int(game[3])
        lteam = game[4]
        lscore = int(game[5])
        wloc = game[6]
        numot = int(game[7])
        wrating = float(wscore)/float(wscore+lscore)
        regularSeasonResults[year] = regularSeasonResults.get(year,{})
        rsry = regularSeasonResults[year]
        rsry[wteam] = rsry.get(wteam,{'games': [], 'opponents': set()})
        rsry[lteam] = rsry.get(lteam,{'games': [], 'opponents': set()})
        rsry[wteam]['games'].append({
                "daynum": daynum,
                "opp": lteam,
                "score": wscore,
                "oscore": lscore,
                "loc": wloc,
                "numot": numot
            })
        rsry[wteam]['opponents'].add(lteam)
        lloc = 'H' if wloc == 'A' else 'A' if wloc == 'H' else 'N'
        rsry[lteam]['games'].append({
                "daynum": daynum,
                "opp": wteam,
                "score": lscore,
                "oscore": wscore,
                "loc": lloc,
                "numot": numot
            })
        rsry[lteam]['opponents'].add(wteam)


with open(dataDir+'Teams.csv') as teamsFile:
    teamsReader = csv.reader(teamsFile, delimiter=',')
    teamsReader.next() # skip header
    for teamsRow in teamsReader:
        teamsDict[teamsRow[0]] = teamsRow[1]


with open(dataDir+'TourneyCompactResults.csv') as resultsFile:
    resultsReader = csv.reader(resultsFile, delimiter=',')
    resultsReader.next() # skip header
    for result in resultsReader:
        year = result[0]
        wteam = result[2]
        lteam = result[4]
        resultsDict[year] = resultsDict.get(year,{})
        resultsDict[year][wteam] = resultsDict[year].get(wteam,set())
        resultsDict[year][wteam].add(lteam)

with open(dataDir+'TourneySeeds.csv') as seedsFile:
    seedsReader = csv.reader(seedsFile, delimiter=',')
    seedsReader.next()
    seedMap = [1,16,8,9,4,13,5,12,3,14,6,11,7,10,2,15]

    playIn = False
    row = -1
    for seedRow in seedsReader:
        year = seedRow[0]
        seed = seedRow[1]
        team = seedRow[2]
        seedsDict[year] = seedsDict.get(year,[None]*64)
        seed_int = int(seed[1:3])
        index = seedMap.index(seed_int)
        yearTeamSeed[year] = yearTeamSeed.get(year,{})
        yearTeamSeed[year][team]=seed_int
        row = (row+1)%4 if seed_int is 1 else row
        if playIn:
            seedsDict[year][row*16+index] = team if team in resultsDict[year] else playInTeam
            playIn = False
        elif seed.endswith('a'):
            playIn = True
            playInTeam = team
        else:
            seedsDict[year][row*16+index] = team

class ResultGetter:
    def __init__(self, results):
        self.results = results
    
    def calculateGame(self, team1, team2):
        return team1 if team1 in self.results and team2 in self.results[team1] else team2

class AdvancedStats:
    def __init__(self, rsry, stat):
        self.rsry = rsry
        self.stat = stat
    
    def calculateGame(self, team1, team2):
        return team1 if self.rsry[team1][stat] > self.rsry[team2][stat] else team2



def calculateGame(team1, team2):
    return team1

def getResult(team1, team2):
    return team2 in results[team1]

def calculateRound(teams, gameCalculator):
    nextRound = []
    for i in range(len(teams)/2):
        # nextRound.append()
        team1 = teams[i*2]
        team2 = teams[i*2+1]
        nextRound.append(gameCalculator(team1,team2))
    return nextRound

def buildActualBracket(tourney):
    for i in range(len(teams)/2):
        nextRound.append()

def calculateTournament(teams,gameCalculator):
    tourney = []
    for round in range(6):
        teams = calculateRound(teams, gameCalculator)
        tourney.append(teams)
    return tourney

def printBracketFromIds(bracket, teamsDict, teamSeed):
    for round in bracket:
        readableRound = []
        for teamId in round:
            readableRound.append(str(teamSeed[teamId])+' '+teamsDict[teamId])
        print readableRound

def scoreBrackets(actual, predicted, teamSeeds):
    score = 0
    multiplier = 1
    for actualRound, predictedRound in zip(actual, predicted):
        for a, p in zip(actualRound, predictedRound):
            if a==p:
                score+=multiplier
                if teamSeeds:
                    score+=teamSeeds[a]
        multiplier *= 2
    return score

def scoreBracketsNoMultiplier(actual, predicted, teamSeeds):
    score = 0
    for actualRound, predictedRound in zip(actual, predicted):
        for a, p in zip(actualRound, predictedRound):
            if a==p:
                score+=1
                if teamSeeds:
                    score+=teamSeeds[a]
    return score

def updateSecondAndThirdOrder(team, statName, ratingName, oppRatingName, oppOppRatingName):
    team['secondOrder'+statName] = team[ratingName]/2.0+team[oppRatingName]/4.0
    team['thirdOrder'+statName] = team[ratingName]/2.0+team[oppRatingName]/4.0+team[oppOppRatingName]/8.0

def calculateStatistics(rsry):
    for teamId, team in rsry.items():
        daySum = 0
        for game in team['games']:
            daySum = daySum+game['daynum']
            game['rawRating'] = game['score']/float(game['score']+game['oscore'])
            game['pythRating'] = float(game['score']*game['score'])/float(game['score']*game['score']+game['oscore']*game['oscore'])
            team['rawRatingSum'] = (team.get('rawRatingSum',0.0)+game['rawRating'])
            team['pythRatingSum'] = (team.get('pythRatingSum',0.0)+game['pythRating'])
            team['rawRatingSumDayWeight'] = team.get('rawRatingSumDayWeight',0.0)+game['rawRating']*game['daynum']
            team['pythRatingSumDayWeight'] = team.get('pythRatingSumDayWeight',0.0)+game['pythRating']*game['daynum']

        team['daySum'] = daySum
        team['rawRatingAvg'] = team['rawRatingSum']/len(team['games'])
        team['pythRatingAvg'] = team['pythRatingSum']/len(team['games'])
        team['rawRatingAvgDayWeight'] = team['rawRatingSumDayWeight']/daySum
        team['pythRatingAvgDayWeight'] = team['pythRatingSumDayWeight']/daySum
    for teamId, team in rsry.items():
        uniqueOppOfOppGameCount = 0
        uniqueOppOfOppDaySum = 0
        for game in team['games']:
            oppRawRating = rsry[game['opp']]['rawRatingAvg']
            oppPythRating = rsry[game['opp']]['pythRatingAvg']
            team['oppRawRatingSum'] = team.get('oppRawRatingSum',0.0)+oppRawRating
            team['oppPythRatingSum'] = team.get('oppPythRatingSum',0.0)+oppPythRating
            team['oppRawRatingSumDayWeight'] = team.get('oppRawRatingSumDayWeight',0.0)+oppRawRating*game['daynum']
            team['oppPythRatingSumDayWeight'] = team.get('oppPythRatingSumDayWeight',0.0)+oppPythRating*game['daynum']

            team['oppAgainstNonOppSum'] = team.get('oppAgainstNonOppSum',0.0)
            oneOppSum = 0.0
            count = 0.0
            for oppGame in rsry[game['opp']]['games']:
                if oppGame['opp'] != teamId and oppGame['opp'] not in team['opponents']:
                    count += 1
                    oneOppSum += oppGame['rawRating']
            if count > 0:
                uniqueOppOfOppGameCount+=1
                uniqueOppOfOppDaySum += game['daynum']
                team['oppAgainstNonOppSum'] = team.get('oppAgainstNonOppSum',0.0)+oneOppSum/count
                team['oppAgainstNonOppSumDayWeight'] = team.get('oppAgainstNonOppSumDayWeight',0.0)+(oneOppSum/count)*game['daynum']

        team['oppRawRatingAvg'] = team['oppRawRatingSum']/len(team['games'])
        team['oppRawRatingAvgDayWeight'] = team['oppRawRatingSumDayWeight']/team['daySum']
        team['oppPythRatingAvg'] = team['oppPythRatingSum']/len(team['games'])
        team['oppPythRatingAvgDayWeight'] = team['oppPythRatingSumDayWeight']/team['daySum']
        team['oppAgainstNonOppAvg'] = team['oppAgainstNonOppSum']/uniqueOppOfOppGameCount
        team['oppAgainstNonOppAvgDayWeight'] = team['oppAgainstNonOppSumDayWeight']/uniqueOppOfOppDaySum
    for teamId, team in rsry.items():
        for game in team['games']:
            oppOppRawRating = rsry[game['opp']]['oppRawRatingAvg']
            oppOppPythRating = rsry[game['opp']]['oppPythRatingAvg']
            team['oppOppRawRatingSum'] = team.get('oppOppRawRatingSum',0.0)+oppOppRawRating
            team['oppOppPythRatingSum'] = team.get('oppOppPythRatingSum',0.0)+oppOppPythRating
            team['oppOppRawRatingSumDayWeight'] = team.get('oppOppRawRatingSumDayWeight',0.0)+oppOppRawRating*game['daynum']
            team['oppOppPythRatingSumDayWeight'] = team.get('oppOppPythRatingSumDayWeight',0.0)+oppOppPythRating*game['daynum']
            team['oppOppAgainstNonOppSum'] = team.get('oppOppAgainstNonOppSum',0.0)+rsry[game['opp']]['oppAgainstNonOppAvg']
            team['oppOppAgainstNonOppSumDayWeight'] = team.get('oppOppAgainstNonOppSumDayWeight',0.0)+rsry[game['opp']]['oppAgainstNonOppAvg']*game['daynum']

        team['oppOppRawRatingAvg'] = team['oppOppRawRatingSum']/len(team['games'])
        team['oppOppPythRatingAvg'] = team['oppOppPythRatingSum']/len(team['games'])
        team['oppOppRawRatingAvgDayWeight'] = team['oppOppRawRatingSumDayWeight']/team['daySum']
        team['oppOppPythRatingAvgDayWeight'] = team['oppOppPythRatingSumDayWeight']/team['daySum']
        team['oppOppAgainstNonOppAvg'] = team['oppOppAgainstNonOppSum']/len(team['games'])
        team['oppOppAgainstNonOppAvgDayWeight'] = team['oppOppAgainstNonOppSumDayWeight']/team['daySum']

        updateSecondAndThirdOrder(team,'Raw','rawRatingAvg','oppRawRatingAvg','oppOppRawRatingAvg')
        updateSecondAndThirdOrder(team,'RawByDay','rawRatingAvgDayWeight','oppRawRatingAvgDayWeight','oppOppRawRatingAvgDayWeight')
        updateSecondAndThirdOrder(team,'Pyth','pythRatingAvg','oppPythRatingAvg','oppOppPythRatingAvg')
        updateSecondAndThirdOrder(team,'PythByDay','pythRatingAvgDayWeight','oppPythRatingAvgDayWeight','oppOppPythRatingAvgDayWeight')
        updateSecondAndThirdOrder(team,'RawFancy','rawRatingAvg','oppAgainstNonOppAvg','oppOppAgainstNonOppAvg')
        updateSecondAndThirdOrder(team,'RawFancyByDay','rawRatingAvgDayWeight','oppAgainstNonOppAvgDayWeight','oppOppAgainstNonOppAvgDayWeight')


def updateScoreTuple(stat, predicted, actual, scoreDict, teamSeed):
    scoreDict[stat] = scoreDict.get(stat,{})
    scoreDict[stat]['unweighted'] = scoreDict[stat].get('unweighted',0)
    scoreDict[stat]['weighted'] = scoreDict[stat].get('weighted',0)
    scoreDict[stat]['unweightedWithBonus'] = scoreDict[stat].get('unweightedWithBonus',0)
    scoreDict[stat]['weightedWithBonus'] = scoreDict[stat].get('weightedWithBonus',0)
    scoreDict[stat]['unweighted'] = scoreDict[stat]['unweighted']+scoreBracketsNoMultiplier(actual,predicted,None)
    scoreDict[stat]['weighted'] = scoreDict[stat]['weighted']+scoreBrackets(actual,predicted,None)
    scoreDict[stat]['unweightedWithBonus'] = scoreDict[stat]['unweightedWithBonus']+scoreBracketsNoMultiplier(actual,predicted,teamSeed)
    scoreDict[stat]['weightedWithBonus'] = scoreDict[stat]['weightedWithBonus']+scoreBrackets(actual,predicted,teamSeed)




scoresByAlgorithm = {}
stats = ['pythRatingAvg','pythRatingAvgDayWeight','rawRatingAvg','rawRatingAvgDayWeight','oppOppRawRatingAvg','oppOppPythRatingAvg','oppOppRawRatingAvgDayWeight','oppOppPythRatingAvgDayWeight','secondOrderRaw','thirdOrderRaw','secondOrderRawByDay','thirdOrderRawByDay','secondOrderPyth','secondOrderPythByDay','thirdOrderPyth','thirdOrderPythByDay','secondOrderRawFancy','thirdOrderRawFancy','secondOrderRawFancyByDay','thirdOrderRawFancyByDay']
for year, seeds in seedsDict.items():
    calculateStatistics(regularSeasonResults[year])
    if year != '2017':
        boring = calculateTournament(seeds,calculateGame)
        rg = ResultGetter(resultsDict[year])
        actual = calculateTournament(seeds,rg.calculateGame)
        updateScoreTuple('actual', actual, actual, scoresByAlgorithm, yearTeamSeed[year])
        updateScoreTuple('boring', boring, actual, scoresByAlgorithm, yearTeamSeed[year])
        for stat in stats:
            advancedStatsCalculator = AdvancedStats(regularSeasonResults[year],stat)
            predicted = calculateTournament(seeds,advancedStatsCalculator.calculateGame)
            # printBracketFromIds(predicted, teamsDict)
            updateScoreTuple(stat, predicted, actual, scoresByAlgorithm, yearTeamSeed[year])

def printScoresForSystem(key):
    for y in sorted(scoresByAlgorithm.items(), key=lambda x: x[1][key]):
        print y[0]+" "+key+" "+str(y[1][key]/32.0)

printScoresForSystem('weighted')
printScoresForSystem('unweighted')
printScoresForSystem('weightedWithBonus')


stat = 'thirdOrderRawFancyByDay'
year = '2017'
advancedStatsCalculator = AdvancedStats(regularSeasonResults[year],stat)
bracket = calculateTournament(seedsDict[year],advancedStatsCalculator.calculateGame)

printBracketFromIds(bracket, teamsDict, yearTeamSeed[year])


for teamId, team in sorted(regularSeasonResults[year].items(), key=lambda team: team[1][stat]):
    print teamsDict[teamId]+" "+str(team[stat])


