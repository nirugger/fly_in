from parser import Parser, parse_argv
from src.graph import Graph
from src.pathfinder import Pathfinder
from src.scheduler import Scheduler
import sys


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
    print(graph.drones)

    for drone in graph.drones:
        print(f"\n{drone.drone_id}: ")
        for turn, zone in drone.path:
            print(f"turn: {turn} - moved to {zone.name}")
