from parser import Parser, ParseError
import sys


if __name__ == "__main__":

    try:
        path = sys.argv[1]
    except Exception:
        print("\nfuck you\n")
        sys.exit(1)
    parser = Parser(path)
    try:
        for key, value in parser.parse().items():
            if key == 'nb_drones':
                print(key, value)
            else:
                print(f"{key}:")
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"{k}: {v}")
                else:
                    for e in value:
                        print(e)

    except ParseError as e:
        print(str(e))
        sys.exit(1)
    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
