# def Research_turn(turn = 1, mageRP = 13, Mscale = 2, AwakeRP = 0):
#     RP = turn*(mageRP+Mscale) + AwakeRP
#     if (turn>12):
#         RP = RP + (turn-12)*(mageRP+Mscale)     
#     if (turn>16):
#         RP = RP + (turn-16)*(mageRP+Mscale)
#     if (turn>24):
#         RP = RP + (turn-24)*(mageRP+Mscale)        
#     return RP

def NumberMages(NmagesPrevious = 0, turn = 1, attritionRate = 0):
    if (turn <= 12):
        #no casualties before turn 13
        #capital fort production
        NmagesNew = NmagesPrevious + 1
    else:
        #capital fort production
        NmagesNew = NmagesPrevious*(1 - attritionRate) + 1
        #second fort (built at turn 13) production
        NmagesNew = NmagesNew + 1   
        if (turn>16):
            #third fort (built at turn 17) production
            NmagesNew = NmagesNew + 1   
            if (turn>20):
                NmagesNew = NmagesNew + 1   

    return NmagesNew

def cumulativeRP( mageRP = 13, Mscale = 2, AwakeRP = 90, targets_andPercentMageResearching = [[750],[1]], attritionRate = 0):
    turn_targets = []
    targets = targets_andPercentMageResearching[0]
    percentMageResearching = targets_andPercentMageResearching[1]
    i_target = 0
    cumulative_RP = 0
    turn = 0
    N_MagesPreviousTurn = 0
    N_MagesNewTurn = 0
    while (i_target < len(targets)):
        turn = turn + 1
        # cumulative_RP = cumulative_RP + Research_turn(turn, mageRP, Mscale, AwakeRP, attritionRate)*percentMageResearching
        N_MagesNewTurn = NumberMages(N_MagesPreviousTurn, turn, attritionRate)
        cumulative_RP = cumulative_RP + (mageRP + Mscale)*N_MagesNewTurn*percentMageResearching[i_target] + AwakeRP
        if (cumulative_RP>targets[i_target]):
            turn_targets.append(turn)
            cumulative_RP = cumulative_RP - targets[i_target]
            i_target = i_target + 1

        #end of turn attribution
        N_MagesPreviousTurn = N_MagesNewTurn
    print ("turn targets got achieved = ",turn_targets)
    return turn_targets




# just calculate it you lazy ass

# if we call T_i(n) the total RP for n for turns at magic scale i
# T_i(n)-T_j(n)=(i-j)*(Sigma_(k=1,n)(k))=(i-j)n*(n+1)/2
