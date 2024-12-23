import explodingDice as drn


def Repel_attack_outcome(Atk_repel,Def_attacker):
    repeller_atk_roll = Atk_repel + drn.DRN()
    attacker_def_roll = Def_attacker + drn.DRN()
    result_repel_atk = repeller_atk_roll - attacker_def_roll
    return result_repel_atk
    # DRN_success_chance(hero_value = 0,opposition_value = 0

def Morale_Check(result_repel_atk,Size_repel,Size_attacker,Morale_attacker):
    repeller_roll = 10 + drn.DRN() + result_repel_atk
    attacker_roll = Morale_attacker + drn.DRN() + (Size_attacker - Size_repel)
    result_morale = repeller_roll - attacker_roll
    return result_morale

def Repel_rate_noHarassment(Atk_repel=12,Size_repel=3,Def_attacker = 8,Morale_attacker = 11,Size_attacker = 3):
    #note: manual is wrong, weapon length difference does not intervene. Rather, it's the unit size difference
    success_count = 0
    total_count = 1000
    for i in range(total_count):
        result_repel_atk = Repel_attack_outcome(Atk_repel,Def_attacker)
        if result_repel_atk > 0:
            result_morale = Morale_Check(result_repel_atk,Size_repel,Size_attacker,Morale_attacker)
            if (result_morale > 0):
                success_count = success_count + 1
    success_rate = success_count*1./total_count
    return success_rate

def Repel_rate_HarassmentSteadyState(Atk_repel=12,Size_repel=4,Def_attacker = 8,Morale_attacker = 11,Size_attacker = 1,N_units_repelling = 1, N_units_attacking =3):
    #N_units_repelling is the number of units on the repeller side. N>1 does not mean it influences the repel check. Only influences attacker harassment.
    success_count = 0
    total_count = 1000
    for i in range(total_count):
        result_repel_atk = Repel_attack_outcome(Atk_repel,Def_attacker)
        if result_repel_atk > 0:
            result_morale = Morale_Check(result_repel_atk,Size_repel,Size_attacker,Morale_attacker)
            if (result_morale > 0):
                success_count = success_count + 1
    success_rate = success_count*1./total_count
    return success_rate
# should I model attacker harassment as well?

# def HarassmentPenalty_steadyState(N_units_harassing, N_units_harassed, HarassedUnitIsMounted = 0):
#     decayRate = 95./100
#     HarassPenalty = 0
#     TurnHarassmentValue = ToBeDetermined # gotta understand how attacks from a square are spread out throughout a turn