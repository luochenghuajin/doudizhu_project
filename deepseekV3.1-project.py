
from __future__ import annotations
from typing import List, Dict, Sequence
from doudizhu.Player import Player

class Judger:
    pass

def NewJudger() -> Judger:
    judger_instance = Judger()
    judger_instance.rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
    return judger_instance

def IsGameOver(players: Sequence[Player]) -> bool:
    for p in players:
        if len(p.GetHand()) == 0:
            return True
    return False

def GetWinner(players: Sequence[Player]) -> int:
    for p in players:
        if len(p.GetHand()) == 0:
            return p.GetId()
    return -1

def CalculatePayoff(winner_id: int, landlord_id: int) -> Dict[int, int]:
    payoff = {}
    for id in range(3):
        payoff[id] = 0
    if winner_id == landlord_id:
        payoff[landlord_id] = 1
    else:
        for id in range(3):
            if id != landlord_id:
                payoff[id] = 1
    return payoff
