"""Main module of the Fly In Simulator."""
import pygame
from src.flyin import FlyInSimulator

if __name__ == "__main__":
    pygame.init()
    simulator = FlyInSimulator()
    # simulator.print_output()
    simulator.run()
