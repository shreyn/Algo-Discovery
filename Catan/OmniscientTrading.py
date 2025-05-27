from Player import Player

def propose_trade(p1: Player, p2: Player):
    s1, x1 = p1.resource_delta()
    s2, x2 = p2.resource_delta()

    for want in s1:
        if want in x2 and x2[want] > 0:
            for give in x1:
                if give in s2 and s2[give] > 0:
                    return ({give:1}, {want:1})

    return None  # no trade found


if __name__ == "__main__":
    alice = Player("Alice")
    bob = Player("Bob")

    alice.resources = {
        'brick': 1,
        'grain': 0,
        'wool': 3,
        'lumber': 3,
        'ore': 0
    }
    alice.current_goal = 'settlement'

    bob.resources = {
        'brick': 1,
        'grain': 3,
        'wool': 0,
        'lumber': 0,  
        'ore': 0
    }
    bob.current_goal = 'road'


    trade = propose_trade(bob, alice)
    print(f"Suggested trade (Bob -> Alice): {trade}")
