# test.py

from Players import Player, RESOURCES, DICE_PROBABILITIES
from FullEngine import TradeEngine
from Agents import ParameterizedTrader
import random

# Fixed goal queue
GOAL_QUEUE = ['road', 'settlement', 'city', 'dev_card']

def simulate_game(
    alpha1: float, beta1: float,
    alpha2: float, beta2: float,
    seed: int = 42
):
    rng = random.Random(seed)

    # Create players with individual (alpha, beta)
    p1 = Player("Alice", personality=ParameterizedTrader(alpha1, beta1))
    p2 = Player("Bob",   personality=ParameterizedTrader(alpha2, beta2))

    # --- Fixed initial tiles ---
    p1.resources = {r: 0 for r in RESOURCES}
    p1.resource_sources = [
        (res, rng.choice(list(DICE_PROBABILITIES.keys())), False)
        for res in ['lumber', 'brick', 'wool']
    ]
    p1.buildings  = []
    p1.goal_queue = GOAL_QUEUE.copy()

    p2.resources = {r: 0 for r in RESOURCES}
    p2.resource_sources = [
        (res, rng.choice(list(DICE_PROBABILITIES.keys())), False)
        for res in ['ore', 'wool', 'grain']
    ]
    p2.buildings  = []
    p2.goal_queue = GOAL_QUEUE.copy()
    # ---------------------------

    initial_tiles = {
        p1.name: list(p1.resource_sources),
        p2.name: list(p2.resource_sources),
    }

    engine = TradeEngine([p1, p2], dice_rolls=None, rng=rng)

    rounds_log = []
    round_num = 0

    while True:
        round_num += 1
        roll, trades, builds = engine.run_trading_round()
        tiles_snapshot = {
            p1.name: list(p1.resource_sources),
            p2.name: list(p2.resource_sources),
        }

        rounds_log.append({
            'round': round_num,
            'roll': roll,
            'trades': trades,
            'builds': builds,
            'tiles': tiles_snapshot
        })

        for p in (p1, p2):
            if not p.goal_queue:
                print(f"\n!!! {p.name} wins in {round_num} rounds !!!\n")
                return rounds_log, p.name, initial_tiles

        if round_num > 200:
            print("\n--- No winner after 200 rounds ---\n")
            return rounds_log, None, initial_tiles

def main():
    # Example: Alice is greedy (alpha=1.3, beta=1.3), Bob is fair (alpha=1.0, beta=0.9)
    rounds_log, winner, initial_tiles = simulate_game(
        alpha1=0.5, beta1=0.5,
        alpha2=3.0, beta2=3,
        seed=42
    )

    MENU = """
Select what to display:
  1) Building events
  2) Trade events
  3) Tile ownership progression
  4) Tile income events
  q) Quit
> """
    while True:
        choice = input(MENU).strip().lower()
        if choice == '1':
            print("\n-- Building Events --")
            for e in rounds_log:
                for name, b in e['builds']:
                    print(f"Round {e['round']}: {name} built {b}")
            print()
        elif choice == '2':
            print("\n-- Trade Events --")
            for e in rounds_log:
                for g, r, give, get in e['trades']:
                    print(f"Round {e['round']}: {g} -> {r} gives {give}, gets {get}")
            print()
        elif choice == '3':
            print("\n-- Tile Ownership Progression --")
            print("Initial:")
            for name, tiles in initial_tiles.items():
                print(f" {name}:")
                for res, dice, is_city in tiles:
                    typ = "City" if is_city else "Settlement"
                    print(f"   - {res} @ {dice} ({typ})")
            print()
            for e in rounds_log:
                if e['builds']:
                    print(f"After round {e['round']}:")
                    for name, tiles in e['tiles'].items():
                        print(f" {name}:")
                        for res, dice, is_city in tiles:
                            typ = "City" if is_city else "Settlement"
                            print(f"   - {res} @ {dice} ({typ})")
                    print()
        elif choice == '4':
            print("\n-- Tile Income Events --")
            for e in rounds_log:
                roll = e['roll']
                for name, tiles in e['tiles'].items():
                    for res, dice, is_city in tiles:
                        if dice == roll:
                            amt = 2 if is_city else 1
                            print(f"Round {e['round']}: {name}'s {res}@{dice} produced {amt}")
            print()
        elif choice == 'q':
            print("Exiting.")
            break
        else:
            print("Invalid choice.\n")

    print(f"Simulation complete. Winner: {winner}")

if __name__ == "__main__":
    main()
