"""Central location for MiniPac tuning constants and asset paths."""

from pathlib import Path


TILE_SIZE = 36
FPS = 60
POWER_DURATION = 10.0
# Seconds needed to move from one grid cell to the next
PLAYER_MOVE_TIME = 0.2
GHOST_MOVE_TIME = 0.2
# Frightened ghosts take longer to cross a tile (must be > 1.0)
GHOST_FRIGHTENED_SPEED_SCALE = 2.0

PLAYER_START = (10, 15)

LEVEL_LAYOUT = [
    "#####################",
    "#.........#.........#",
    "#o###.###.#.###.###o#",
    "#...................#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#####.### # ###.#####",
    "    #.#   G   #.#    ",
    "#####.# ## ## #.#####",
    "     .  #GGG#  .     ",
    "#####.# ##### #.#####",
    "    #.#       #.#    ",
    "#####.# ##### #.#####",
    "#.........#.........#",
    "#.###.###.#.###.###.#",
    "#o..#.....P.....#..o#",
    "###.#.#.#####.#.#.###",
    "#.....#...#...#.....#",
    "#.#######.#.#######.#",
    "#...................#",
    "#####################",
]

ASSETS_DIR = Path(__file__).resolve().parent / "assets"

