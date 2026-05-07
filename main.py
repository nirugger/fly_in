"""Main module of the Fly In Simulator."""

from src.flyin import FlyInSimulator
import pygame

if __name__ == "__main__":
    pygame.init()
    simulator = FlyInSimulator()
    simulator.run()
