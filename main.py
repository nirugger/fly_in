from parser import Parser, parse_argv
from src.graph import Graph
from src.pathfinder import Pathfinder
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
    finder = Pathfinder(graph)
    finder.EK()

    # for zone in graph.grid:
    #     neighbors = graph.get_neighbors(zone)
    #     print("zone:", str(zone))
    #     if neighbors:
    #         print("neighbor:", neighbors[0][0].name)
    #         print("cost:", neighbors[0][1])
    #     else:
    #         print("neighbor: (none)")
    #         print("cost: -")
    #     print()
