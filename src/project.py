import pygame
import random
import os

# These are the Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0, 0, 0)

#Typings
TYPE_EFFECTIVENESS = {
    "Fire":     {"Plant": 2.0, "Normal": 2.0, "Electric": 1.0, "Psychic": 1.0, "Earth": 0.5, "Wind": 0.5},
    "Water":    {"Fire": 2.0, "Earth": 2.0, "Plant": 0.5, "Electric": 0.5},
    "Plant":    {"Water": 2.0, "Earth": 2.0, "Fire": 0.5, "Wind": 0.5},
    


}

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


    if__name__ == "__main__":
    main()