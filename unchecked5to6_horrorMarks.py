import matplotlib.pyplot as plt
import random as rand
import numpy as np

def PotentialAddMark(markChance):
    MarkIncrement = 0
    if rand.randrange(100) < markChance*100:
        MarkIncrement = 1
    return MarkIncrement

def IsAttacked(Nmarks, drainScale, fortuneScale, cursed):
    if cursed == 1:
        Attractiveness = Nmarks * 5 * 2 - drainScale - fortuneScale
    else :
        Attractiveness = Nmarks * 5     - drainScale - fortuneScale
    if rand.randrange(1000) < Attractiveness :
        return 1
    else :
        return 0

def FirstHorrorAttackTurn(drainScale, fortuneScale, cursed, markChance):
    turn = 0
    hasBeenAttacked = 0
    Nmarks = 0
    while hasBeenAttacked == 0 :
        turn +=1
        Nmarks += PotentialAddMark(markChance)
        if IsAttacked(Nmarks, drainScale, fortuneScale, cursed) == 1 :
            hasBeenAttacked = 1
    return turn


def expected_FirstHorrorAttack(drainScale = -3, fortuneScale = -2, cursed = 1, markChance = 0.1):
    #only look at values above 0 ; a difference of -3 is seen as a 0

    #initialise expected value of the difference
    FirstHorrorAttack = 0
    Statistics = 1000000
    for i in range(Statistics):
        FirstHorrorAttack += FirstHorrorAttackTurn(drainScale, fortuneScale, cursed, markChance)
    FirstHorrorAttack = FirstHorrorAttack*1./Statistics
    return FirstHorrorAttack 