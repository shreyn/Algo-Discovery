# Agents.py

from typing import Dict, List, Optional, Tuple

class Personality:
    def propose_trade(self, player, others) -> Optional[Tuple[Dict[str,int],Dict[str,int]]]:
        raise NotImplementedError
    def accept_trade(self, receiver, offer_give:Dict[str,int], offer_get:Dict[str,int], proposer) -> bool:
        raise NotImplementedError

class ParameterizedTrader(Personality):
    def __init__(self, alpha: float, beta: float):
        self.alpha = alpha
        self.beta  = beta

    def propose_trade(self, player, others):
        shortage, surplus = player.resource_delta()
        if not shortage or not surplus:
            return None
        prices = player.shadow_prices()
        want = max(shortage, key=lambda r: shortage[r] * prices[r])
        give = min(surplus,  key=lambda r: prices[r])
        return {give:1}, {want:1}

    def accept_trade(self, receiver, offer_give, offer_get, proposer):
        # affordability check
        for r,c in offer_get.items():
            if receiver.resources.get(r,0) < c:
                return False
        prices = receiver.shadow_prices()
        val_in  = sum(prices[r]*c for r,c in offer_give.items())
        val_out = sum(prices[r]*c for r,c in offer_get.items())
        return val_in >= self.beta * val_out
