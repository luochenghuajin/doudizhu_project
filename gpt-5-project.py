@@ FILE: doudizhu/Judger.py @@
from__future__ import annotations
from typing import List, Dict, Sequence
from doudizhu.Player import Player

class Judger:
    def __init__(self) -> None:
        self.rank_order: List[str] = []

    def IsGameOver(self, players: Sequence[Player]) -> bool:
        for p in players:
            if len(p.GetHand()) == 0:
                return True
        return False

    def GetWinner(self, players: Sequence[Player]) -> int:
        for p in players:
            if len(p.GetHand()) == 0:
                return p.GetId()
        return -1

    def CalculatePayoff(self, winner_id: int, landlord_id: int) -> Dict[int, int]:
        payoff: Dict[int, int] = {}
        for id in range(0, 3):
            payoff[id] = 0
        if winner_id == landlord_id:
            payoff[landlord_id] = 1
        else:
            for id in range(0, 3):
                if id != landlord_id:
                    payoff[id] = 1
        return payoff

def NewJudger() -> Judger:
    judger_instance = Judger()
    judger_instance.rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
    return judger_instance
@@ FILE: doudizhu/Dealer.py @@
from__future__ import annotations
import random
from typing import List, Tuple, Sequence, Dict
from doudizhu.base import Card, Deck, Hand

def CreateFullDeck() -> Deck:
    deck: Deck = []
    suits = ["Spade", "Heart", "Club", "Diamond"]
    ranks = ["3","4","5","6","7","8","9","T","J","Q","K","A","2"]
    for suit in suits:
        for rank in ranks:
            card = Card(rank=rank, suit=suit)
            deck.append(card)
    deck.append(Card(rank="B", suit=None))
    deck.append(Card(rank="R", suit=None))
    return deck

class Dealer:
    def __init__(self) -> None:
        self.deck: Deck = []

    @staticmethod
    def EvaluateHandHeuristic(hand_str: str) -> int:
        score = 0
        frequency: Dict[str, int] = {}
        for ch in hand_str:
            if ch in frequency:
                frequency[ch] = frequency[ch] + 1
            else:
                frequency[ch] = 1
        for rank_char, count in frequency.items():
            if rank_char == "R":
                score = score + 50 * count
            elif rank_char == "B":
                score = score + 45 * count
            elif rank_char == "2":
                score = score + 20 * count
            elif rank_char == "A":
                score = score + 12 * count
            elif rank_char == "K":
                score = score + 8 * count
            elif rank_char == "Q":
                score = score + 6 * count
            elif rank_char == "J":
                score = score + 5 * count
            elif rank_char == "T":
                score = score + 4 * count
            else:
                score = score + 1 * count
            if count == 2:
                score = score + 10
            elif count == 3:
                score = score + 25
            elif count == 4:
                score = score + 40
        return score

    def ShuffleDeck(self) -> Deck:
        deck_to_shuffle = list(self.deck)
        n = len(deck_to_shuffle)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            temp = deck_to_shuffle[i]
            deck_to_shuffle[i] = deck_to_shuffle[j]
            deck_to_shuffle[j] = temp
        return deck_to_shuffle

    def Deal(self, deck: Deck) -> Tuple[List[Hand], Hand]:
        hands: List[Hand] = [[], [], []]
        for i in range(0, 51):
            player_index = i % 3
            hands[player_index].append(deck[i])
        seen_cards: Hand = []
        for i in range(51, 54):
            seen_cards.append(deck[i])
        return (hands, seen_cards)

    def DetermineLandlord(self, players: Sequence) -> int:
        best_score = float("-inf")
        landlord_id = 0
        for player in players:
            hand_str = player.GetHandAsString()
            score = Dealer.EvaluateHandHeuristic(hand_str)
            if score > best_score:
                best_score = score
                landlord_id = player.GetId()
        return landlord_id

def NewDealer() -> Dealer:
    dealer_instance = Dealer()
    dealer_instance.deck = CreateFullDeck()
    return dealer_instance
@@ FILE: doudizhu/Player.py @@
from typing import List, Dict, Any, Optional, Sequence
import copy
from doudizhu.base import Card, Hand, PlayAction

class Player:
    def __init__(self) -> None:
        self.id: int = 0
        self.hand: Hand = []
        self.role: str = "peasant"

    @staticmethod
    def CardsEqual(a: Card, b: Card) -> bool:
        return (a.rank == b.rank) and ((a.suit == b.suit) or (a.suit is None) or (b.suit is None))

    @staticmethod
    def SortHand(player: 'Player') -> None:
        order_map: Dict[str, int] = {"3":0,"4":1,"5":2,"6":3,"7":4,"8":5,"9":6,"T":7,"J":8,"Q":9,"K":10,"A":11,"2":12,"B":13,"R":14}
        player.hand.sort(key=lambda card: (order_map[card.rank], (card.suit or "")))

    def ParseActionStringToCards(self, action_str: str) -> PlayAction:
        result: PlayAction = []
        if action_str == "pass":
            return result
        rank_to_indices: Dict[str, List[int]] = {}
        for i in range(0, len(self.hand)):
            r = self.hand[i].rank
            if r not in rank_to_indices:
                rank_to_indices[r] = []
            rank_to_indices[r].append(i)
        for ch in action_str:
            if (ch in rank_to_indices) and (len(rank_to_indices[ch]) > 0):
                idx = rank_to_indices[ch].pop()
                result.append(copy.copy(self.hand[idx]))
            else:
                result.append(Card(rank=ch, suit=None))
        return result

    def GetHand(self) -> Hand:
        return copy.copy(self.hand)

    def GetId(self) -> int:
        return self.id

    def GetRole(self) -> str:
        return self.role

    def GetHandAsString(self) -> str:
        rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
        bucket: Dict[str, int] = {r: 0 for r in rank_order}
        for card in self.hand:
            ch = card.rank
            bucket[ch] = bucket[ch] + 1
        result = ""
        for r in rank_order:
            count = bucket[r]
            for _ in range(1, count + 1):
                result = result + r
        return result

def NewPlayer(id: int) -> Player:
    player_instance = Player()
    player_instance.id = id
    player_instance.hand = []
    player_instance.role = "peasant"
    return player_instance

class Player(Player):  # Extend with remaining methods under the same class name per constraints
    def SetHand(self, hand: Hand) -> None:
        self.hand = copy.copy(hand)

    def SetRole(self, role: str) -> None:
        self.role = role

    def AddCards(self, cards: Hand) -> None:
        for card in cards:
            self.hand.append(card)
        Player.SortHand(self)

    def RemoveCards(self, cards: PlayAction) -> None:
        for played_card in cards:
            removed = False
            for i in range(0, len(self.hand)):
                if Player.CardsEqual(self.hand[i], played_card):
                    del self.hand[i]
                    removed = True
                    break
            if not removed:
                print("Warning: attempted to remove card not in hand for player", self.id)
        Player.SortHand(self)

    def SelectAction(self, state: Dict) -> PlayAction:
        legal_action_strings: List[str] = state["actions"]
        chosen_str = "pass"
        max_len = 0
        if legal_action_strings:
            chosen_str = legal_action_strings[0]
            for act_str in legal_action_strings:
                if act_str != "pass" and len(act_str) > max_len:
                    max_len = len(act_str)
                    chosen_str = act_str
        if max_len == 0 and ("pass" in legal_action_strings):
            chosen_str = "pass"
        if chosen_str == "pass":
            return []
        else:
            return self.ParseActionStringToCards(chosen_str)
@@ FILE: doudizhu/Round.py @@
from__future__ import annotations
from typing import List, Tuple, Optional, Sequence
from doudizhu.base import Card, PlayAction
from doudizhu.Player import Player

class Round:
    def __init__(self) -> None:
        self.players: Sequence[Player] = []
        self.judger = None
        self.action_trace: List[Tuple[int, str]] = []
        self.played_cards: List[Card] = []
        self.last_non_pass_player: Optional[int] = None
        self.consecutive_passes: int = 0

    @staticmethod
    def ActionToString(action: PlayAction) -> str:
        s = ""
        for c in action:
            s = s + c.rank
        return s

    def GetLastValidPlay(self) -> Optional[Tuple[int, str]]:
        if self.last_non_pass_player is None:
            return None
        for i in range(len(self.action_trace) - 1, -1, -1):
            player_id, action_str = self.action_trace[i]
            if player_id == self.last_non_pass_player:
                return (player_id, action_str)
        return None

    def RecordAction(self, player_id: int, action: PlayAction) -> None:
        if len(action) == 0:
            self.action_trace.append((player_id, "pass"))
            self.consecutive_passes = self.consecutive_passes + 1
        else:
            action_str = Round.ActionToString(action)
            self.action_trace.append((player_id, action_str))
            for c in action:
                self.played_cards.append(c)
            self.consecutive_passes = 0
            self.last_non_pass_player = player_id
        return

    def GetNextPlayer(self, current_player_id: int) -> int:
        n = len(self.players)
        next_index = -1
        for i in range(0, n):
            if self.players[i].GetId() == current_player_id:
                next_index = (i + 1) % n
                break
        if next_index == -1:
            return self.players[0].GetId()
        return self.players[next_index].GetId()

    def GetActionTrace(self) -> Sequence[Tuple[int, str]]:
        return list(self.action_trace)

    def GetAllPlayedCards(self) -> Sequence[str]:
        ranks_list: List[str] = []
        for c in self.played_cards:
            ranks_list.append(c.rank)
        order_map = {r: i for i, r in enumerate(self.judger.rank_order)}
        ranks_list.sort(key=lambda ch: order_map[ch])
        return ranks_list

def NewRound(players: Sequence[Player], judger) -> Round:
    round_instance = Round()
    round_instance.players = players
    round_instance.judger = judger
    round_instance.action_trace = []
    round_instance.played_cards = []
    round_instance.last_non_pass_player = None
    round_instance.consecutive_passes = 0
    return round_instance
@@ FILE: doudizhu/ActionGenerator.py @@
from__future__ import annotations
from typing import Any, Dict, List, Optional, Sequence

class ActionGenerator:
    def __init__(self) -> None:
        self.RANK_ORDER: List[str] = []
        self.RANK_TO_VAL: Dict[str, int] = {}
        self.MAX_STRAIGHT_RANK: str = ""
        self.MIN_STRAIGHT_RANK: str = ""

    def RankBefore(self, r: str) -> Optional[str]:
        idx = self.RANK_TO_VAL[r]
        if idx <= 0:
            return None
        return self.RANK_ORDER[idx - 1]

    def RankAfter(self, r: str) -> Optional[str]:
        idx = self.RANK_TO_VAL[r]
        if idx >= len(self.RANK_ORDER) - 1:
            return None
        return self.RANK_ORDER[idx + 1]

    def IsRankInStraightRange(self, r: str) -> bool:
        val = self.RANK_TO_VAL[r]
        return (self.RANK_TO_VAL[self.MIN_STRAIGHT_RANK] <= val) and (val <= self.RANK_TO_VAL[self.MAX_STRAIGHT_RANK])

    def CountRanks(self, hand_cards) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for c in hand_cards:
            m[c.rank] = m.get(c.rank, 0) + 1
        return m

    def CountRanksFromString(self, s: str) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for ch in s:
            m[ch] = m.get(ch, 0) + 1
        return m

    def CloneCounts(self, m: Dict[str, int]) -> Dict[str, int]:
        n: Dict[str, int] = {}
        for k, v in m.items():
            n[k] = v
        return n

    def SubCounts(self, a: Dict[str, int], b: Dict[str, int]) -> Dict[str, int]:
        n = self.CloneCounts(a)
        for k, v in b.items():
            n[k] = n.get(k, 0) - v
            if n[k] < 0:
                n[k] = 0
        return n

    def MakeUseMap(self, ranks: Sequence[str], times: int) -> Dict[str, int]:
        m: Dict[str, int] = {}
        for r in ranks:
            m[r] = m.get(r, 0) + times
        return m

    def CountTotal(self, m: Dict[str, int]) -> int:
        s = 0
        for _, c in m.items():
            s = s + c
        return s

    def NumberOfKeys(self, cnt: Dict[str, int]) -> int:
        n = 0
        for _, _ in cnt.items():
            n = n + 1
        return n

    def AllSameCount(self, cnt: Dict[str, int], value: int) -> bool:
        if self.NumberOfKeys(cnt) == 0:
            return False
        for _, c in cnt.items():
            if c != value:
                return False
        return True

    def AllCountsMax(self, cnt: Dict[str, int], maxv: int) -> bool:
        for _, c in cnt.items():
            if c > maxv:
                return False
        return True

    def ContainsCount(self, cnt: Dict[str, int], target: int) -> bool:
        for _, c in cnt.items():
            if c == target:
                return True
        return False

    def GetRankWithCount(self, cnt: Dict[str, int], target: int) -> Optional[str]:
        for r, c in cnt.items():
            if c == target:
                return r
        return None

    def SortRanks(self, ranks: Sequence[str]) -> Sequence[str]:
        ranks = list(ranks)
        ranks.sort(key=lambda rank: self.RANK_TO_VAL[rank])
        return ranks

    def SortedRanks(self, cnt: Dict[str, int]) -> Sequence[str]:
        ranks: List[str] = []
        for r, _ in cnt.items():
            ranks.append(r)
        return self.SortRanks(ranks)

    def IsConsecutive(self, ranks_sorted: Sequence[str]) -> bool:
        if len(ranks_sorted) <= 1:
            return True
        for i in range(0, len(ranks_sorted) - 1):
            if self.RANK_TO_VAL[ranks_sorted[i + 1]] != self.RANK_TO_VAL[ranks_sorted[i]] + 1:
                return False
        return True

    def AllWithinStraightRange(self, ranks_sorted: Sequence[str]) -> bool:
        for r in ranks_sorted:
            if not self.IsRankInStraightRange(r):
                return False
        return True

    def ListSingleRanksFromCounts(self, cnt: Dict[str, int]) -> Sequence[str]:
        out: List[str] = []
        for r, c in cnt.items():
            for _ in range(1, c + 1):
                out.append(r)
        out = list(self.SortRanks(out))
        return out

    def ListPairRanksFromCounts(self, cnt: Dict[str, int]) -> Sequence[str]:
        out: List[str] = []
        for r, c in cnt.items():
            k = c // 2
            for _ in range(1, k + 1):
                out.append(r)
        out = list(self.SortRanks(out))
        return out

    def CombinationsByIndex(self, A: Sequence, k: int) -> Sequence[Sequence[int]]:
        result: List[List[int]] = []
        cur: List[int] = []

        def dfs(start: int, remain: int) -> None:
            if remain == 0:
                result.append(list(cur))
                return
            for i in range(start, len(A) - remain + 1):
                cur.append(i)
                dfs(i + 1, remain - 1)
                cur.pop()

        if k <= len(A) and k >= 0:
            dfs(0, k)
        return result

    def StringFromCounts(self, cnt: Dict[str, int]) -> str:
        s = ""
        ranks_sorted = self.SortRanks(self.SortedRanks(cnt))
        for r in ranks_sorted:
            for _ in range(1, cnt.get(r, 0) + 1):
                s = s + r
        return s

    def FindAirplaneCores(self, counts: Dict[str, int]) -> Sequence[Sequence[str]]:
        cores: List[List[str]] = []
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 3) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = list(self.SortRanks(elig))
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j + 1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 2:
                for L in range(2, block_len + 1):
                    for start in range(i, j - L + 2):
                        core: List[str] = []
                        for t in range(start, start + L):
                            core.append(elig[t])
                        cores.append(core)
            i = j + 1
        return cores

    def TryExtractAirplaneCore(self, cnt: Dict[str, int]) -> Dict[str, Any]:
        cores = self.FindAirplaneCores(cnt)
        for core_ranks in cores:
            ok = True
            for r in core_ranks:
                if cnt.get(r, 0) < 3:
                    ok = False
                    break
            if ok:
                use = self.MakeUseMap(core_ranks, 3)
                return {"success": True, "core_ranks": core_ranks, "core_use": use}
        return {"success": False}

    def RepeatRanks(self, core_ranks: Sequence[str], times: int) -> str:
        s = ""
        for r in core_ranks:
            for _ in range(1, times + 1):
                s = s + r
        return s

    def IsValidAirplaneAttachmentCounts(self, core_ranks: Sequence[str], attach_cnt: Dict[str, int], attach_type: str) -> bool:
        if attach_type == "single":
            if (attach_cnt.get("B", 0) == 1) and (attach_cnt.get("R", 0) == 1):
                return False
        total: Dict[str, int] = {}
        for r in core_ranks:
            total[r] = total.get(r, 0) + 3
        for r, c in attach_cnt.items():
            total[r] = total.get(r, 0) + c
        for _, c in total.items():
            if c == 4:
                return False
        min_r = core_ranks[0]
        max_r = core_ranks[len(core_ranks) - 1]
        left_edge = self.RankBefore(min_r)
        if (left_edge is not None) and self.IsRankInStraightRange(left_edge):
            if total.get(left_edge, 0) >= 3:
                return False
        right_edge = self.RankAfter(max_r)
        if (right_edge is not None) and self.IsRankInStraightRange(right_edge):
            if total.get(right_edge, 0) >= 3:
                return False
        return True

    def IsValidAirplaneAttachmentString(self, core_str: str, attach_cnt: Dict[str, int], attach_type: str) -> bool:
        core_rank_cnt = self.CountRanksFromString(core_str)
        core_ranks = self.SortedRanks(core_rank_cnt)
        return self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, attach_type)

    def IdentifyPatternFromString(self, action_str: str) -> Dict[str, Any]:
        info: Dict[str, Any] = {"kind": "invalid", "main_value": -1}
        if action_str == "" or action_str == "pass":
            return info
        cnt = self.CountRanksFromString(action_str)
        if (len(action_str) == 2) and (cnt.get("B", 0) == 1) and (cnt.get("R", 0) == 1):
            info["kind"] = "rocket"
            info["main_value"] = 999
            return info
        if len(action_str) == 4:
            for rank, c in cnt.items():
                if c == 4:
                    info["kind"] = "bomb"
                    info["main_value"] = self.RANK_TO_VAL[rank]
                    return info
        if len(action_str) == 1:
            r = action_str[0]
            info["kind"] = "solo"
            info["main_value"] = self.RANK_TO_VAL[r]
            return info
        if len(action_str) == 2:
            if self.AllSameCount(cnt, 2) and (self.NumberOfKeys(cnt) == 1):
                r = next(iter(cnt))
                info["kind"] = "pair"
                info["main_value"] = self.RANK_TO_VAL[r]
                return info
        if len(action_str) == 3:
            if self.AllSameCount(cnt, 3) and (self.NumberOfKeys(cnt) == 1):
                r = next(iter(cnt))
                info["kind"] = "trio"
                info["main_value"] = self.RANK_TO_VAL[r]
                info["core_count"] = 1
                return info
        if len(action_str) == 4:
            if self.ContainsCount(cnt, 3) and self.ContainsCount(cnt, 1) and (self.NumberOfKeys(cnt) == 2):
                trio_rank = self.GetRankWithCount(cnt, 3)
                single_rank = self.GetRankWithCount(cnt, 1)
                if trio_rank != single_rank:
                    info["kind"] = "trio_single"
                    info["main_value"] = self.RANK_TO_VAL[trio_rank]  # type: ignore
                    info["core_count"] = 1
                    return info
        if len(action_str) == 5:
            if self.ContainsCount(cnt, 3) and self.ContainsCount(cnt, 2) and (self.NumberOfKeys(cnt) == 2):
                trio_rank = self.GetRankWithCount(cnt, 3)
                pair_rank = self.GetRankWithCount(cnt, 2)
                if (trio_rank != pair_rank) and (pair_rank != "B") and (pair_rank != "R"):
                    info["kind"] = "trio_pair"
                    info["main_value"] = self.RANK_TO_VAL[trio_rank]  # type: ignore
                    info["core_count"] = 1
                    return info
        if len(action_str) == 6:
            if self.ContainsCount(cnt, 4):
                four_rank = self.GetRankWithCount(cnt, 4)
                rem_ranks: List[str] = []
                for rank, c in cnt.items():
                    if rank != four_rank:
                        for _ in range(1, c + 1):
                            rem_ranks.append(rank)
                if len(rem_ranks) == 2:
                    if not (("B" in rem_ranks) and ("R" in rem_ranks)):
                        info["kind"] = "four_two_single"
                        info["main_value"] = self.RANK_TO_VAL[four_rank]  # type: ignore
                        return info
        if len(action_str) == 8:
            if self.ContainsCount(cnt, 4):
                four_rank = self.GetRankWithCount(cnt, 4)
                pairs_count = 0
                ok = True
                for rank, c in cnt.items():
                    if rank == four_rank:
                        continue
                    if c == 2:
                        pairs_count = pairs_count + 1
                    else:
                        ok = False
                if ok and (pairs_count == 2):
                    info["kind"] = "four_two_pair"
                    info["main_value"] = self.RANK_TO_VAL[four_rank]  # type: ignore
                    return info
        if (len(action_str) >= 5) and self.AllSameCount(cnt, 1):
            ranks_sorted = self.SortedRanks(cnt)
            if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                top = ranks_sorted[len(ranks_sorted) - 1]
                info["kind"] = "straight"
                info["main_value"] = self.RANK_TO_VAL[top]
                info["length"] = len(action_str)
                return info
        if (len(action_str) >= 6) and (len(action_str) % 2 == 0) and self.AllSameCount(cnt, 2):
            ranks_sorted = self.SortedRanks(cnt)
            if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                top = ranks_sorted[len(ranks_sorted) - 1]
                info["kind"] = "pair_chain"
                info["main_value"] = self.RANK_TO_VAL[top]
                info["pair_len"] = len(action_str) // 2
                return info
        if (len(action_str) >= 6) and (len(action_str) % 3 == 0):
            if self.AllSameCount(cnt, 3):
                ranks_sorted = self.SortedRanks(cnt)
                if self.AllWithinStraightRange(ranks_sorted) and self.IsConsecutive(ranks_sorted):
                    top = ranks_sorted[len(ranks_sorted) - 1]
                    info["kind"] = "airplane"
                    info["main_value"] = self.RANK_TO_VAL[top]
                    info["trio_len"] = len(action_str) // 3
                    info["core_count"] = info["trio_len"]
                    return info
        core = self.TryExtractAirplaneCore(cnt)
        if core.get("success"):
            core_ranks = core["core_ranks"]
            k = len(core_ranks)
            top = core_ranks[k - 1]
            remain = self.SubCounts(cnt, core["core_use"])
            total_len = len(action_str)
            if total_len == 4 * k:
                if self.CountTotal(remain) == k and self.AllCountsMax(remain, 1):
                    airplane_cards_str = self.RepeatRanks(core_ranks, 3)
                    if self.IsValidAirplaneAttachmentString(airplane_cards_str, remain, "single"):
                        info["kind"] = "airplane_single"
                        info["main_value"] = self.RANK_TO_VAL[top]
                        info["trio_len"] = k
                        info["core_count"] = k
                        return info
            if total_len == 5 * k:
                if self.CountTotal(remain) == 2 * k and self.AllSameCount(remain, 2):
                    airplane_cards_str = self.RepeatRanks(core_ranks, 3)
                    if self.IsValidAirplaneAttachmentString(airplane_cards_str, remain, "pair"):
                        info["kind"] = "airplane_pair"
                        info["main_value"] = self.RANK_TO_VAL[top]
                        info["trio_len"] = k
                        info["core_count"] = k
                        return info
        return info

    def LexRankLess(self, a: str, b: str) -> bool:
        i = 0
        while (i < len(a)) and (i < len(b)):
            va = self.RANK_TO_VAL[a[i]]
            vb = self.RANK_TO_VAL[b[i]]
            if va != vb:
                return va < vb
            i = i + 1
        return len(a) < len(b)

    def SortUnique(self, seq: Sequence[str]) -> Sequence[str]:
        seen = set()
        tmp: List[str] = []
        for s in seq:
            if s not in seen:
                seen.add(s)
                tmp.append(s)
        for i in range(1, len(tmp)):
            j = i
            while j > 0 and self.CompareActions(tmp[j], tmp[j - 1]):
                tmp[j], tmp[j - 1] = tmp[j - 1], tmp[j]
                j -= 1
        return tmp

    def CompareActions(self, a: str, b: str) -> bool:
        if len(a) != len(b):
            return len(a) < len(b)
        ia = self.IdentifyPatternFromString(a)
        ib = self.IdentifyPatternFromString(b)
        if (ia["kind"] != "invalid") and (ib["kind"] != "invalid"):
            if ia["main_value"] != ib["main_value"]:
                return ia["main_value"] < ib["main_value"]
            return self.LexRankLess(a, b)
        else:
            return self.LexRankLess(a, b)

    def FindSolos(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 1:
                result.append(r)
        return self.SortUnique(result)

    def FindPairs(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 2 and r != "B" and r != "R":
                result.append(r + r)
        return self.SortUnique(result)

    def FindTrios(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                result.append(r + r + r)
        return self.SortUnique(result)

    def FindTrioWithSingle(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 3
                for s_rank, s_cnt in remain.items():
                    if s_cnt >= 1 and s_rank != r:
                        result.append(r + r + r + s_rank)
        return self.SortUnique(result)

    def FindTrioWithPair(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 3 and r != "B" and r != "R":
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 3
                for p_rank, p_cnt in remain.items():
                    if (p_cnt >= 2) and (p_rank != "B") and (p_rank != "R") and (p_rank != r):
                        result.append(r + r + r + p_rank + p_rank)
        return self.SortUnique(result)

    def FindStraights(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 1) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = list(self.SortRanks(elig))
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j + 1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 5:
                for L in range(5, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t]
                        result.append(s)
            i = j + 1
        return self.SortUnique(result)

    def FindPairChains(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 2) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = list(self.SortRanks(elig))
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j + 1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 3:
                for L in range(3, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t] + elig[t]
                        result.append(s)
            i = j + 1
        return self.SortUnique(result)

    def FindAirplanes(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        elig: List[str] = []
        for r, c in counts.items():
            if (c >= 3) and self.IsRankInStraightRange(r):
                elig.append(r)
        elig = list(self.SortRanks(elig))
        i = 0
        while i < len(elig):
            j = i
            while (j + 1 < len(elig)) and (self.RANK_TO_VAL[elig[j + 1]] == self.RANK_TO_VAL[elig[j]] + 1):
                j = j + 1
            block_len = j - i + 1
            if block_len >= 2:
                for L in range(2, block_len + 1):
                    for start in range(i, j - L + 2):
                        s = ""
                        for t in range(start, start + L):
                            s = s + elig[t] + elig[t] + elig[t]
                        result.append(s)
            i = j + 1
        return self.SortUnique(result)

    def FindAirplanesWithAttachments(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        cores = self.FindAirplaneCores(counts)
        for core_ranks in cores:
            k = len(core_ranks)
            core_str = self.RepeatRanks(core_ranks, 3)
            remain = self.SubCounts(counts, self.MakeUseMap(core_ranks, 3))
            single_slots = k
            single_candidates = self.ListSingleRanksFromCounts(remain)
            for pick in self.CombinationsByIndex(single_candidates, single_slots):
                attach_cnt: Dict[str, int] = {}
                for idx in pick:
                    r = single_candidates[idx]
                    attach_cnt[r] = attach_cnt.get(r, 0) + 1
                if (attach_cnt.get("B", 0) == 1) and (attach_cnt.get("R", 0) == 1):
                    continue
                if not self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, "single"):
                    continue
                attach_str = self.StringFromCounts(attach_cnt)
                result.append(core_str + attach_str)
            pair_slots = k
            pair_candidates = self.ListPairRanksFromCounts(remain)
            for pick in self.CombinationsByIndex(pair_candidates, pair_slots):
                attach_cnt: Dict[str, int] = {}
                for idx in pick:
                    r = pair_candidates[idx]
                    attach_cnt[r] = attach_cnt.get(r, 0) + 2
                if not self.IsValidAirplaneAttachmentCounts(core_ranks, attach_cnt, "pair"):
                    continue
                attach_str = self.StringFromCounts(attach_cnt)
                result.append(core_str + attach_str)
        return self.SortUnique(result)

    def FindFourWithTwo(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 4:
                core_str = r + r + r + r
                remain = self.CloneCounts(counts)
                remain[r] = remain.get(r, 0) - 4
                singles = self.ListSingleRanksFromCounts(remain)
                for pick in self.CombinationsByIndex(singles, 2):
                    rank1 = singles[pick[0]]
                    rank2 = singles[pick[1]]
                    if ((rank1 == "B" and rank2 == "R") or (rank1 == "R" and rank2 == "B")):
                        continue
                    s = core_str + rank1 + rank2
                    result.append(s)
                pairs = self.ListPairRanksFromCounts(remain)
                for pick in self.CombinationsByIndex(pairs, 2):
                    rankA = pairs[pick[0]]
                    rankB = pairs[pick[1]]
                    if rankA == rankB:
                        continue
                    s = core_str + rankA + rankA + rankB + rankB
                    result.append(s)
        return self.SortUnique(result)

    def FindBombs(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        counts = self.CountRanks(hand_cards)
        for r, c in counts.items():
            if c >= 4 and r != "B" and r != "R":
                result.append(r + r + r + r)
        return self.SortUnique(result)

    def FilterHigherBombs(self, hand_cards, last_bomb_value: int) -> Sequence[str]:
        bombs = self.FindBombs(hand_cards)
        out: List[str] = []
        for b in bombs:
            r = b[0]
            if self.RANK_TO_VAL[r] > last_bomb_value:
                out.append(b)
        return self.SortUnique(out)

    def HasRocket(self, hand_cards) -> bool:
        counts = self.CountRanks(hand_cards)
        return (counts.get("B", 0) >= 1) and (counts.get("R", 0) >= 1)

    def FindSamePatternStronger(self, hand_cards, last_info: Dict[str, Any]) -> Sequence[str]:
        out: List[str] = []
        kind = last_info["kind"]
        if kind == "solo":
            candidates = self.FindSolos(hand_cards)
            for s in candidates:
                val = self.RANK_TO_VAL[s[0]]
                if val > last_info["main_value"]:
                    out.append(s)
        elif kind == "pair":
            candidates = self.FindPairs(hand_cards)
            for s in candidates:
                val = self.RANK_TO_VAL[s[0]]
                if val > last_info["main_value"]:
                    out.append(s)
        elif kind == "trio":
            candidates = self.FindTrios(hand_cards)
            for s in candidates:
                trio_rank = s[0]
                if self.RANK_TO_VAL[trio_rank] > last_info["main_value"]:
                    out.append(s)
        elif kind == "trio_single":
            candidates = self.FindTrioWithSingle(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "trio_single") and (info.get("core_count") == last_info.get("core_count")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "trio_pair":
            candidates = self.FindTrioWithPair(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "trio_pair") and (info.get("core_count") == last_info.get("core_count")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "straight":
            candidates = self.FindStraights(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "straight") and (info.get("length") == last_info.get("length")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "pair_chain":
            candidates = self.FindPairChains(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "pair_chain") and (info.get("pair_len") == last_info.get("pair_len")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "airplane":
            candidates = self.FindAirplanes(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane") and (info.get("trio_len") == last_info.get("trio_len")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "airplane_single":
            candidates = self.FindAirplanesWithAttachments(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane_single") and (info.get("trio_len") == last_info.get("trio_len")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "airplane_pair":
            candidates = self.FindAirplanesWithAttachments(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "airplane_pair") and (info.get("trio_len") == last_info.get("trio_len")) and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "four_two_single":
            candidates = self.FindFourWithTwo(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "four_two_single") and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "four_two_pair":
            candidates = self.FindFourWithTwo(hand_cards)
            for s in candidates:
                info = self.IdentifyPatternFromString(s)
                if (info["kind"] == "four_two_pair") and (info["main_value"] > last_info["main_value"]):
                    out.append(s)
        elif kind == "bomb":
            pass
        else:
            pass
        return self.SortUnique(out)

    def GenerateAllPatterns(self, hand_cards) -> Sequence[str]:
        result: List[str] = []
        solos = self.FindSolos(hand_cards)
        for s in solos:
            result.append(s)
        pairs = self.FindPairs(hand_cards)
        for s in pairs:
            result.append(s)
        trios = self.FindTrios(hand_cards)
        for s in trios:
            result.append(s)
        trio_single = self.FindTrioWithSingle(hand_cards)
        for s in trio_single:
            result.append(s)
        trio_pair = self.FindTrioWithPair(hand_cards)
        for s in trio_pair:
            result.append(s)
        straights = self.FindStraights(hand_cards)
        for s in straights:
            result.append(s)
        pair_chains = self.FindPairChains(hand_cards)
        for s in pair_chains:
            result.append(s)
        airplanes = self.FindAirplanes(hand_cards)
        for s in airplanes:
            result.append(s)
        airplane_wings = self.FindAirplanesWithAttachments(hand_cards)
        for s in airplane_wings:
            result.append(s)
        four_two = self.FindFourWithTwo(hand_cards)
        for s in four_two:
            result.append(s)
        bombs = self.FindBombs(hand_cards)
        for s in bombs:
            result.append(s)
        if self.HasRocket(hand_cards):
            result.append("BR")
        return self.SortUnique(result)

    def GetLegalActions(self, player, round_context) -> Sequence[str]:
        actions: List[str] = []
        hand_cards = player.GetHand()
        last = round_context.GetLastValidPlay()
        if (last is None) or (last[0] == player.GetId()):
            all_patterns = self.GenerateAllPatterns(hand_cards)
            for s in all_patterns:
                actions.append(s)
            return self.SortUnique(actions)
        actions.append("pass")
        last_str = last[1]
        last_info = self.IdentifyPatternFromString(last_str)
        if last_info["kind"] == "invalid":
            all_patterns = self.GenerateAllPatterns(hand_cards)
            for s in all_patterns:
                actions.append(s)
            return self.SortUnique(actions)
        if last_info["kind"] == "rocket":
            return self.SortUnique(actions)
        stronger = self.FindSamePatternStronger(hand_cards, last_info)
        for s in stronger:
            actions.append(s)
        if last_info["kind"] != "bomb":
            bombs = self.FindBombs(hand_cards)
            for b in bombs:
                actions.append(b)
        else:
            higher_bombs = self.FilterHigherBombs(hand_cards, last_info["main_value"])
            for b in higher_bombs:
                actions.append(b)
        if self.HasRocket(hand_cards):
            actions.append("BR")
        return self.SortUnique(actions)

def NewActionGenerator() -> ActionGenerator:
    ag = ActionGenerator()
    ag.RANK_ORDER = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
    ag.RANK_TO_VAL = {}
    for i in range(0, len(ag.RANK_ORDER)):
        ag.RANK_TO_VAL[ag.RANK_ORDER[i]] = i
    ag.MAX_STRAIGHT_RANK = "A"
    ag.MIN_STRAIGHT_RANK = "3"
    return ag
@@ FILE: doudizhu/Game.py @@
from__future__ import annotations
from typing import Dict, List, Any, Sequence, Optional
from doudizhu.Player import NewPlayer, Player
from doudizhu.Dealer import NewDealer, Dealer
from doudizhu.Judger import NewJudger, Judger
from doudizhu.Round import NewRound, Round
from doudizhu.ActionGenerator import NewActionGenerator

class Game:
    def __init__(self) -> None:
        self.players: List[Player] = []
        self.dealer: Dealer = None  # type: ignore
        self.judger: Judger = None  # type: ignore
        self.round: Round = None  # type: ignore
        self.seen_cards = []
        self.action_generator = None
        self.landlord_id: Optional[int] = None

    def GetOthersHandAsString(self, exclude_player_id: int) -> str:
        combined = ""
        for p in self.players:
            if p.GetId() == exclude_player_id:
                continue
            combined = combined + p.GetHandAsString()
        order_map = {"3":0,"4":1,"5":2,"6":3,"7":4,"8":5,"9":6,"T":7,"J":8,"Q":9,"K":10,"A":11,"2":12,"B":13,"R":14}
        chars = list(combined)
        chars.sort(key=lambda ch: order_map[ch])
        result = ""
        for ch in chars:
            result = result + ch
        return result

    def BuildState(self, current_player_id: int, landlord_id: int, seen_cards, legal_actions: Sequence[str]) -> Dict:
        current_hand = self.players[current_player_id].GetHandAsString()
        others_hand = self.GetOthersHandAsString(current_player_id)
        trace = self.round.GetActionTrace()
        played_cards = self.round.GetAllPlayedCards()
        seen_str = ""
        for c in seen_cards:
            seen_str = seen_str + c.rank
        state = {
            "self": current_player_id,
            "current_hand": current_hand,
            "others_hand": others_hand,
            "actions": legal_actions,
            "trace": trace,
            "landlord": landlord_id,
            "seen_cards": seen_str,
            "played_cards": played_cards
        }
        return state

    def DisplayResults(self, winner_id: int, payoff: Dict[int, int]) -> None:
        if winner_id == -1:
            print("No winner determined.")
        else:
            print("Game winner: Player", winner_id)
        print("Payoff:")
        for id in range(0, 3):
            print(" Player", id, ":", payoff[id])
        print("Final hands (post-play):")
        for p in self.players:
            print(" Player", p.GetId(), "role=", p.GetRole(), "hand=", p.GetHandAsString())
        print("Action trace:")
        trace = self.round.GetActionTrace()
        for entry in trace:
            print(entry)
        return

def NewGame() -> Game:
    game = Game()
    game.players = [ NewPlayer(0),
                     NewPlayer(1),
                     NewPlayer(2) ]
    game.dealer = NewDealer()
    game.judger = NewJudger()
    game.round = NewRound(game.players, game.judger)
    game.seen_cards = []
    game.action_generator = NewActionGenerator()
    game.landlord_id = None
    return game

class Game(Game):  # Extend with Run under the same class name per constraints
    def Run(self) -> None:
        deck = self.dealer.ShuffleDeck()
        (hands, seen_cards) = self.dealer.Deal(deck)
        self.seen_cards = seen_cards
        for i in range(0, 3):
            self.players[i].SetHand(hands[i])
        landlord_id = self.dealer.DetermineLandlord(self.players)
        self.landlord_id = landlord_id
        for i in range(0, 3):
            if self.players[i].GetId() == landlord_id:
                self.players[i].AddCards(seen_cards)
                self.players[i].SetRole("landlord")
            else:
                self.players[i].SetRole("peasant")
        current_player_id = landlord_id
        turn_count = 0
        max_turns = 163
        while not self.judger.IsGameOver(self.players):
            if turn_count >= max_turns:
                print("Reached max turns, aborting game loop.")
                break
            current_player = self.players[current_player_id]
            legal_actions = self.action_generator.GetLegalActions(current_player, self.round)
            state = self.BuildState(current_player_id, landlord_id, seen_cards, legal_actions)
            action = self.players[current_player_id].SelectAction(state)
            if len(action) == 0:
                action_as_string = "pass"
            else:
                action_as_string = self.round.ActionToString(action)
            is_legal = False
            for legal_action_str in state["actions"]:
                if action_as_string == legal_action_str:
                    is_legal = True
                    break
            if not is_legal:
                print("Warning: Player", current_player_id, "returned an illegal action. Choosing a valid fallback.")
                fallback_action_str = state["actions"][0]
                action = Player.ParseActionStringToCards(self.players[current_player_id], fallback_action_str)
            self.round.RecordAction(current_player_id, action)
            self.players[current_player_id].RemoveCards(action)
            if self.judger.IsGameOver(self.players):
                break
            current_player_id = self.round.GetNextPlayer(current_player_id)
            turn_count = turn_count + 1
        winner_id = self.judger.GetWinner(self.players)
        payoff = self.judger.CalculatePayoff(winner_id, self.landlord_id)  # type: ignore
        self.DisplayResults(winner_id, payoff)
        return
