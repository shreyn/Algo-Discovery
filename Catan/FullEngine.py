import random
from collections import defaultdict
from Player import Player, BUILDING_COSTS, DICE_PROBABILITIES

class TradeOffer:
    def __init__(self, giver, receiver, offer_give, offer_get):
        self.giver = giver
        self.receiver = receiver
        self.offer_give = offer_give
        self.offer_get = offer_get

    def __str__(self):
        return f"{self.giver} offers {self.offer_give} to {self.receiver} in exchange for {self.offer_get}"

class TradeEngine:
    def __init__(self, players, dice_rolls=None):
        self.players = players            # List of Player instances
        self.dice_rolls = dice_rolls      # Optional list of predetermined dice rolls
        self.roll_index = 0               # Next index into dice_rolls

    def _next_roll(self):
        if self.dice_rolls is not None and self.roll_index < len(self.dice_rolls):
            roll = self.dice_rolls[self.roll_index]
            self.roll_index += 1
            return roll
        # Fallback to random
        return random.randint(1,6) + random.randint(1,6)

    def generate_offer(self, player):
        """
        Choose one unit from surplus to offer for one unit of shortage.
        """
        if player.current_goal is None:
            return None, None

        shortage, surplus = player.resource_delta()
        for want in shortage:
            for give in surplus:
                if player.resources[give] > 0:
                    return {give: 1}, {want: 1}
        return None, None

    def would_accept_offer(self, receiver, offer_give, offer_get):
        """
        Receiver gives offer_get and receives offer_give.
        Accept if net shadow price gain is positive.
        """
        prices = receiver.shadow_prices()
        value_give = sum(prices[r] * c for r, c in offer_get.items())
        value_get = sum(prices[r] * c for r, c in offer_give.items())
        return value_get > value_give

    def execute_trade(self, p1, p2, offer_give, offer_get):
        # Check resources
        for res, cnt in offer_give.items():
            if p1.resources.get(res, 0) < cnt:
                return False
        for res, cnt in offer_get.items():
            if p2.resources.get(res, 0) < cnt:
                return False
        # Exchange
        for res, cnt in offer_give.items():
            p1.remove_resource(res, cnt)
            p2.add_resource(res, cnt)
        for res, cnt in offer_get.items():
            p2.remove_resource(res, cnt)
            p1.add_resource(res, cnt)
        return True

    def attempt_build(self, player):
        """
        If player can build their current goal, pay cost, record building,
        and add 3 random resource_sources (new tiles) based on type.
        """
        goal = player.goal_queue[0]
        if not goal:
            return False
        cost = BUILDING_COSTS[goal]
        if all(player.resources.get(res,0) >= cnt for res,cnt in cost.items()):
            # Pay cost
            for res, cnt in cost.items():
                player.remove_resource(res, cnt)
            # Record building
            player.buildings.append(goal)
            player.goal_queue.pop(0)
            # Add random tiles
            is_city = (goal == 'city')
            for _ in range(3):
                res = random.choice(list(player.resources.keys()))
                dice = random.choice(list(DICE_PROBABILITIES.keys()))
                player.resource_sources.append((res, dice, is_city))
            return True
        return False

    def run_trading_round(self):
        """
        One round: distribute resources by dice, then trading, then building.
        """
        # Resource distribution phase
        roll = self._next_roll()
        print(f"\nDice roll: {roll}")
        for player in self.players:
            gained = defaultdict(int)
            for (res, dice, is_city) in player.resource_sources:
                if dice == roll:
                    amt = 2 if is_city else 1
                    player.add_resource(res, amt)
                    gained[res] += amt
            if gained:
                print(f"{player.name} gains {dict(gained)}")

        # Trading phase
        trades = []
        for player in self.players:
            give, get = self.generate_offer(player)
            if not give:
                continue
            others = [p for p in self.players if p != player]
            random.shuffle(others)
            for other in others:
                if self.would_accept_offer(other, give, get):
                    if self.execute_trade(player, other, give, get):
                        trades.append((player.name, other.name, give, get))
                    break
        if trades:
            for t in trades:
                print(f"Trade: {t[0]} -> {t[1]} gives {t[2]}, gets {t[3]}")
        else:
            print("No trades this round.")

        # Building phase
        builds = []
        for player in self.players:
            if self.attempt_build(player):
                builds.append((player.name, player.buildings[-1]))
        if builds:
            for b in builds:
                print(f"Build: {b[0]} built {b[1]}")
        else:
            print("No builds this round.")

        # Resource summary
        print("Resource summary:")
        for player in self.players:
            print(f" {player.name}: {player.resources}")
        return roll, trades, builds


def test_full_simulation():
    # Two-player simulation with coverage of all resource types
    alice = Player("Alice")
    bob = Player("Bob")
    # Initial resources and sources: ensure at least one settlement on each resource type
    alice.resources = {'brick':1, 'lumber':1, 'grain':1, 'wool':1, 'ore':1}
    # Alice has settlements on brick, lumber, grain
    alice.resource_sources = [
        ('brick', 6, False),
        ('lumber', 8, False),
        ('grain', 5, False)
    ]
    alice.goal_queue = ['settlement','road','city','dev_card']

    bob.resources = {'brick':1, 'lumber':1, 'grain':1, 'wool':1, 'ore':1}
    # Bob has settlements on wool and ore
    bob.resource_sources = [
        ('wool', 9, False),
        ('ore', 10, False)
    ]
    bob.goal_queue = ['settlement','dev_card','road']

    # Predetermined dice rolls for visibility
    dice_seq = [6, 8, 5, 9, 10, 4, 11, 8, 5, 6]
    engine = TradeEngine([alice, bob], dice_rolls=dice_seq)

    for i in range(len(dice_seq)):
        print(f"\n=== Round {i+1}/{len(dice_seq)} ===")
        engine.run_trading_round()

    # Final state
    print("\n=== Final State ===")
    for p in [alice, bob]:
        print(f"{p.name}: resources={p.resources}, buildings={p.buildings}, sources={p.resource_sources}")

if __name__ == '__main__':
    test_full_simulation()

