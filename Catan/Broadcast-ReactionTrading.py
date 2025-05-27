from Player import Player

def generate_offer(player: Player):
    """
    Public offer: (give: {res: 1}, want: {res: 1})
    Based on surplus/shortage.
    """
    shortage, surplus = player.resource_delta()
    for want in shortage:
        for give in surplus:
            return ({give: 1}, {want: 1})
    return None

def would_accept_offer(p: Player, offer_give, offer_get):
    # Do I have what they want?
    for res in offer_get:
        if p.resources[res] > 0:
            # Would I benefit from getting what they offer?
            shortage, _ = p.resource_delta()
            for want in offer_give:
                if want in shortage:
                    return True
    return False


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
    # Alice offers something
    offer = generate_offer(bob)

    # Bob considers whether he’d accept it
    if offer:
        give, get = offer
        if would_accept_offer(alice, give, get):
            print(f"Alice accepts Bob's offer: {give} for {get}")
