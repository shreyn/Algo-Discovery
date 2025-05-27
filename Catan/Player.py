#### GAME INFO ####
BUILDING_COSTS = {
    'road':      {'brick': 1, 'lumber': 1},
    'settlement': {'brick': 1, 'lumber': 1, 'grain': 1, 'wool': 1},
    'city':      {'grain': 2, 'ore': 3},
    'dev_card':  {'grain': 1, 'ore': 1, 'wool': 1}
}


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

        self.current_goal = 'settlement'
    
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

        for res in self.resources: # add resources that aren't in the goal at all
            if res not in goal_cost and self.resources[res] > 0:
                surplus[res] = self.resources[res]

        return shortage, surplus
    
    def __str__(self):
        return f"Player {self.name} | Resources: {self.resources} | Buildings: {self.buildings} | Goal: {self.current_goal}"
    

# p1 = Player("Alice")
# p1.resources['brick'] = 1
# p1.resources['grain'] = 1
# p1.resources['wool'] = 3

# p1.current_goal = 'settlement'

# shortage, surplus = p1.resource_delta()
# print(p1)
# print("Shortage:", shortage)
# print("Surplus:", surplus)

