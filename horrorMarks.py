import random as rand


def attractivenessHorror(nMarks, drainScale, misfortuneScale, globalHorrorLevel):
    return (5*nMarks + 1 - drainScale + misfortuneScale ) * globalHorrorLevel

def horror_scenario(horrorMarkChance = 10, drainScale = 0, misfortuneScale = 0, globalHorrorLevel = 1, nStatistics = 10000):
    sumTurns = 0
    for i in range (nStatistics):
        horrorAttack = False
        nMarks = 0
        turn = 0
        while horrorAttack == False:
            if rand.randrange(100) < horrorMarkChance:
                nMarks += 1
            if rand.randrange(1000) < attractivenessHorror(nMarks, drainScale, misfortuneScale, globalHorrorLevel):
                horrorAttack = True
            turn += 1
        sumTurns += turn
    esperance = sumTurns * 1./nStatistics
    return esperance
