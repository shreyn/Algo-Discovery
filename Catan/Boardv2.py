# Boardv2.py

import pygame
import sys
import math

pygame.init()

# -------------------------------------------------------------------
# SCREEN & RENDER SURFACE SETUP
# -------------------------------------------------------------------
DISPLAY_INFO   = pygame.display.Info()
SCREEN_WIDTH   = DISPLAY_INFO.current_w
SCREEN_HEIGHT  = DISPLAY_INFO.current_h

# use 85% of the screen
WIDTH, HEIGHT    = int(SCREEN_WIDTH * 0.85), int(SCREEN_HEIGHT * 0.85)
RENDER_SCALE     = 15
RENDER_WIDTH     = WIDTH * RENDER_SCALE
RENDER_HEIGHT    = HEIGHT * RENDER_SCALE

SCREEN         = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
render_surface = pygame.Surface((RENDER_WIDTH, RENDER_HEIGHT))


# -------------------------------------------------------------------
# COLORS
# -------------------------------------------------------------------
COLORS = {
    'brick':      pygame.Color('#c57440'),
    'lumber':     pygame.Color('#2b4a27'),
    'grain':      pygame.Color('#facd40'),
    'wool':       pygame.Color('#a8cd4b'),
    'ore':        pygame.Color('#534e61'),
    'desert':     pygame.Color('#deb887'),
    'background': pygame.Color('white'),
    'dice_bg':    pygame.Color('yellow'),
}
PLAYER_COLORS = {
    'Alice': pygame.Color('red'),
    'Bob':   pygame.Color('blue'),
}


# -------------------------------------------------------------------
# HEX GEOMETRY
# -------------------------------------------------------------------
HEX_SIZE    = RENDER_WIDTH // 17
CENTER_X    = RENDER_WIDTH // 2
CENTER_Y    = RENDER_HEIGHT // 2

def axial_to_cartesian(q, r, size=HEX_SIZE):
    x = CENTER_X + size * math.sqrt(3) * (q + r/2)
    y = CENTER_Y + size * 1.5 * r
    return x, y

def hex_vertices(q, r, size=HEX_SIZE):
    cx, cy = axial_to_cartesian(q, r, size)
    return [
        (
            cx + size * math.cos(math.radians(60*i - 30)),
            cy + size * math.sin(math.radians(60*i - 30))
        )
        for i in range(6)
    ]


# -------------------------------------------------------------------
# STATIC BEGINNER SETUP
# -------------------------------------------------------------------
BEGINNER_HEXES = [
    {'q':  0, 'r': -2, 'resource':'grain',  'number': 4},
    {'q':  1, 'r': -2, 'resource':'brick',  'number': 5},
    {'q':  2, 'r': -2, 'resource':'wool',   'number': 9},
    {'q': -1, 'r': -1, 'resource':'ore',    'number': 2},
    {'q':  0, 'r': -1, 'resource':'grain',  'number':11},
    {'q':  1, 'r': -1, 'resource':'lumber', 'number': 8},
    {'q':  2, 'r': -1, 'resource':'grain',  'number':10},
    {'q': -2, 'r':  0, 'resource':'brick',  'number': 5},
    {'q': -1, 'r':  0, 'resource':'lumber', 'number':12},
    {'q':  1, 'r':  0, 'resource':'wool',   'number': 4},
    {'q':  2, 'r':  0, 'resource':'ore',    'number':10},
    {'q':  0, 'r':  0, 'resource':'desert', 'number': None},
    {'q': -2, 'r':  1, 'resource':'wool',   'number': 6},
    {'q': -1, 'r':  1, 'resource':'ore',    'number': 3},
    {'q':  0, 'r':  1, 'resource':'lumber', 'number': 3},
    {'q':  1, 'r':  1, 'resource':'brick',  'number': 8},
    {'q': -2, 'r':  2, 'resource':'wool',   'number': 6},
    {'q': -1, 'r':  2, 'resource':'lumber', 'number': 4},
    {'q':  0, 'r':  2, 'resource':'grain',  'number':11},
]

BEGINNER_BUILDINGS = [
    {'vertex': hex_vertices(0,-2)[2], 'player':'Alice', 'building':'settlement'},
    {'v1':      hex_vertices(0,-2)[2], 'v2':      hex_vertices(0,-2)[3], 'player':'Alice'},
    {'vertex': hex_vertices(2,-1)[4], 'player':'Alice', 'building':'city'},
    {'v1':      hex_vertices(2,-1)[4], 'v2':      hex_vertices(1, 0)[5], 'player':'Alice'},
    {'vertex': hex_vertices(-2,0)[0],'player':'Bob',   'building':'settlement'},
    {'v1':      hex_vertices(-2,0)[0], 'v2':      hex_vertices(-1,0)[3], 'player':'Bob'},
    {'vertex': hex_vertices(1,2)[5], 'player':'Bob',   'building':'settlement'},
    {'v1':      hex_vertices(1,2)[5], 'v2':      hex_vertices(1,1)[0], 'player':'Bob'},
]

FONT = pygame.font.SysFont(None, HEX_SIZE//2)


# -------------------------------------------------------------------
# DRAW FUNCTION
# -------------------------------------------------------------------
def draw_board(hexes, buildings=None, size=HEX_SIZE, show_numbers=True):
    render_surface.fill(COLORS['background'])

    # tiles + dice‐circles + numbers
    for h in hexes:
        verts = hex_vertices(h['q'], h['r'], size)
        pygame.draw.polygon(render_surface,  COLORS[h['resource']], verts)
        pygame.draw.polygon(render_surface, pygame.Color('black'), verts, 2)

        if show_numbers and h['number'] is not None:
            cx, cy = axial_to_cartesian(h['q'], h['r'], size)
            r = size//3
            pygame.draw.circle(render_surface, COLORS['dice_bg'], (int(cx),int(cy)), r)
            pygame.draw.circle(render_surface, pygame.Color('black'),   (int(cx),int(cy)), r, 2)
            txt = FONT.render(str(h['number']), True, pygame.Color('black'))
            rect = txt.get_rect(center=(cx,cy))
            render_surface.blit(txt, rect)

    # roads
    if buildings:
        for b in buildings:
            if 'v1' in b and 'v2' in b:
                pygame.draw.line(
                    render_surface,
                    PLAYER_COLORS[b['player']],
                    b['v1'], b['v2'],
                    max(1, size//8)
                )

    # settlements & cities
    if buildings:
        for b in buildings:
            if 'vertex' in b:
                x,y   = b['vertex']
                color = PLAYER_COLORS[b['player']]
                btype = b.get('building','settlement')
                if btype=='settlement':
                    s = size//4
                    rect = pygame.Rect(x-s,y-s,2*s,2*s)
                    pygame.draw.rect(render_surface, color, rect)
                    pygame.draw.rect(render_surface, pygame.Color('black'), rect, 2)
                else:  # city
                    s   = size//3
                    pts = [(x,y-s),(x+s,y),(x,y+s),(x-s,y)]
                    pygame.draw.polygon(render_surface, color,     pts)
                    pygame.draw.polygon(render_surface, pygame.Color('black'), pts, 2)

    # down‐scale & blit
    scaled = pygame.transform.smoothscale(render_surface, (WIDTH, HEIGHT))
    SCREEN.blit(scaled, (0,0))
    pygame.display.flip()


# -------------------------------------------------------------------
# SELF‐RUN DEMO
# -------------------------------------------------------------------
def main():
    # only here do we set *this* caption:
    pygame.display.set_caption("Catan Board Visualization – Boardv2.py")
    clock = pygame.time.Clock()
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit(); sys.exit()
        draw_board(BEGINNER_HEXES,
                   buildings=BEGINNER_BUILDINGS,
                   size=HEX_SIZE,
                   show_numbers=True)
        clock.tick(30)


if __name__=='__main__':
    main()
