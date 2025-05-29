# Players.py

from typing import Dict, List, Tuple, Optional
from Agents import Personality

# All five resource types
RESOURCES = ['brick', 'lumber', 'grain', 'wool', 'ore']

BUILDING_COSTS = {
    'road':      {'brick': 1, 'lumber': 1},
    'settlement': {'brick': 1, 'lumber': 1, 'grain': 1, 'wool': 1},
    'city':      {'grain': 2, 'ore': 3},
    'dev_card':  {'grain': 1, 'ore': 1, 'wool': 1}
}

DICE_PROBABILITIES = {
    2: 1/36, 3: 2/36, 4: 3/36, 5: 4/36,
    6: 5/36, 8: 5/36, 9: 4/36, 10: 3/36,
    11: 2/36, 12: 1/36
}

DISCOUNT_FACTOR = 0.6

class Player:
    def __init__(self, name: str, personality: Optional[Personality] = None):
        self.name = name
        # Initialize all five resources
        self.resources: Dict[str,int] = {r: 0 for r in RESOURCES}
        self.buildings: List[str] = []
        self.resource_sources: List[Tuple[str, int, bool]] = []
        self.goal_queue: List[str] = ['settlement','city','dev_card']
        self.personality = personality

    @property
    def current_goal(self) -> Optional[str]:
        return self.goal_queue[0] if self.goal_queue else None

    def add_resource(self, resource: str, count: int = 1):
        self.resources[resource] += count

    def remove_resource(self, resource: str, count: int = 1):
        self.resources[resource] = max(0, self.resources[resource] - count)

    def resource_delta(self) -> Tuple[Dict[str,int], Dict[str,int]]:
        if self.current_goal is None:
            return {}, {}
        cost = BUILDING_COSTS[self.current_goal]
        shortage, surplus = {}, {}
        for res, have in self.resources.items():
            req = cost.get(res, 0)
            if have < req:
                shortage[res] = req - have
            elif have > req:
                surplus[res] = have - req
        # Any extra beyond current goal counts as surplus
        for res, have in self.resources.items():
            if res not in cost and have > 0:
                surplus[res] = surplus.get(res, have)
        return shortage, surplus

    def expected_income(self) -> Dict[str,float]:
        income = {r: 0.0 for r in RESOURCES}
        for res, dice, is_city in self.resource_sources:
            prob = DICE_PROBABILITIES.get(dice, 0)
            income[res] += prob * (2 if is_city else 1)
        return income

    def resource_urgency_vector(self) -> Dict[str,float]:
        urgency = {r: 0.0 for r in RESOURCES}
        hand = self.resources.copy()
        discount = 1.0
        for goal in self.goal_queue:
            cost = BUILDING_COSTS[goal]
            for res in RESOURCES:
                req = cost.get(res, 0)
                have = hand[res]
                if have < req:
                    urgency[res] += discount * (req - have)
                    hand[res] = 0
                else:
                    hand[res] -= req
            discount *= DISCOUNT_FACTOR
        total = sum(urgency.values())
        if total == 0:
            return {r:0.0 for r in RESOURCES}
        return {r: urgency[r] / total for r in RESOURCES}

    def marginal_value(self) -> Dict[str,float]:
        return self.resource_urgency_vector()

    def shadow_prices(self) -> Dict[str,float]:
        exp_inc = self.expected_income()
        mv = self.marginal_value()
        prices: Dict[str,float] = {}
        for r in RESOURCES:
            if exp_inc[r] > 0:
                prices[r] = mv[r] / exp_inc[r]
            elif mv[r] > 0:
                prices[r] = 1000.0
            else:
                prices[r] = 0.0
        return prices

    def __str__(self):
        return (f"{self.name} | Res: {self.resources} | "
                f"Builds: {self.buildings} | Goals: {self.goal_queue}")
