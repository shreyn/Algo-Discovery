import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
import numpy as np


class Tile:
    """A single terrain hex on the Catan board."""
    def __init__(self, resource: str, number: int, q: int, r: int):
        self.resource    = resource   # 'brick','lumber','ore','grain','wool','desert'
        self.number      = number     # 2–12 or None for desert
        self.q           = q          # axial coordinate
        self.r           = r
        self.has_robber  = (resource=='desert')
    def __repr__(self):
        return f"<Tile {self.resource!r}@({self.q},{self.r})#{self.number}>"


# flat‐top axial coords for the 19‐hex layout, row by row:
AXIAL_COORDS = [
    (-2,  2), (-1,  2), ( 0,  2),            # 3
    (-2,  1), (-1,  1), ( 0,  1), ( 1,  1),  # 4
    (-2,  0), (-1,  0), ( 0,  0), ( 1,  0), ( 2,  0),  # 5
    (-1, -1), ( 0, -1), ( 1, -1), ( 2, -1),  # 4
    ( 0, -2), ( 1, -2), ( 2, -2)             # 3
]

# pick any layout
# tuple is (resource, number, q, r)
FIXED_TILE_SPECS = [
    ('ore',     9, -2,  2),
    ('grain',   8, -1,  2),
    ('wool',    3,  0,  2),

    ('lumber', 11, -2,  1),
    ('brick',  11, -1,  1),
    ('grain',   6,  0,  1),
    ('ore',     4,  1,  1),

    ('wool',    2, -2,  0),
    ('wool',    5, -1,  0),
    ('desert', None, 0,  0),
    ('grain',  10,  1,  0),
    ('lumber',  9,  2,  0),

    ('brick',  10, -1, -1),
    ('lumber',  6,  0, -1),
    ('ore',     4,  1, -1),
    ('grain',  12,  2, -1),

    ('brick',   3,  0, -2),
    ('wool',    5,  1, -2),
    ('lumber',  8,  2, -2),
]

class Board:
    def __init__(self, tile_specs=None):
        # allow to pass in any tile_specs; default to FIXED_TILE_SPECS
        specs = tile_specs or FIXED_TILE_SPECS
        self.tiles = [Tile(res, num, q, r) for res, num, q, r in specs]

    def draw(self, ax=None, size=1.0):
        color_map = {
            'brick':'#c57440', 'lumber':'#2c4317', 'ore':'#534e61',
            'grain':'#facd40','wool':'#a8cd4b','desert':'#deb887'
        }
        if ax is None:
            fig, ax = plt.subplots(figsize=(8,8))

        for tile in self.tiles:
            # flat‐top axial->Cartesian
            x = size * (3/2 * tile.q)
            y = size * (np.sqrt(3)/2 * tile.q + np.sqrt(3) * tile.r)

            hexagon = RegularPolygon(
                (x, y), numVertices=6, radius=size,
                orientation=np.radians(30),  # flat top
                facecolor=color_map[tile.resource],
                edgecolor='k'
            )
            ax.add_patch(hexagon)

            if tile.number is not None:
                ax.text(x, y, str(tile.number),
                        ha='center', va='center', weight='bold')
            if tile.has_robber:
                ax.text(x, y, 'X', ha='center', va='center')

        ax.set_aspect('equal')
        ax.autoscale_view()
        ax.axis('off')
        plt.show()


if __name__ == "__main__":
    b = Board()             # uses the FIXED_TILE_SPECS layout
    print("Tiles:", len(b.tiles))
    for t in b.tiles:
        print(" ", t)
    b.draw()

if __name__ == "__main__":
    board = Board(variable_setup=True)
    print("Tiles:", len(board.tiles))
    board.draw()

