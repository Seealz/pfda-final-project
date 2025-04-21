import pygame
import random
import os

# These are the Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0, 0, 0)

# Typings
TYPES = ["Fire", "Water", "Plant", "Normal", "Wind", "Electric", "Psychic", "Earth"]

TYPE_EFFECTIVENESS = {t: {op: 1.0 for op in TYPES} for t in TYPES}

# Defines strengths and weaknesses
TYPE_EFFECTIVENESS["Fire"].update({"Plant": 2.0, "Normal": 2.0, "Earth": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Water"].update({"Fire": 2.0, "Earth": 2.0, "Plant": 0.5, "Electric": 0.5})
TYPE_EFFECTIVENESS["Plant"].update({"Water": 2.0, "Earth": 2.0, "Fire": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Normal"].update({"Psychic": 1.0, "Wind": 1.0})
TYPE_EFFECTIVENESS["Wind"].update({"Fire": 2.0, "Plant": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Electric"].update({"Water": 2.0, "Wind": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Psychic"].update({"Normal": 1.0, "Water": 1.0, "Psychic": 0.5})
TYPE_EFFECTIVENESS["Earth"].update({"Fire": 2.0, "Electric": 2.0, "Water": 0.5, "Plant": 0.5})

class Move:
    def __init__(self, name, move_type, power, pp, sound=None, effect_image=None, is_physical=False):
        self.name = name
        self.move_type = move_type  # e.g., 'Fire', 'Water', 'Normal'
        self.power = power
        self.pp = pp
        self.sound = pygame.mixer.Sound(sound) if sound else None
        self.effect_image = effect_image  # Special effect image
        self.is_physical = is_physical   # physical movement

    def play_sound(self):
        if self.sound:
            self.sound.play()

# Moves List, is_physical=True = Sprite move towards opponent, if False then fx plays
MOVES = {
     "Tackle": Move(
        name="Tackle",
        move_type="Normal",
        power=40,
        pp=35,
        sound="assets/sounds/tackle.wav",
        is_physical=True
     ),
     "Ember": Move(
        name="Ember",
        move_type="Fire",
        power=50,
        pp=25,
        sound="assets/sounds/ember.wav",
        effect_image="assets/effects/ember.png",
        is_physical=False
     ),
    "Water Gun": Move(
        name="Water Gun",
        move_type="Water",
        power=40,
        pp=25,
        sound="assets/sounds/water_gun.wav",
        effect_image="assets/effects/watergun.png",
        is_physical=False
    )
}

class Monsoons:
    def __init__(self, name, types, stats, moves):
        self.name = name
        self.types = types
        self.stats = stats
        self.moves = [Move(move) for move in moves]
        self.load_sprites()

# This is where the main Monsoon Front and Back sprites are loaded
    def load_sprites(self):
        try:
            self.front_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_front.png").convert_alpha()
            self.back_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_back.png").convert_alpha()
        except:
            self._create_placeholder_sprites()

# This is placeholder sprites
    def _create_placeholder_sprites(self):
        placeholder_sprite = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(placeholder_sprite, (255, 0, 255), (0, 0, 100, 100))
        self.front_sprite = self.back_sprite = placeholder_sprite

# This is how a move is used, it checks for pp, plays the attack animation and sound, and checks for type effectiveness
    def attack(self, move_index, opponent, screen):
        move = self.moves[move_index]
        if move.pp <= 0:
            return False, f"{move.name} has no PP left!"
        move.pp -= 1
        self.animate_attack(screen, opponent)
        move.play_sound()
        damage = self._calculate_damage(move, opponent)
        opponent.take_damage(damage)
        return True, f"{self.name} used {move.name}!"
    
    def _calculate_damage(self, move, opponent):
        stab_bonus = 1.5 if move.type in self.types else 1.0
        effectiveness = TYPE_EFFECTIVENESS.get(move.type, {}).get(opponent.types[0], 1.0)
        base_damage = (move.power * self.stats["attack"] / opponent.stats["defense"]) * effectiveness
        return int(base_damage * random.uniform(0.85, 1.0))
    
    def take_damage(self, amount):
        self.stats["hp"] = max(0, self.stats["hp"] - amount)
        return self.stats["hp"] <= 0
    
    # This is the way a move is animated
    def animate_attack(self, screen, opponent):
        # Positions for the player and opponent
        player_start_x = 100 #Players sprite position
        player_start_y = 300
        player_end_x = 500  #Opps sprite position
        player_end_y = 100  

    # This is the animation time, it's in milliseconds
        duration = 1000
        start_time = pygame.time.get_ticks()

    # This loads fx based on move type


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock - pygame.time.Clock()


    if__name__ == "__main__":
    main()