"""Output writer for the Fly In simulation.

This module formats and writes the per-turn drone movements to a text
file for the currently selected map.
"""

from parser import RED, YELLOW, RESET

from src.zone import Zone
from src.drone import Drone

import pygame
import sys
import os


output_path: str = "output/"
map_registry: dict[str, str] = {
    'maps/easy/01_linear_path.txt': 'linear_path',
    'maps/easy/02_simple_fork.txt': 'simple_fork',
    'maps/easy/03_basic_capacity.txt': 'basic_capacity',
    'maps/medium/01_dead_end_trap.txt': 'dead_end_trap',
    'maps/medium/02_circular_loop.txt': 'circular_loop',
    'maps/medium/03_priority_puzzle.txt': 'priority_puzzle',
    'maps/hard/01_maze_nightmare.txt': 'maze_nightmare',
    'maps/hard/02_capacity_hell.txt': 'capacity_hell',
    'maps/hard/03_ultimate_challenge.txt': 'ultimate_challenge',
    'maps/challenger/01_the_impossible_dream.txt': 'the_impossible_dream',
    'maps/custom/01_custom_delta_v2.txt': 'river_delta',
    'maps/custom/02_feedback_loop_puzzle.txt': 'feedback_loop',
    'maps/custom/03_custom_highway.txt': 'highway_jam',
    'maps/custom/04_custom_labyrinth_city.txt': 'labyrinth_city',
    'maps/custom/00_a_day_off.txt': 'a_day_off'
}


def _build_turn_map(
        drones: list[Drone]
        ) -> dict[int, list[tuple[int, Zone]]]:
    """Build a map of turn numbers to drone positions.

    Args:
        drones (list[Drone]): list of drones in the simulation.

    Returns:
        dict[int, list[tuple[int, Zone]]]: mapping from turn number to
        a list of tuples containing drone id and zone.
    """
    max_turn = max(
        turn for drone in drones
        for turn, _ in drone.path
    )

    turn_map: dict[int, list[tuple[int, Zone]]] = {
        t: [(drone.drone_id, zone)
            for drone in drones for turn, zone in drone.path
            if turn == t]
        for t in range(1, max_turn + 1)
    }

    return turn_map


def write_output(
        drones: list[Drone],
        path_to_map: str
        ) -> None:
    """Print each drone movement by turn.

    The output excludes start hub positions and shows the
    destination zone for each drone at every simulated turn.
    """
    turn_map = _build_turn_map(drones)

    try:
        path = output_path + map_registry[path_to_map] + '.txt'
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            for _, drone_zone in turn_map.items():
                line: list[str] = []
                for drone, zone in drone_zone:
                    if zone.is_start:
                        continue
                    line.append(f"D{drone}-{zone.name}")
                f.write(" ".join(line))
                f.write('\n')

    except KeyError:
        print(f"{YELLOW}[WARNING]:{RESET} "
              f"map not found in registry")
        pygame.quit()
        sys.exit(1)

    except FileNotFoundError:
        print(f"{RED}[ERROR]:{RESET} "
              f"directory for {path} doesn't exist")
        pygame.quit()
        sys.exit(1)

    except PermissionError:
        print(f"{RED}[ERROR]:{RESET} "
              f"file {path} doesn't have necessary permissions")
        pygame.quit()
        sys.exit(1)

    except OSError as e:
        print(f"{RED}[ERROR]:{RESET} "
              f"couldn't write to {path}: {e}")
        pygame.quit()
        sys.exit(1)
