from parser import Parser, ParseError
from src.builder import Builder
import sys


if __name__ == "__main__":

    try:
        path = sys.argv[1]
    except Exception:
        print("\nfuck you\n")
        sys.exit(1)
    parser = Parser(path)
    try:
        raw_data = parser.parse()
        builder = Builder(raw_data)

    except ParseError as e:
        print(str(e))
        sys.exit(1)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
