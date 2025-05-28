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

DISCOUNT_FACTOR = 0.6  # Discount for future build steps

class Player:
    def __init__(self, name):
        self.name = name

        self.resources = {
            'lumber': 0,
            'brick': 0,
            'grain': 0,
            'wool': 0,
            'ore': 0
        }
        
        self.buildings = [] 
        self.resource_sources = []

        # Build plan: first build a settlement, then a city, then a dev card
        self.goal_queue = ['settlement', 'city', 'dev_card']
    
    @property
    def current_goal(self):
        return self.goal_queue[0] if self.goal_queue else None

    def add_resource(self, resource, count=1):
        self.resources[resource] += count
    
    def remove_resource(self, resource, count=1):
        self.resources[resource] = max(0, self.resources[resource] - count)

    def resource_delta(self):
        goal_cost = BUILDING_COSTS[self.current_goal]
        shortage = {}
        surplus = {}

        for res in self.resources:
            current = self.resources[res]
            required = goal_cost.get(res, 0)

            if current < required:
                shortage[res] = required - current
            elif current > required:
                surplus[res] = current - required

        for res in self.resources:  # add resources not needed for current goal
            if res not in goal_cost and self.resources[res] > 0:
                surplus[res] = self.resources[res]

        return shortage, surplus
    
    def expected_income(self):
        income = {res: 0.0 for res in self.resources}

        for (res, dice_num, is_city) in self.resource_sources:
            prob = DICE_PROBABILITIES.get(dice_num, 0)
            multiplier = 2 if is_city else 1
            income[res] += prob * multiplier
        
        return income

    def resource_urgency_vector(self):
        """
        Assigns a value to each resource based on how soon it is needed in the goal queue.
        Sooner = higher weight. Later = more discounted.
        """
        urgency = {res: 0.0 for res in self.resources}
        hand = self.resources.copy()
        discount = 1.0

        for goal in self.goal_queue:
            goal_cost = BUILDING_COSTS[goal]
            for res in self.resources:
                required = goal_cost.get(res, 0)
                current = hand[res]
                if required > current:
                    needed = required - current
                    urgency[res] += discount * needed
                    hand[res] = 0
                else:
                    hand[res] -= required
            discount *= DISCOUNT_FACTOR
        
        total = sum(urgency.values())
        if total == 0:
            return {res: 0.0 for res in self.resources}
        return {res: urgency[res] / total for res in self.resources}

    def marginal_value(self):
        return self.resource_urgency_vector()

    def shadow_prices(self):
        expected = self.expected_income()
        value = self.marginal_value()

        prices = {}
        for res in self.resources:
            if expected[res] > 0:
                prices[res] = value[res] / expected[res]
            elif value[res] > 0:
                prices[res] = 1000  # Needed but no access
            else:
                prices[res] = 0.0
        return prices

    def __str__(self):
        return f"Player {self.name} | Resources: {self.resources} | Buildings: {self.buildings} | Goal Queue: {self.goal_queue}"


if __name__ == '__main__':
    # Create player
    p1 = Player("Alice")
    
    # Give her some resources
    p1.resources['brick'] = 1
    p1.resources['grain'] = 1
    p1.resources['wool'] = 0
    p1.resources['ore'] = 0
    p1.resources['lumber'] = 0



    # Simulate that Alice has:
    # - a settlement on 8-brick
    # - a settlement on 5-grain
    # - a city on 10-wool
    # (this affects income probabilities)
    p1.resource_sources = [
        ('brick', 8, False),  # 5/36 prob × 1
        ('grain', 5, False),  # 4/36 × 1
        ('lumber', 10, True)    # 3/36 × 2 (city = 2 cards)

    ]

    print("=== Player Status ===")
    print(p1)

    print("\n=== Expected Income ===")
    expected = p1.expected_income()
    for res, val in expected.items():
        print(f"{res}: {val:.3f}")

    print("\n=== Marginal Value ===")
    mv = p1.marginal_value()
    for res, val in mv.items():
        print(f"{res}: {val:.3f}")

    print("\n=== Shadow Prices ===")
    prices = p1.shadow_prices()
    for res, val in prices.items():
        if val == float('inf'):
            print(f"{res}: inf (desperately needed but unobtainable)")
        else:
            print(f"{res}: {val:.3f}")
