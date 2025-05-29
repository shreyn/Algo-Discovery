# FullEngine.py

import random
from collections import defaultdict
from typing import List, Optional, Dict, Tuple

from Players import Player, RESOURCES, BUILDING_COSTS, DICE_PROBABILITIES


class TradeEngine:
    def __init__(
        self,
        players: List[Player],
        dice_rolls: Optional[List[int]] = None,
        rng: Optional[random.Random] = None
    ):
        self.players = players
        self.dice_rolls = dice_rolls
        self.roll_index = 0
        self.rng = rng or random.Random()

    def _next_roll(self) -> int:
        if self.dice_rolls and self.roll_index < len(self.dice_rolls):
            r = self.dice_rolls[self.roll_index]
            self.roll_index += 1
            return r
        return self.rng.randint(1, 6) + self.rng.randint(1, 6)

    def execute_trade(
        self,
        p1: Player,
        p2: Player,
        give: Dict[str, int],
        get: Dict[str, int]
    ) -> bool:
        for r, c in give.items():
            if p1.resources[r] < c:
                return False
        for r, c in get.items():
            if p2.resources[r] < c:
                return False
        for r, c in give.items():
            p1.remove_resource(r, c)
            p2.add_resource(r, c)
        for r, c in get.items():
            p2.remove_resource(r, c)
            p1.add_resource(r, c)
        return True

    def attempt_build(self, player: Player) -> bool:
        """
        If player can build their current goal, pay cost, record building,
        and then for settlement: add 3 new tiles;
        for city: upgrade one existing settlement's 3 tiles to a city.
        """
        if not player.goal_queue:
            return False

        goal = player.goal_queue[0]
        cost = BUILDING_COSTS[goal]
        # Check affordability
        if not all(player.resources.get(r, 0) >= c for r, c in cost.items()):
            return False

        # Pay cost
        for r, c in cost.items():
            player.remove_resource(r, c)

        # Record building
        player.buildings.append(goal)
        player.goal_queue.pop(0)

        if goal == 'settlement':
            # Add 3 new random settlement tiles
            for _ in range(3):
                res  = self.rng.choice(RESOURCES)
                dice = self.rng.choice(list(DICE_PROBABILITIES.keys()))
                player.resource_sources.append((res, dice, False))

        elif goal == 'city':
            # Find all settlement groups (chunks of 3 with is_city=False)
            groups = []
            total = len(player.resource_sources)
            for k in range(total // 3):
                chunk = player.resource_sources[3*k : 3*k+3]
                if not any(is_city for (_, _, is_city) in chunk):
                    groups.append(k)
            if groups:
                chosen = self.rng.choice(groups)
                # Upgrade those 3 tiles
                for j in range(3):
                    res, dice, _ = player.resource_sources[3*chosen + j]
                    player.resource_sources[3*chosen + j] = (res, dice, True)

        # road or dev_card have no tile effect
        return True

    def run_trading_round(self) -> Tuple[int, List, List]:
        roll = self._next_roll()
        print(f"\n--- Dice roll: {roll} ---")

        # 1) Distribute resources
        for p in self.players:
            gains = defaultdict(int)
            for res, dice, is_city in p.resource_sources:
                if dice == roll:
                    amt = 2 if is_city else 1
                    p.add_resource(res, amt)
                    gains[res] += amt
            if gains:
                print(f"{p.name} gains {dict(gains)}")

        # 2) Trading phase
        trades = []
        for p in self.players:
            others = [o for o in self.players if o is not p]
            offer = p.personality.propose_trade(p, others)
            if not offer:
                continue
            give, get = offer
            self.rng.shuffle(others)
            for o in others:
                if o.personality.accept_trade(o, give, get, p):
                    if self.execute_trade(p, o, give, get):
                        trades.append((p.name, o.name, give, get))
                    break
        if trades:
            for g, r, gv, gt in trades:
                print(f"Trade: {g} → {r} gives {gv}, gets {gt}")
        else:
            print("No trades")

        # 3) Building phase
        builds = []
        for p in self.players:
            if self.attempt_build(p):
                builds.append((p.name, p.buildings[-1]))
        if builds:
            for name, b in builds:
                print(f"Build: {name} built {b}")
        else:
            print("No builds")

        # 4) Resource summary
        print("Resources:")
        for p in self.players:
            print(f" {p.name}: {p.resources}")

        return roll, trades, builds
