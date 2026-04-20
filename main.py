from parser import Parser, parse_argv
from src.zone import Zone
from src.drone import Drone
from src.graph import Graph
from src.pathfinder import Pathfinder
from src.scheduler import Scheduler
import sys


def print_output(drones: list[Drone]) -> None:

    turn_map = _build_turn_map(drones)

    for t, drone_zone in turn_map.items():
        line = f"turn {t}: "
        for drone, zone in drone_zone:
            if zone.is_start:
                continue
            line += f"D{drone}-{zone.name} "
        print(line)
    print()


def _build_turn_map(drones: list[Drone]) -> dict[int, list[tuple[int, Zone]]]:

    max_turn = max(
        turn for drone in drones
        for turn, _ in drone.path
    )

    turn_map: dict[int, list[tuple[int, Zone]]] = {
        t: [] for t in range(1, max_turn + 1)
    }

    for drone in drones:
        for t, zone in drone.path:
            if t == 0:
                continue
            turn_map[t].append((drone.drone_id, zone))
    return turn_map


if __name__ == "__main__":

    try:
        parser = Parser(parse_argv(sys.argv))
        raw_data = parser.parse()

    except FileNotFoundError:
        print("[ERROR]: "
              "expected usage:\ninsert <map_name> or leave empty")
        sys.exit(1)

    graph = Graph.build(raw_data)
    pathfinder = Pathfinder(graph)
    scheduler = Scheduler(graph, pathfinder)
    scheduler.schedule_drones()

    drones = graph.drones
    print_output(drones)
