import pygame
import random
import os

# These are the Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0, 0, 0)

class Monsoons:
    def __init__(self, name, element, stats, moves):
        self.name = name
        self.element = element
        self.stats = stats
        self.moves = [Move(move) for move in moves]
        self.load_sprites()

# This is where the main Monsoon Front and Back sprites are loaded
    def load_sprites(self):
        



def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock - pygame.time.Clock()