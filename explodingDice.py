import matplotlib.pyplot as plt
import random as rand
import numpy as np

def exploDICE(size = 6):
    die = 1+rand.randrange(size)
    if (size == 1):
      return 1
    if (die == size):
        return die - 1 + exploDICE(size)
    else:
        return die

def DRN():
    return exploDICE(6)+exploDICE(6)
def DRN_fateweaving():
    return exploDICE(6)
def DRN_triple():
    return exploDICE(6)+exploDICE(6)+exploDICE(6)

def expectedValue_exploDICE(size = 6):
    #calculate the expected value of an exploding dice

    #initialise expected value of the exploding dice
    expected_value=0
    Statistics = 1000000
    for i in range (Statistics):
        expected_value = expected_value + exploDICE(size)
    expected_value = expected_value*1./Statistics
    print(expected_value)

def expected_DRNvsDRN_pos(hero_value = 0,opposition_value = 0):
    #only look at values above 0 ; a difference of -3 is seen as a 0

    #initialise expected value of the difference
    expected_difference = 0
    Statistics = 1000000
    for i in range(Statistics):
        expected_difference = expected_difference + max(hero_value + DRN() - opposition_value - DRN(),0)
    expected_difference = expected_difference*1./Statistics
    return expected_difference

def expected_DRNvsDRN_pos_Fateweaving(hero_value = 0,opposition_value = 0):
    #only look at values above 0 ; a difference of -3 is seen as a 0

    #initialise expected value of the difference
    expected_difference = 0
    Statistics = 1000000
    for i in range(Statistics):
        expected_difference = expected_difference + max(hero_value + DRN() - opposition_value - DRN_fateweaving(),0)
    expected_difference = expected_difference*1./Statistics
    return expected_difference

def expected_DRNvsDRN(hero_value = 0,opposition_value = 0):
    #also consider negative values

    #initialise expected value of the difference
    expected_difference = 0
    #monte carlo calculation
    Statistics = 1000000
    for i in range(Statistics):
        expected_difference = expected_difference + (hero_value + DRN() - opposition_value - DRN())
    expected_difference = expected_difference*1./Statistics
    return expected_difference

def DRN_difference_distribution_pos(hero_value = 0,opposition_value = 0):
    #only look at values above 0 ; a difference of -3 is seen as a 0
    DRNdifference = []
    Statistics = 1000000
    for i in range (Statistics):
        DRNdifference = DRNdifference + [max(0,hero_value + DRN() - opposition_value - DRN())]
    DRNdifference = np.array(DRNdifference)
    num_bins = max(DRNdifference)
    n, bins, patches = plt.hist(DRNdifference, num_bins, density=1,facecolor='blue',alpha=0.5)
    plt.show()

def DRN_difference_distribution(hero_value = 0,opposition_value = 0):
    #look at all values, a -3 is a -3
    DRNdifference = []
    Statistics = 1000000
    for i in range (Statistics):
        DRNdifference = DRNdifference + [hero_value + DRN() - opposition_value - DRN()]
    DRNdifference = np.array(DRNdifference)
    num_bins = max(DRNdifference)
    n, bins, patches = plt.hist(DRNdifference, num_bins, density=1,facecolor='blue',alpha=0.5)
    plt.show()

def DRN_success_chance(hero_value = 0,opposition_value = 0):
    #success is heroDRN > oppositionDRN
    DRNdifference = []  
    Statistics = 100000
    for i in range (Statistics):
        DRNdifference = DRNdifference + [hero_value + DRN() - opposition_value - DRN()]
    DRNdifference = np.array(DRNdifference)
    success_count = 0
    total_count = 0
    for drn in DRNdifference:
        total_count = total_count + 1
        if drn > 0 :
            success_count = success_count + 1
    success_rate = success_count*1./total_count
    return success_rate
    

# a = expected_DRNvsDRN(0,0)
# print(a)
# DRN_difference_distribution(0,0)