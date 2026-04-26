import os
import random

SPAN: float = 25.0

COLORS: dict[str, tuple[int, int, int]] = {
    "red": (255, 182, 185),
    "green": (182, 235, 182),
    "blue": (182, 210, 255),
    "orange": (255, 218, 182),
    "yellow": (255, 245, 182),
    "purple": (218, 182, 255),
    "cyan": (182, 245, 245),
    "pink": (255, 182, 230),
    "lime": (210, 255, 182),
    "brown": (210, 195, 175),
    "magenta": (245, 182, 235),
    "gold": (255, 235, 182),
    "violet": (200, 182, 255),
    "crimson": (255, 190, 195),
    "maroon": (220, 185, 185),
    "default": (210, 210, 215),
}


MAPS = {
    # '01_e': 'maps/easy/01_linear_path.txt',
    '01_e': 'maps/test/color_test.txt',
    '02_e': 'maps/easy/02_simple_fork.txt',
    '03_e': 'maps/easy/03_basic_capacity.txt',
    '01_m': 'maps/medium/01_dead_end_trap.txt',
    '02_m': 'maps/medium/02_circular_loop.txt',
    '03_m': 'maps/medium/03_priority_puzzle.txt',
    '01_h': 'maps/hard/01_maze_nightmare.txt',
    '02_h': 'maps/hard/02_capacity_hell.txt',
    '03_h': 'maps/hard/03_ultimate_challenge.txt',
    '04_h': 'maps/challenger/01_the_impossible_dream.txt'
}

FONT_DIR: str = os.path.join(os.path.dirname(__file__), 'assets')
FONT_REGULAR: str = os.path.join(FONT_DIR, 'JetBrainsMono-Regular.ttf')
FONT_BOLD: str = os.path.join(FONT_DIR, 'JetBrainsMono-Bold.ttf')

TEXT_COLOR: tuple[int, int, int] = (242, 242, 242)
DRONE_COLOR: tuple[int, int, int] = (220, 110, 110)

MIN_INT: int = -2147483648
MAX_INT: int = 2147483647
RAND_INT: int = random.randint(MIN_INT, MAX_INT)
