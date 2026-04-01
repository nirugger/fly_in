from parser import Parser, ParseError
from src.builder import Builder
import sys


if __name__ == "__main__":

    try:
        path = sys.argv[1]
        parser = Parser(path)
        raw_data = parser.parse()
    except Exception as e:
        print(str(e))
        print("\nfuck you\n")
        sys.exit(1)
    builder = Builder(raw_data)
    for key in builder.adjacency.keys():
        print(f"Zone: {key.name}")
        for value in builder.adjacency[key]:
            print("Connected zones: "
                  f"{value.zone_a.name}, "
                  f"{value.zone_b.name}")
