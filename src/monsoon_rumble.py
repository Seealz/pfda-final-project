import pygame
import random
import os

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (245, 245, 245)
WHITE = (255, 255, 255)
SPRITE_SCALE_FACTOR = 7
MOVE_PANEL_COLOR = (220, 220, 220)
TEXT_BOX_COLOR = (240, 240, 240)

# Win/Loss tracking
wins = 0
losses = 0

# Type chart
TYPES = ["Fire", "Water", "Plant", "Normal", "Wind", "Electric", "Psychic", "Earth"]
TYPE_EFFECTIVENESS = {t: {op: 1.0 for op in TYPES} for t in TYPES}
TYPE_EFFECTIVENESS["Fire"].update({"Plant": 2.0, "Normal": 2.0, "Earth": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Water"].update({"Fire": 2.0, "Earth": 2.0, "Plant": 0.5, "Electric": 0.5})
TYPE_EFFECTIVENESS["Plant"].update({"Water": 2.0, "Earth": 2.0, "Fire": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Wind"].update({"Fire": 2.0, "Plant": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Electric"].update({"Water": 2.0, "Wind": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Psychic"].update({"Psychic": 0.5})
TYPE_EFFECTIVENESS["Earth"].update({"Fire": 2.0, "Electric": 2.0, "Water": 0.5, "Plant": 0.5})

class Move:
    def __init__(self, name, type, power, pp):
        self.name = name
        self.type = type
        self.power = power
        self.max_pp = pp
        self.pp = pp

TYPE_COLORS = {
    "Fire": (255, 80, 80),
    "Water": (80, 80, 255),
    "Plant": (80, 200, 80),
    "Normal": (200, 200, 200),
    "Wind": (180, 180, 255),
    "Electric": (255, 255, 100),
    "Psychic": (255, 100, 255),
    "Earth": (170, 120, 60)
}

