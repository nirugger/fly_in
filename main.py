"""Main module of the Fly In Simulator."""

from parser import RED, RESET
from src.flyin import FlyInSimulator

import pygame
import sys

if __name__ == "__main__":
    try:
        pygame.init()
        simulator = FlyInSimulator()
        simulator.run()

    except KeyboardInterrupt as e:
        print(f"{RED}[FROCED]: {RESET}"
              "the program was closed by a keyboard interrupt command")
        print(str(e))
        pygame.quit()
        sys.exit(1)

    except Exception as e:
        print(F"{RED}[WHOOPS]: {RESET}"
              "an unexpected error occurred:")
        print(str(e))

    finally:
        print("\n\nDrones are dangerous.\n\n")

    # pygame.init()
    # simulator = FlyInSimulator()
    # simulator.run()
