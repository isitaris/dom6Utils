import matplotlib.pyplot as plt
import matplotlib.colors
import random as rand
import numpy as np
import math
import explodingDice as DRN
from matplotlib.lines import Line2D
import os
import matplotlib.ticker as mtick

#ceiling division: if a = qb + r when euclidian dividing by b, returns q+1
def ceildiv(a, b): 
    return -(a // -b)

# to-do list: 
#    - THINK ABOUT how to show squad size in histograms; maybe check if it has an effect with a graph, and if not say that we can thus play with squads of arbitrary size, and we choose one that's not too big to help with CPU (if yes RIP, gonna have to be clever)
#           it looks like routing of high morale units under wailing winds only really depends highly on squad size: low size squads take longer to rout; luckily, looks like there might be a size above which it doesn't change much anymore (30-40?) so maybe use 50 as standard size; see once more stats are available
#    - do fear aura I guess as well, assuming line vs line
#    - try and calculate variance and show it in plots
#    - try and add back a simulation for run 2 (ww and ww+bloodrain) and compare to new ones
#    - make it 50/50 which of wailing winds or blood rain goes first; I don't think it's very important to be honest
#    - DONE I THINK? TO BE RE_READ: add modelling of the loss of the bonus of 4 to morale check (i would need to make sure that routed units count as killed units)
#    - DONE I THINK? TO BE RE_READ: add modelling of the effect of blood rain on squad that go below size 5
#    - DONE: check whether blood rain can rout commanders by itself; answer: yes
#    - DONE: check what happens if morale malus is above unit's morale; answer: looks like negative morale after maluses are taken into account


# graphics suggestions: 
#    - DONE: use % instead of proba for easier access by people
#    - DONE: alternate half and full lines


# globals effects (values gotten by asking Loggy): 
# wailing winds: 3% of battlefield every 320 ticks, full fear effect if fail weird morale check (resists == openended 3d6 < current morale), max penalty -5
# blood rain 3% of battlefield every 320 ticks, frighten effect, max penalty -5, won't cause rout by itself for the squad scenario, but will for lone commanders 



#######################################################################
########################### global settings ###########################
#######################################################################

wailingHitRate = 3
rainHitRate = 3
fullFearMalusLimit = 5 # maximum morale malus from wailing winds
frightenMalusLimit = 5 # maximum morale malus from blood rain

DOM5_wailingHitRate = 5



##############################################################################
########################### morale check functions ###########################
##############################################################################

def moraleDomAverage(squadSize, unitMorale, moraleMalus): 
    totalMorale = 0
    for unitID in range(squadSize):
        totalMorale += unitMorale - moraleMalus[unitID]
    return ((squadSize // 2) + totalMorale) // squadSize #https://illwiki.com/dom5/user/loggy/morale

def moraleCheckFailureStandard_commanders(unitMorale, moraleMalus):
    # note: the value of 5 is in fact the morale bonus 5*squadSize/squadSize; the "base morale bonus" is 0 because "The number of alive units in the squad is less than or equal to a closed d4, AND the highest number of morale problems is greater than or equal to half the number of alive units in the squad" (https://illwiki.com/dom5/user/loggy/morale)
    if (5 + unitMorale + DRN.DRN() < 14 + moraleMalus + DRN.DRN()):
        return True
    else:
        return False

def moraleCheckFailureStandard_squad(averageMorale, squadSize, squadMoraleBonus):
    # note: the value 4 on the left-hand side is a bonus that becomes 0 if the squad becomes too beaten up (exact conditions in https://illwiki.com/dom5/user/loggy/morale);
    # loss of this bonus is not modelled here 
    if (squadMoraleBonus + averageMorale + (squadSize // 2 + squadSize*5) // squadSize + DRN.DRN() < 14 + DRN.DRN()):
        return True
    else:
        return False

def moraleCheckFailureIndividual(unitMorale, moraleMalus):
    if (unitMorale + DRN.DRN() < 6 + moraleMalus + DRN.DRN()):
        return True
    else:
        return False

def moraleCheckFailureWailingWindsNegation(unitMorale, moraleMalus):
    if (DRN.DRN_triple() < max(unitMorale - moraleMalus, 0)):
        return False
    else:
        return True




#################################################################################
########################### single battle simulations ###########################
#################################################################################

def wailingBattleSim_commanders(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, debug = 0):
    tickCount = 0
    roundCountCurrent = 0
    roundCountNew = 0
    moraleCheckCount = 0 # one morale check per turn maximum - monitors this
    moraleCheckCount_easier = 0 # one morale check per turn maximum - monitors this
    unitHasRouted = False
    moraleMalus = 0
    while unitHasRouted == False: 
        tickCount += 320
        roundCountNew = tickCount // 7500

        # Blood Rain effect if active
        if bloodRainActive == 1:
            if rand.randrange(100) < rainHitRate: #chance for Blood rain to hit the commander square: rainHitRate% every 320 ticks
                if moraleMalus < frightenMalusLimit:
                    moraleMalus += 1
                if moraleCheckCount == 0 and moraleCheckFailureStandard_commanders(unitMorale, moraleMalus):
                    unitHasRouted = True
                moraleCheckCount = 1

        # Wailing Winds effect
        if wailingWindsActive == 1:
            if rand.randrange(100) < wailingHitRate: #chance for Wailing winds to hit the commander square: wailingHitRate% every 320 ticks
                if moraleCheckFailureWailingWindsNegation(unitMorale, moraleMalus): # units get a morale check to avoid being affected by wailing winds
                    if moraleMalus < fullFearMalusLimit:
                        moraleMalus += 1
                    if moraleCheckCount == 0 and moraleCheckFailureStandard_commanders(unitMorale, moraleMalus):
                        unitHasRouted = True
                    moraleCheckCount = 1
                    if moraleCheckCount_easier == 0 and moraleCheckFailureIndividual(unitMorale, moraleMalus):
                        unitHasRouted = True
                    moraleCheckCount_easier = 1

        # new round, chance of morale malus to decay, and wailing winds will be able to try a rout one more time
        if roundCountNew > roundCountCurrent:
            if rand.randrange(100) < 50: # 50% chance of the morale malus being reduced by 1 every round
                moraleMalus = max(moraleMalus - 1, 0)
            moraleCheckCount = 0
            moraleCheckCount_easier = 0
            if debug == 1:
                print(moraleMalus)
        roundCountCurrent = tickCount // 7500

        # end of battle, unit hasn't routed yet (this is dom5 number, gotta check new dom6 end of turn stuff)
        if roundCountCurrent > 100: # turn 100: battle enchantents end
            unitHasRouted = True

            roundCountCurrent = 130 #debug value
    return roundCountCurrent

def wailingBattleSim_squad(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, squadSize = 1, unitDensity = 1, debug = 0):
    tickCount = 0
    roundCountCurrent = 0
    roundCountNew = 0
    unitHasRouted = np.zeros(squadSize, dtype=bool)
    moraleMalus = np.zeros(squadSize)
    moraleCheckCount = 0 # one morale check per unit per turn maximum - monitors this ; this one is shared by whole squad
    moraleCheckCount_easier = np.zeros(squadSize) # one morale check per unit per turn maximum - monitors this
    unitMoraleProblems = np.zeros(squadSize) # see morale problems in https://illwiki.com/dom5/user/loggy/morale ; only counts the 1000 ones, not the finer details, should be enough
    squadSquareSize = ceildiv(squadSize, unitDensity) # how many squares deos the squad cover
    unitRoutRound = np.zeros(squadSize) # turn at which the unit routed
    unitRoutCount = 0 # how many units have routed so far
    squadMoraleBonus = 4 # is 4 by default, unless squad size is small
    while not np.all(unitHasRouted):
        tickCount += 320
        roundCountNew = tickCount // 7500

        for squadSquare_i in range(squadSquareSize):
            # Blood Rain effect if active
            if bloodRainActive == 1:
                if rand.randrange(100) < rainHitRate: #chance for Blood rain to hit the unit's square: rainHitRate% every 320 ticks
                    for j in range(unitDensity):
                        if squadSquare_i*unitDensity + j >= squadSize: 
                            continue #the unit does not exist, its ID is beyond the number of unit defined with squadSize
                        unitID = squadSquare_i*unitDensity + j
                        if moraleMalus[unitID] < frightenMalusLimit:
                            moraleMalus[unitID] += 1

                        unitMoraleProblems[:] += 1
                        unitMoraleProblems[unitID] += 1

                        # squad survival ratio check
                        if ((unitRoutCount <= squadSize*80//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 8)  or
                                (unitRoutCount <= squadSize*75//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 10) or
                                (unitRoutCount <= squadSize*70//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 11) or
                                (unitRoutCount <= squadSize*60//100 and np.sum(unitMoraleProblems) > squadSize//2) or
                                (unitRoutCount <= squadSize*30//100 and np.sum(unitMoraleProblems) >= 0)):
                            squadMoraleBonus = 0
                            unitMoraleProblems[:] = 10000

                        if squadSize <= rand.randrange(4)+1 and np.sum(unitMoraleProblems) >= squadSize//2:
                            squadMoraleBonus = 0
                            squadAttemptsRout = True

                        if np.max(unitMoraleProblems) >= 10000:
                            squadAttemptsRout = True

                        if squadAttemptsRout == True: 
                            if moraleCheckCount == 0 and unitHasRouted[unitID] == False and moraleCheckFailureStandard_squad(moraleDomAverage(squadSize, unitMorale, moraleMalus), squadSize, squadMoraleBonus): # This is not a true average, but in fact is rather %%((number of alive units in squad / 2) + total morale) / number of alive units (https://illwiki.com/dom5/user/loggy/morale)
                                unitHasRouted[:] = True
                                unitRoutRound[:] = roundCountNew
                                if debug == 1:
                                    print("big fear routs whole squad at round "+str(roundCountNew)+"----------------")
                            moraleCheckCount = 1

                        #resetting variables at end of iteration
                        squadAttemptsRout = False
                        squadmoralebonus = 4

            # Wailing Winds effect
            if wailingWindsActive == 1:
                if rand.randrange(100) < wailingHitRate: #chance for Wailing winds to hit the unit's square: wailingHitRate% every 320 ticks
                    for j in range(unitDensity):
                        if squadSquare_i*unitDensity + j >= squadSize: 
                            continue #the unit does not exist, its ID is beyond the number of unit defined with squadSize
                        unitID = squadSquare_i*unitDensity + j
                        if moraleCheckFailureWailingWindsNegation(unitMorale, moraleMalus[unitID]): # units get a morale check to avoid being affected by wailing winds
                            if moraleMalus[unitID] < fullFearMalusLimit:
                                moraleMalus[unitID] += 1

                            if moraleCheckCount_easier[unitID] == 0 and unitHasRouted[unitID] == False and moraleCheckFailureIndividual(unitMorale, moraleMalus[unitID]):
                                unitHasRouted[unitID] = True
                                unitRoutRound[unitID] = roundCountNew
                                if debug == 1:
                                    print("big fear routs unit "+str(unitID)+" at round "+str(roundCountNew))

                            moraleCheckCount_easier[unitID] = 1

                            unitMoraleProblems[:] += 1000
                            unitMoraleProblems[unitID] += 1000

                            # squad survival ratio check
                            if ((unitRoutCount <= squadSize*80//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 8)  or
                                    (unitRoutCount <= squadSize*75//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 10) or
                                    (unitRoutCount <= squadSize*70//100 and np.sum(unitMoraleProblems) > squadSize//2 and moraleDomAverage(squadSize, unitMorale, moraleMalus) <= 11) or
                                    (unitRoutCount <= squadSize*60//100 and np.sum(unitMoraleProblems) > squadSize//2) or
                                    (unitRoutCount <= squadSize*30//100 and np.sum(unitMoraleProblems) >= 0)):
                                squadMoraleBonus = 0
                                unitMoraleProblems[:] = 10000

                            if squadSize <= rand.randrange(4)+1 and np.sum(unitMoraleProblems) >= squadSize//2:
                                squadMoraleBonus = 0
                                squadAttemptsRout = True

                            if np.max(unitMoraleProblems) >= 10000:
                                squadAttemptsRout = True

                            if squadAttemptsRout == True: 
                                if moraleCheckCount == 0 and unitHasRouted[unitID] == False and moraleCheckFailureStandard_squad(moraleDomAverage(squadSize, unitMorale, moraleMalus), squadSize, squadMoraleBonus): # This is not a true average, but in fact is rather %%((number of alive units in squad / 2) + total morale) / number of alive units (https://illwiki.com/dom5/user/loggy/morale)
                                    unitHasRouted[:] = True
                                    unitRoutRound[:] = roundCountNew
                                    if debug == 1:
                                        print("big fear routs whole squad at round "+str(roundCountNew)+"----------------")
                                moraleCheckCount = 1

                            #resetting variables at end of iteration
                            squadAttemptsRout = False
                            squadmoralebonus = 4


        # new round, chance of morale malus to decay, and wailing winds will be able to try a rout one more time
        if roundCountNew > roundCountCurrent:
            for unitID in range(squadSize):
                if rand.randrange(100) < 50: # 50% chance of the morale malus being reduced by 1 every round
                    moraleMalus[unitID] = max(moraleMalus[unitID] - 1, 0)
            moraleCheckCount = 0
            moraleCheckCount_easier[:] = 0
            unitMoraleProblems[:] = 0 #reset every round after the fear checks above according to loggy
            if debug == 1:
                print(moraleMalus)
        roundCountCurrent = tickCount // 7500
        # end of battle, unit hasn't routed yet (this is dom5 number, gotta check new dom6 end of turn stuff)
        if roundCountCurrent > 100: # turn 100: battle enchantents end
            roundCountCurrent = 130 #debug value
            # unitHasRouted = np.ones(squadSize, dtype=bool)
            for unitID in range(squadSize):
                if unitHasRouted[unitID] == False:
                    unitHasRouted[unitID] = True
                    unitRoutRound[unitID] = roundCountCurrent
    if debug == 1:
        print("sim ends at round "+str(roundCountCurrent)+" with unitRoutRound = "+str(unitRoutRound))
    return unitRoutRound

def FearMoraleMalusSim(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, debug = 0):
    battleHasEnded = False
    tickCount = 0
    roundCountCurrent = 0
    roundCountNew = 0
    moraleMalus = 0

    nRounds = 100
    moraleMalusArray = np.zeros(nRounds)
    moraleMalusArray[0] = 0
    while not battleHasEnded:
        tickCount += 320
        roundCountNew = tickCount // 7500

        # Blood Rain effect if active
        if bloodRainActive == 1:
            if rand.randrange(100) < rainHitRate: #chance for Blood rain to hit the unit's square: rainHitRate% every 320 ticks
                if moraleMalus < frightenMalusLimit:
                    moraleMalus += 1

        # Wailing Winds effect
        if wailingWindsActive == 1:
            if rand.randrange(100) < wailingHitRate: #chance for Wailing winds to hit the unit's square: wailingHitRate% every 320 ticks
                if moraleCheckFailureWailingWindsNegation(unitMorale, moraleMalus): # units get a morale check to avoid being affected by wailing winds
                    if moraleMalus < fullFearMalusLimit:
                        moraleMalus += 1

        # new round, chance of morale malus to decay, and wailing winds will be able to try a rout one more time
        if roundCountNew > roundCountCurrent:
            moraleMalusArray[roundCountNew] = moraleMalus
            if rand.randrange(100) < 50: # 50% chance of the morale malus being reduced by 1 every round
                moraleMalus = max(moraleMalus - 1, 0)
            if debug == 1:
                print(moraleMalus)
        roundCountCurrent = tickCount // 7500
        # end of battle, unit hasn't routed yet (this is dom5 number, gotta check new dom6 end of turn stuff)
        if roundCountCurrent > 98: # turn 100: battle enchantents end
            roundCountCurrent = 130 #debug value
            battleHasEnded = True
    if debug == 1:
        print("sim ends at round "+str(roundCountCurrent)+" with moraleMalus = "+str(moraleMalus))
    return moraleMalusArray

# FearMoraleMalusSim(10, 1, 1, debug = 1)


# did I actually finish those DOM5 versions? to be checked
def DOM5_wailingBattleSim_commanders(unitMorale = 10, bloodRainActive = 0, debug = 0):
    tickCount = 0
    roundCountCurrent = 0
    roundCountNew = 0
    moraleCheckCount = 0 # one morale check per turn maximum - monitors this
    moraleCheckCount_easier = 0 # one morale check per turn maximum - monitors this
    unitHasRouted = False
    moraleMalus = 0
    while unitHasRouted == False: 
        tickCount += 320
        roundCountNew = tickCount // 7500

        # Blood Rain effect if active
        # if wailingWindsActive == 1: for DOM5 if wailing winds isn't active there is no rout check, so there would be no need for a simulation
        if rand.randrange(100) < DOM5_wailingHitRate: #chance for Blood rain to hit the commander square: rainHitRate% every 320 ticks
            if moraleMalus < frightenMalusLimit: # in DOM5 the morale malus caps at 5
                moraleMalus += 1
            if moraleCheckCount == 0 and moraleCheckFailureStandard_commanders(unitMorale, moraleMalus - (4 if bloodRainActive == 0 else 0)):
                unitHasRouted = True
            moraleCheckCount = 1

        # new round, chance of morale malus to decay, and wailing winds will be able to try a rout one more time
        if roundCountNew > roundCountCurrent:
            moraleMalus = moraleMalus // 2
            moraleCheckCount = 0
            if debug == 1:
                print(moraleMalus)
        roundCountCurrent = tickCount // 7500

        # end of battle, unit hasn't routed yet (this is dom5 number, gotta check new dom6 end of turn stuff)
        if roundCountCurrent > 100: # turn 100: battle enchantents end
            unitHasRouted = True

            roundCountCurrent = 130 #debug value
    return roundCountCurrent

# did I actually finish those DOM5 versions? to be checked
def DOM5_wailingBattleSim_squad(unitMorale = 10, bloodRainActive = 0, squadSize = 1, unitDensity = 1, debug = 0):
    tickCount = 0
    roundCountCurrent = 0
    roundCountNew = 0
    unitHasRouted = np.zeros(squadSize, dtype=bool)
    moraleMalus = np.zeros(squadSize)
    moraleCheckCount = 0 # one morale check per unit per turn maximum - monitors this ; this one is shared by whole squad
    moraleCheckCount_easier = np.zeros(squadSize) # one morale check per unit per turn maximum - monitors this
    unitMoraleProblems = np.zeros(squadSize) # see morale problems in https://illwiki.com/dom5/user/loggy/morale ; only counts the 1000 ones, not the finer details, should be enough
    squadSquareSize = ceildiv(squadSize, unitDensity) # how many squares deos the squad cover
    unitRoutRound = np.zeros(squadSize) # turn at which the unit routed
    while not np.all(unitHasRouted):
        tickCount += 320
        roundCountNew = tickCount // 7500

        for squadSquare_i in range(squadSquareSize):
            # Wailing Winds effect
            # if wailingWindsActive == 1: for DOM5 if wailing winds isn't active there is no rout check, so there would be no need for a simulation
            if rand.randrange(100) < DOM5_wailingHitRate: #chance for Wailing winds to hit the commander square: DOM5_wailingHitRate% every 320 ticks
                for j in range(unitDensity):
                    if squadSquare_i*unitDensity + j >= squadSize: 
                        continue #the unit does not exist, its ID is beyond the number of unit defined with squadSize
                    unitID = squadSquare_i*unitDensity + j
                    # if moraleCheckFailureWailingWindsNegation(unitMorale, moraleMalus[unitID]): # in DOM5 units do not get a morale check to avoid being affected by wailing winds
                    if moraleMalus[unitID] < frightenMalusLimit: # in DOM5 the morale malus caps at 5
                        moraleMalus[unitID] += 1

                    # in DOM5 there is no individual rout
                    # if moraleCheckCount_easier[unitID] == 0 and unitHasRouted[unitID] == False and moraleCheckFailureIndividual(unitMorale, moraleMalus[unitID]):
                    #     unitHasRouted[unitID] = True
                    #     unitRoutRound[unitID] = roundCountNew
                    #     if debug == 1:
                    #         print("big fear routs unit "+str(unitID)+" at round "+str(roundCountNew))

                    moraleCheckCount_easier[unitID] = 1

                    unitMoraleProblems[:] += 1000
                    unitMoraleProblems[unitID] += 1000

                    if np.max(unitMoraleProblems) >= 10000: # or 5 cases depending on surviving number of squad members; issue is those cases look at whether the unit is alive, not routed. So it's hard to check in a sim without fighting; maybe ignore for now
                        if moraleCheckCount == 0 and unitHasRouted[unitID] == False and moraleCheckFailureStandard_squad(moraleDomAverage(squadSize, unitMorale, moraleMalus), squadSize, squadMoraleBonus): # This should not be a true average, but in fact is rather %%((number of alive units in squad / 2) + total morale) / number of alive units (https://illwiki.com/dom5/user/loggy/morale)
                            unitHasRouted[:] = True
                            unitRoutRound[:] = roundCountNew
                            if debug == 1:
                                print("big fear routs whole squad at round "+str(roundCountNew)+"----------------")
                        moraleCheckCount = 1

        # new round, chance of morale malus to decay, and wailing winds will be able to try a rout one more time
        if roundCountNew > roundCountCurrent:
            for unitID in range(squadSize):
                moraleMalus[unitID] = moraleMalus[unitID] // 2
            moraleCheckCount = 0
            moraleCheckCount_easier[:] = 0
            unitMoraleProblems[:] = 0
            if debug == 1:
                print(moraleMalus)
        roundCountCurrent = tickCount // 7500
        # end of battle, unit hasn't routed yet (this is dom5 number, gotta check new dom6 end of turn stuff)
        if roundCountCurrent > 100: # turn 100: battle enchantents end
            roundCountCurrent = 130 #debug value
            # unitHasRouted = np.ones(squadSize, dtype=bool)
            for unitID in range(squadSize):
                if unitHasRouted[unitID] == False:
                    unitHasRouted[unitID] = True
                    unitRoutRound[unitID] = roundCountCurrent
    if debug == 1:
        print("sim ends at round "+str(roundCountCurrent)+" with unitRoutRound = "+str(unitRoutRound))
    return unitRoutRound



########################################################################################################################
########################### Making distributions by running battle simulations several times ###########################
########################################################################################################################


def wailingExpectedRout_commanders(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, nIteration = 1000):
    roundExpectedRout = 0
    for i in range(nIteration):
        if (i % 5000 == 0):
            print("nIteration done: " + str(i)) 
        routRound = wailingBattleSim_commanders(unitMorale, bloodRainActive, wailingWindsActive)
        roundExpectedRout+=routRound
    return 1./nIteration * roundExpectedRout

def makeWailingRoutDistrib_commanders(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, nIteration = 1000, isDOM5 = 0):
    routingTime = []
    for i in range(nIteration):
        if (i % 5000 == 0):
            print("nIteration done: " + str(i)) 
        if (isDOM5 == 0):
            routingTime = routingTime + [wailingBattleSim_commanders(unitMorale, bloodRainActive, wailingWindsActive)]
        else:
            routingTime = routingTime + [DOM5_wailingBattleSim_commanders(unitMorale, bloodRainActive, wailingWindsActive)]
    routingTime = np.array(routingTime)
    return routingTime

def makeWailingRoutDistrib_squad(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, squadSize = 1, unitDensity = 1, nIteration = 1000, isDOM5 = 0):
    nRounds = 100
    routedRatio = np.zeros(nRounds)
    for i in range(nIteration):
        if (i % 5000 == 0):
            print("nIteration done: " + str(i)) 
        if (isDOM5 == 0):
            unitRoutRound = np.array(wailingBattleSim_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity))
        else:
            unitRoutRound = np.array(DOM5_wailingBattleSim_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity))
        for round in range(nRounds):
            routedRatio[round] += (unitRoutRound <= round).sum() * 1./squadSize # sum of array of booleans (unitRoutRound =< round), then division by squad size
    routedRatio = routedRatio * 1./nIteration
    return routedRatio

def makeFearMoraleMalusAverageDistrib(unitMorale = 10, bloodRainActive = 0, wailingWindsActive = 1, nIteration = 1000):
    nRounds = 100
    moraleMalusAverage = np.zeros(nRounds)
    for i in range(nIteration):
        if (i % 5000 == 0):
            print("nIteration done: " + str(i))
        moraleMalusAverage += np.array(FearMoraleMalusSim(unitMorale, bloodRainActive, wailingWindsActive))
    moraleMalusAverage = moraleMalusAverage * 1./nIteration
    return moraleMalusAverage
# makeFearMoraleMalusAverageDistrib(10, 1, 0, 1000)



################################################################################################################
########################### Functions to plot distributions into a .pdf or .png file ###########################
################################################################################################################

def plotHistograms_commanders(nDistribs, routingTimeDistrib_collection, collectionLegend, pltTitle, pdfName, option = ""):

    nBins = 140
    fig, ax = plt.subplots()
    color1 = 'tab:red'
    ax.set_xlabel('Round number')
    ax.set_ylabel('Proba of being already routed (ie cumulative) in %')

    if option == "longCollection":
        colourMap = plt.get_cmap("viridis", nDistribs)
    else:
        colourMap = plt.get_cmap("copper", nDistribs)

    for i in range(nDistribs):
        if option == "longCollection":
            ax.hist(routingTimeDistrib_collection[i], nBins, label=collectionLegend[i], range=(0,nBins), density=True, cumulative=True, color=colourMap(i), histtype="step", linestyle=('solid' if i%2 == 0 else 'dashed'))
        else:
            ax.hist(routingTimeDistrib_collection[i], nBins, label=collectionLegend[i], range=(0,nBins), density=True, cumulative=True, color=colourMap(i), histtype="step")


    # Create new legend handles but use the colors from the existing ones
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) != nDistribs:
        raise ValueError('handles list should have length of nDistribs, it is not the case')
    if option == "longCollection":
        new_handles = [Line2D([], [], c=handles[i].get_edgecolor(), linestyle=('solid' if i%2 == 0 else 'dashed')) for i in range(nDistribs)]
    else:
        new_handles = [Line2D([], [], c=handles[i].get_edgecolor()) for i in range(nDistribs)]

    # plt.legend(handles=new_handles, labels=labels)

    ax.legend(handles=new_handles, labels=labels, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.label_outer()

    plt.xlim(xmin=0, xmax = 100)
    plt.ylim(ymin=0, ymax = 1.05)
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # transforms y-axis in % format

    plt.title(pltTitle)

    fig.tight_layout() # otherwise the right y-label is slightly clipped
    fig.tight_layout() # for some reason gotta call it twice for the top title to not be cropped


    # x-axis: major ticks every 20, minor ticks every 5
    major_ticks_x = np.arange(0, 101, 20)
    minor_ticks_x = np.arange(0, 101, 5)
    # y-axis: major ticks every 0.2, minor ticks every 0.05
    major_ticks_y = np.arange(0, 101, 20)*1./100
    minor_ticks_y = np.arange(0, 101, 5)*1./100

    ax.set_xticks(major_ticks_x)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(major_ticks_y)
    ax.set_yticks(minor_ticks_y, minor=True)

    ax.grid(which='both')

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # save figure in ./WailingWindsPlots/ folder ; if it  doesnt exist, create it
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, 'WailingWindsPlots/')
    results_dir_png = os.path.join(script_dir, 'WailingWindsPlots/pngPlots/')

    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    if not os.path.isdir(results_dir_png):
        os.makedirs(results_dir_png)

    if option == "debug":
        plt.show()
    plt.savefig(results_dir+pdfName+'.pdf')
    plt.savefig(results_dir_png+pdfName+'.png')
    

def plotHistograms_squad(nDistribs, routedRatioDistrib_collection, collectionLegend, pltTitle, pdfName, option = ""):

    fig, ax = plt.subplots()
    color1 = 'tab:red'
    ax.set_xlabel('Round number')
    ax.set_ylabel('Proportion of squad already routed in %')

    if option == "longCollection":
        colourMap = plt.get_cmap("viridis", nDistribs)
    else:
        colourMap = plt.get_cmap("copper", nDistribs)

    nRounds = 100 # x-axis bin size
    for i in range(nDistribs):
        if option == "longCollection":
            ax.plot(np.array(range(nRounds)), routedRatioDistrib_collection[i], label=collectionLegend[i], color=colourMap(i), linestyle=('solid' if i%2 == 0 else 'dashed'))
        else:
            ax.plot(np.array(range(nRounds)), routedRatioDistrib_collection[i], label=collectionLegend[i], color=colourMap(i))

    # Create new legend handles but use the colors from the existing ones
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) != nDistribs:
        raise ValueError('handles list should have length of nDistribs, it is not the case')
    if option == "longCollection":
        new_handles = [Line2D([], [], c=handles[i].get_color(), linestyle=('solid' if i%2 == 0 else 'dashed')) for i in range(nDistribs)]
    else:
        new_handles = [Line2D([], [], c=handles[i].get_color()) for i in range(nDistribs)]

    ax.legend(handles=new_handles, labels=labels, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.label_outer()

    plt.xlim(xmin=0, xmax = 100)
    plt.ylim(ymin=0, ymax = 1.05)
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # transforms y-axis in % format

    plt.title(pltTitle)

    fig.tight_layout() # otherwise the right y-label is slightly clipped
    fig.tight_layout() # for some reason gotta call it twice for the top title to not be cropped


    # setting up the grid and the ticks on the axes:

    # x-axis: major ticks every 20, minor ticks every 5
    major_ticks_x = np.arange(0, 101, 20)
    minor_ticks_x = np.arange(0, 101, 5)
    # y-axis: major ticks every 0.2, minor ticks every 0.05
    major_ticks_y = np.arange(0, 101, 20)*1./100
    minor_ticks_y = np.arange(0, 101, 5)*1./100

    ax.set_xticks(major_ticks_x)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(major_ticks_y)
    ax.set_yticks(minor_ticks_y, minor=True)

    ax.grid(which='both')

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # save figure in ./WailingWindsPlots/ folder ; if it  doesnt exist, create it
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, 'WailingWindsPlots/')
    results_dir_png = os.path.join(script_dir, 'WailingWindsPlots/pngPlots/')

    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    if not os.path.isdir(results_dir_png):
        os.makedirs(results_dir_png)

    if option == "debug":
        plt.show()
    plt.savefig(results_dir+pdfName+'.pdf')
    plt.savefig(results_dir_png+pdfName+'.png')

def plotHistograms_fearMoraleMalus(nDistribs, fearMoraleMalusDistrib_collection, collectionLegend, pltTitle, pdfName, option = ""):

    nBins = 140
    fig, ax = plt.subplots()
    color1 = 'tab:red'
    ax.set_xlabel('Round number')
    ax.set_ylabel('Morale malus')

    if option == "longCollection":
        colourMap = plt.get_cmap("viridis", nDistribs)
    else:
        colourMap = plt.get_cmap("copper", nDistribs)

    xRounds = np.arange(100)
    for i in range(nDistribs):
        if option == "longCollection":
            # ax.hist(fearMoraleMalusDistrib_collection[i], nBins, label=collectionLegend[i], range=(0,nBins), density=False, cumulative=False, color=colourMap(i), histtype="step", linestyle=('solid' if i%2 == 0 else 'dashed'))
            ax.plot(xRounds, fearMoraleMalusDistrib_collection[i], label=collectionLegend[i], color=colourMap(i), linestyle=('solid' if i%2 == 0 else 'dashed'))
        else:
            # ax.hist(fearMoraleMalusDistrib_collection[i], nBins, label=collectionLegend[i], range=(0,nBins), density=False, cumulative=False, color=colourMap(i), histtype="step")
            ax.plot(xRounds, fearMoraleMalusDistrib_collection[i], label=collectionLegend[i], color=colourMap(i))

    # Create new legend handles but use the colors from the existing ones
    handles, labels = ax.get_legend_handles_labels()
    if len(handles) != nDistribs:
        raise ValueError('handles list should have length of nDistribs, it is not the case')
    if option == "longCollection":
        new_handles = [Line2D([], [], c=handles[i].get_color(), linestyle=('solid' if i%2 == 0 else 'dashed')) for i in range(nDistribs)]
    else:
        new_handles = [Line2D([], [], c=handles[i].get_color()) for i in range(nDistribs)]

    # plt.legend(handles=new_handles, labels=labels)

    ax.legend(handles=new_handles, labels=labels, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.label_outer()

    plt.xlim(xmin=0, xmax = 100)
    plt.ylim(ymin=0, ymax = 10)
    # plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # transforms y-axis in % format

    plt.title(pltTitle)

    fig.tight_layout() # otherwise the right y-label is slightly clipped
    fig.tight_layout() # for some reason gotta call it twice for the top title to not be cropped


    # x-axis: major ticks every 20, minor ticks every 5
    major_ticks_x = np.arange(0, 101, 20)
    minor_ticks_x = np.arange(0, 101, 5)
    # # y-axis: major ticks every 0.2, minor ticks every 0.05
    # major_ticks_y = np.arange(0, 101, 20)*1./100
    # minor_ticks_y = np.arange(0, 101, 5)*1./100
    # y-axis: major ticks every 0.2, minor ticks every 0.05
    major_ticks_y = np.arange(0, 10, 1 )
    minor_ticks_y = np.arange(0, 10, 1./5)

    ax.set_xticks(major_ticks_x)
    ax.set_xticks(minor_ticks_x, minor=True)
    ax.set_yticks(major_ticks_y)
    ax.set_yticks(minor_ticks_y, minor=True)

    ax.grid(which='both')

    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)

    # save figure in ./WailingWindsPlots/ folder ; if it  doesnt exist, create it
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, 'WailingWindsPlots/')
    results_dir_png = os.path.join(script_dir, 'WailingWindsPlots/pngPlots/')

    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    if not os.path.isdir(results_dir_png):
        os.makedirs(results_dir_png)

    if option == "debug":
        plt.show()
    plt.savefig(results_dir+pdfName+'.pdf')
    plt.savefig(results_dir_png+pdfName+'.png')


################################################################################################################################
########################### Main functions that call plotting functions for many different scenarios ###########################
################################################################################################################################

def plot_varyingMorale_setEnchantments_commandersRout(nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # nIteration=100000

    nDistribs = len(unitMorale_collection)

    for bloodRainActive in [0,1]:
        for wailingWindsActive in [0,1]:
            if (bloodRainActive, wailingWindsActive) != (0, 0):
                print("analysing: (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                bloodRain = ""
                if bloodRainActive == 1:
                    bloodRain = "_withBloodRain"
                if bloodRainActive == 0:
                    bloodRain = "_noBloodRain"
                wailingWinds = ""
                if wailingWindsActive == 1:
                    wailingWinds = "_withWailingWinds"
                if wailingWindsActive == 0:
                    wailingWinds = "_noWailingWinds"

                routingTimeDistrib_collection = []
                collectionLegend = []
                for unitMorale in unitMorale_collection:
                    print("Morale "+str(unitMorale))
                    routingTimeDistrib_collection += [makeWailingRoutDistrib_commanders(unitMorale, bloodRainActive, wailingWindsActive, nIteration)]
                    collectionLegend += ["morale " + str(unitMorale)]

                wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                rainStatus = "ON" if bloodRainActive == 1 else "OFF"

                pltTitle = "commanders - BloodRain" + rainStatus + ", WailingWinds " + wailingStatus
                pdfName = "MoralePlays_MoraleComparison_commanders___BloodRain_" + rainStatus + "_WailingWinds_" + wailingStatus

                plotHistograms_commanders(nDistribs, routingTimeDistrib_collection, collectionLegend, pltTitle, pdfName, "longCollection")

def plot_setMorale_varyingEnchantments_commandersRout(nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # unitMorale_collection = [15]
    # nIteration=100000

    for unitMorale in unitMorale_collection:
        print("simulating unit morale "+str(unitMorale))
        # for wailingWindsActive in [0,1]:
        #     if (bloodRainActive, wailingWindsActive) != (0, 0):

        nDistribs = 3 # wailing,rain (on,on), (on,off), (off,on)
        routingTimeDistrib_collection = []
        collectionLegend = []

        for bloodRainActive in [0,1]:
            for wailingWindsActive in [0,1]:
                if (bloodRainActive, wailingWindsActive) != (0, 0):
                    print("simulating (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                    routingTimeDistrib_collection += [makeWailingRoutDistrib_commanders(unitMorale, bloodRainActive, wailingWindsActive, nIteration)]
                    wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                    rainStatus = "ON" if bloodRainActive == 1 else "OFF"
                    collectionLegend += ["winds " + wailingStatus + "\nrain    " + rainStatus]


        pltTitle = "commanders - morale " + str(unitMorale)
        pdfName = "MoralePlays_WailingRainComparison_commanders___morale_" + str(unitMorale)

        plotHistograms_commanders(nDistribs, routingTimeDistrib_collection, collectionLegend, pltTitle, pdfName)

def plot_setMorale_varyingEnchantments_squadRout(unitDensity = 3, squadSize = 10, nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # unitMorale_collection = range(16,30,2)
    # nIteration=100000

    # squadSize = 10
    # unitDensity = 2

    for unitMorale in unitMorale_collection:
        print("analysing: morale "+str(unitMorale)+":")

        nDistribs = 2 # wailing,rain (on,on), (on,off), (off,on)
        routedRatioDistrib_collection = []
        collectionLegend = []

        for bloodRainActive in [0,1]:
            for wailingWindsActive in [0,1]:
                if (bloodRainActive, wailingWindsActive) != (0, 0) and (bloodRainActive, wailingWindsActive) != (1, 0): #don't care about blood rain alone given it's not gonna rout squads by itself
                    print("simulating (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                    routedRatioDistrib_collection += [makeWailingRoutDistrib_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity, nIteration)]
                    wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                    rainStatus = "ON" if bloodRainActive == 1 else "OFF" 
                    collectionLegend += ["winds " + wailingStatus + "\nrain    " + rainStatus]


        pltTitle = "squad density" + str(unitDensity) + " size" + str(squadSize) + " morale " + str(unitMorale)
        pdfName = "MoralePlays_WailingRainComparison_squad_density" + str(unitDensity) + "_size" + str(squadSize) + "___morale_" + str(unitMorale)

        plotHistograms_squad(nDistribs, routedRatioDistrib_collection, collectionLegend, pltTitle, pdfName, "")

def plot_varyingMorale_setEnchantments_squadRout(unitDensity = 3, squadSize = 10, nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # nIteration=100000

    # squadSize = 10
    # unitDensity = 2

    nDistribs = len(unitMorale_collection)

    for bloodRainActive in [0,1]:
        for wailingWindsActive in [0,1]:
            if (bloodRainActive, wailingWindsActive) != (0, 0) and (bloodRainActive, wailingWindsActive) != (1, 0): #don't care about blood rain alone given it's not gonna rout squads by itself
                print("analysing: (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                bloodRain = ""
                if bloodRainActive == 1:
                    bloodRain = "_withBloodRain"
                if bloodRainActive == 0:
                    bloodRain = "_noBloodRain"
                wailingWinds = ""
                if wailingWindsActive == 1:
                    wailingWinds = "_withWailingWinds"
                if wailingWindsActive == 0:
                    wailingWinds = "_noWailingWinds"

                routedRatioDistrib_collection = []
                collectionLegend = []

                for unitMorale in unitMorale_collection:
                    print("Morale "+str(unitMorale))
                    routedRatioDistrib_collection += [makeWailingRoutDistrib_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity, nIteration)]
                    collectionLegend += ["morale " + str(unitMorale)]

                wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                rainStatus = "ON" if bloodRainActive == 1 else "OFF"

                pltTitle = "squad density" + str(unitDensity) + " size" + str(squadSize) + " - BloodRain" + rainStatus + ", WailingWinds " + wailingStatus
                pdfName = "MoralePlays_MoraleComparison_squad_density" + str(unitDensity) + "_size" + str(squadSize) + "___BloodRain_" + rainStatus + "_WailingWinds_" + wailingStatus

                plotHistograms_squad(nDistribs, routedRatioDistrib_collection, collectionLegend, pltTitle, pdfName, "longCollection")

def plot_varyingMorale_setEnchantments_moraleMalus(nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # nIteration=10000

    nDistribs = len(unitMorale_collection)

    for bloodRainActive in [0,1]:
        for wailingWindsActive in [0,1]:
            if (bloodRainActive, wailingWindsActive) != (0, 0):
                print("analysing: (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                bloodRain = ""
                if bloodRainActive == 1:
                    bloodRain = "_withBloodRain"
                if bloodRainActive == 0:
                    bloodRain = "_noBloodRain"
                wailingWinds = ""
                if wailingWindsActive == 1:
                    wailingWinds = "_withWailingWinds"
                if wailingWindsActive == 0:
                    wailingWinds = "_noWailingWinds"

                fearMoraleMalusDistrib_collection = []
                collectionLegend = []
                for unitMorale in unitMorale_collection:
                    print("Morale "+str(unitMorale))
                    fearMoraleMalusDistrib_collection += [makeFearMoraleMalusAverageDistrib(unitMorale, bloodRainActive, wailingWindsActive, nIteration)]
                    collectionLegend += ["morale " + str(unitMorale)]

                wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                rainStatus = "ON" if bloodRainActive == 1 else "OFF"

                pltTitle = "morale malus - BloodRain" + rainStatus + ", WailingWinds " + wailingStatus
                pdfName = "MoralePlays_MoraleComparison___BloodRain_" + rainStatus + "_WailingWinds_" + wailingStatus + "_moraleMalus"

                plotHistograms_fearMoraleMalus(nDistribs, fearMoraleMalusDistrib_collection, collectionLegend, pltTitle, pdfName, "longCollection")

def plot_setMorale_varyingEnchantments_moraleMalus(nIteration = 100000):
    unitMorale_collection = range(10,30,2)
    # unitMorale_collection = [15]
    # nIteration=10000

    for unitMorale in unitMorale_collection:
        print("simulating unit morale "+str(unitMorale))
        # for wailingWindsActive in [0,1]:
        #     if (bloodRainActive, wailingWindsActive) != (0, 0):

        nDistribs = 3 # wailing,rain (on,on), (on,off), (off,on)
        fearMoraleMalusDistrib_collection = []
        collectionLegend = []

        for bloodRainActive in [0,1]:
            for wailingWindsActive in [0,1]:
                if (bloodRainActive, wailingWindsActive) != (0, 0):
                    print("simulating (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                    fearMoraleMalusDistrib_collection += [makeFearMoraleMalusAverageDistrib(unitMorale, bloodRainActive, wailingWindsActive, nIteration)]
                    wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                    rainStatus = "ON" if bloodRainActive == 1 else "OFF"
                    collectionLegend += ["winds " + wailingStatus + "\nrain    " + rainStatus]


        pltTitle = "morale malus - morale " + str(unitMorale)
        pdfName = "MoralePlays_WailingRainComparison___morale_" + str(unitMorale)+"_moraleMalus"

        plotHistograms_fearMoraleMalus(nDistribs, fearMoraleMalusDistrib_collection, collectionLegend, pltTitle, pdfName)


def plot_varyingSquadSize_setMorale_setEnchantments_squadRout(unitDensity = 3, nIteration = 100000):
    squadSize_collection = range(10,110,10)
    nDistribs = len(squadSize_collection)
    unitMorale_collection = range(18,30,2)
    # nIteration=100
    # unitDensity = 2

    for unitMorale in unitMorale_collection:
        for bloodRainActive in [0,1]:
            for wailingWindsActive in [0,1]:
                if (bloodRainActive, wailingWindsActive) != (0, 0) and (bloodRainActive, wailingWindsActive) != (1, 0): #don't care about blood rain alone given it's not gonna rout squads by itself
                    print("analysing: unitMorale = " + str(unitMorale) + ", (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                    bloodRain = ""
                    if bloodRainActive == 1:
                        bloodRain = "_withBloodRain"
                    if bloodRainActive == 0:
                        bloodRain = "_noBloodRain"
                    wailingWinds = ""
                    if wailingWindsActive == 1:
                        wailingWinds = "_withWailingWinds"
                    if wailingWindsActive == 0:
                        wailingWinds = "_noWailingWinds"

                    routedRatioDistrib_collection = []
                    collectionLegend = []

                    for squadSize in squadSize_collection:
                        print("squadSize "+str(squadSize))
                        routedRatioDistrib_collection += [makeWailingRoutDistrib_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity, nIteration)]
                        collectionLegend += ["squadSize " + str(squadSize)]

                    wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                    rainStatus = "ON" if bloodRainActive == 1 else "OFF"

                    pltTitle = "squad density" + str(unitDensity) + ", morale" + str(unitMorale) + " - BloodRain" + rainStatus + ", WailingWinds " + wailingStatus
                    pdfName = "MoralePlays_squadSizeComparison_squad_density" + str(unitDensity) + "_morale" + str(unitMorale) + "___BloodRain_" + rainStatus + "_WailingWinds_" + wailingStatus

                    plotHistograms_squad(nDistribs, routedRatioDistrib_collection, collectionLegend, pltTitle, pdfName, "longCollection")




def plot_all_commanders():
    plot_varyingMorale_setEnchantments_commandersRout()
    plot_setMorale_varyingEnchantments_commandersRout()



def plot_test():
    unitMorale_collection = [10,15,20,25]
    nIteration=100000

    # # commanders
    # for unitMorale in unitMorale_collection:
    #     # for wailingWindsActive in [0,1]:
    #     #     if (bloodRainActive, wailingWindsActive) != (0, 0):

    #     nDistribs = 3 # wailing,rain (on,on), (on,off), (off,on)
    #     routingTimeDistrib_collection = []
    #     collectionLegend = []

    #     for bloodRainActive in [0,1]:
    #         for wailingWindsActive in [0,1]:
    #             if (bloodRainActive, wailingWindsActive) != (0, 0):
    #                 routingTimeDistrib_collection += [makeWailingRoutDistrib_commanders(unitMorale, bloodRainActive, wailingWindsActive, nIteration)]
    #                 wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
    #                 rainStatus = "ON" if bloodRainActive == 1 else "OFF"
    #                 collectionLegend += ["winds " + wailingStatus + "\nrain    " + rainStatus]


    #     pltTitle = "commander morale " + str(unitMorale)
    #     pdfName = "test_WailingRainComparison___morale_" + str(unitMorale)+"_commanders"

    #     plotHistograms_commanders(nDistribs, routingTimeDistrib_collection, collectionLegend, pltTitle, pdfName, "debug")


    # squad
    for unitMorale in unitMorale_collection:
        print("simulating "+str(unitMorale)+":")
        # for wailingWindsActive in [0,1]:
        #     if (bloodRainActive, wailingWindsActive) != (0, 0):

        nDistribs = 2 # wailing,rain (on,on), (on,off), (off,on)
        routedRatioDistrib_collection = []
        collectionLegend = []
        squadSize = 10
        unitDensity = 2

        for bloodRainActive in [0,1]:
            for wailingWindsActive in [0,1]:
                if (bloodRainActive, wailingWindsActive) != (0, 0) and (bloodRainActive, wailingWindsActive) != (1, 0):
                    print("simulating (bloodRainActive, wailingWindsActive) = " + str((bloodRainActive, wailingWindsActive))) 
                    routedRatioDistrib_collection += [makeWailingRoutDistrib_squad(unitMorale, bloodRainActive, wailingWindsActive, squadSize, unitDensity, nIteration)]
                    wailingStatus = "ON" if wailingWindsActive == 1 else "OFF"
                    rainStatus = "ON" if bloodRainActive == 1 else "OFF"
                    collectionLegend += ["winds " + wailingStatus + "\nrain    " + rainStatus]


        pltTitle = "squad morale " + str(unitMorale)
        pdfName = "test_WailingRainComparison___morale_" + str(unitMorale)+"_squad"

        plotHistograms_squad(nDistribs, routedRatioDistrib_collection, collectionLegend, pltTitle, pdfName, "")







# for units:
#     proba full squad gone
#     proba one unit gone
#     % of units in the squad gone


# legacy error bars attempt

    # SumSquareDev = 0
    # E = wailingExpectedRout(unitMorale, bloodRainActive, wailingWindsActive, nIteration)
    
    # n, bins, patches = plt.hist(RoutingTime, num_bins, range=(0,140), density=1, facecolor='blue', alpha=0.5)    

    # y,binEdges = np.histogram(RoutingTime,range=(0,300),bins=num_bins)
    # bincenters = 0.5*(binEdges[1:]+binEdges[:-1])
    # sigma     = np.sqrt(y) # wrong error bar, check out https://stats.stackexchange.com/questions/368533/conditional-probability-for-consecutive-bernoulli-trials for an idea
    # width      = 0.0
    # # plt.bar(bincenters, y, width=width, color='r', yerr=sigma)
    # plt.errorbar(
    #     bincenters,
    #     y,
    #     yerr = y**0.5,
    #     marker = '.',
    #     linestyle='',
    #     drawstyle = 'steps-mid'
    # )