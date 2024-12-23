import explodingDice as drn
import math as math
import random as rand

def Repel_attack_outcome(Atk_repel,Def_attacker):
    repel_atk_roll = Atk_repel + drn.DRN()
    attacker_def_roll = Def_attacker + drn.DRN()
    result_repel_atk = repel_atk_roll - attacker_def_roll
    return result_repel_atk
    # DRN_success_chance(hero_value = 0,opposition_value = 0


def hunting_unrest(N_turns = 1, N_hunter = 1,lv_hunter = 2, order_scale = 3, N_candles = 10, PD_unrest_reduction = 0,site_freq = 40):
  current_unrest = 0
  if lv_hunter < 3:
    proba_find = 0.1 + 0.4*lv_hunter
  else:
    proba_find = 1
  
  unrest_from_hunting = proba_find*(d(slaves x 3 +4)) + (1-probafind)*(d6-1)
  for turn in range (N_turns):
    order_factor = (10 - order_scale - 1)/(10 - order_scale)
    current_unrest = order_factor*(current_unrest + unrest_from_hunting - math.ceil(N_candles/2) - PD_unrest_reduction)
  return current_unrest
  unfinished
