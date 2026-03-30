from parser import input_handler
import sys
import random

if __name__ == "__main__":

    try:
        path = sys.argv[1]
    except:
        print("\nfuck you\n")
        sys.exit(1)
        # path = random.choice(map_list)
    try:
        input_handler(sys.argv[1])
    except:
        print("\nfuck you\n")
        sys.exit(1)
