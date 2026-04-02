from parser import Parser
from src.builder import Builder
from src.graph import Graph
import sys


if __name__ == "__main__":

    try:
        parser = Parser(Parser.parse_argv(sys.argv))
        raw_data = parser.parse()

    except FileNotFoundError:
        print("[ERROR]: "
              "expected usage:\ninsert <map_name> or leave empty")
        sys.exit(1)

    builder = Builder(raw_data)
    zones = builder.build_zone_list()
    graph = Graph(builder.build_adjacency())
    for zone in zones:
        print("zone:", str(zone))
        print("neighbor:", graph.get_neighbors(zone)[0][0].name)
        print("cost:", graph.get_neighbors(zone)[0][1])
        print()

    # for key in adjacency:
    #     print(f"Zone:           '{key.name}'")
    #     print("Connected with:", end=' ')
    #     for value in adjacency[key]:
    #         connected_zone = value.get_other(key)
    #         print(f"'{connected_zone.name}'", end=' ')
    #     print('\n')
