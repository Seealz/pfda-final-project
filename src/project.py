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
        self.type = move_type
        self.power = power
        self.pp = pp
        self.sound = pygame.mixer.Sound(sound) if sound and os.path.exists(sound) else None
        self.effect_image = effect_image
        self.is_physical = is_physical

    def play_sound(self):
        if self.sound:
            self.sound.play()

# Moves List, is_physical=True = Sprite move towards opponent, if False then fx plays
MOVES = {
    "Tackle": Move("Tackle", "Normal", 40, 35, "assets/sounds/tackle.wav", is_physical=True),
    "Ember": Move("Ember", "Fire", 50, 25, "assets/sounds/ember.wav", "assets/effects/ember.png", is_physical=False),
    "Water Gun": Move("Water Gun", "Water", 40, 25, "assets/sounds/water_gun.wav", "assets/effects/watergun.png", is_physical=False)
}

class Monsoons:
    def __init__(self, name, types, stats, moves):
        self.name = name
        self.types = types
        self.stats = stats
        self.moves = [MOVES[name] for name in move_names]
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
    self.animate_attack(screen, opponent, move)
    move.play_sound()
    damage = self._calculate_damage(move, opponent)
    opponent.take_damage(damage)
    return True, f"{self.name} used {move.name}!"
    
def _calculate_damage(self, move, opponent):
    stab = 1.5 if move.type in self.types else 1.0
    effectiveness = TYPE_EFFECTIVENESS[move.type][opponent.types[0]]
    base = (move.power * self.stats["attack"] / opponent.stats["defense"])
    return int(base * stab * effectiveness * random.uniform(0.85, 1.0))

    
def take_damage(self, amount):
    self.stats["hp"] = max(0, self.stats["hp"] - amount)
    return self.stats["hp"] <= 0

def animate_attack(self, screen, opponent, move):
    # Initial positions for the player and opponent
    player_start_x = 100    # Player's X starting position
    player_start_y = 300    # Player's Y starting position 
    opponent_start_x = 500  # Opponent's starting X position
    opponent_start_y = 100  # Opponent's starting Y position
    
    # End positions, Where the player and opponent will meet
    player_end_x = opponent_start_x
    player_end_y = opponent_start_y
    opponent_end_x = player_start_x
    opponent_end_y = player_start_y

    # Time of animation in milliseconds
    duration = 1000
    steps = duration // 100  # Number of steps in the animation (frame rate control)
    dx = (player_end_x - player_start_x) / steps  # X movement per step
    dy = (player_end_y - player_start_y) / steps  # Y movement per step
    
    # For the opponent's movement (they move towards the player too)
    opponent_dx = (opponent_end_x - opponent_start_x) / steps
    opponent_dy = (opponent_end_y - opponent_start_y) / steps
   
   # This loads special effect images
    effect_image = None
    if move.effect_image:
        effect_image = pygame.image.load(move.effect_image)
        effect_pos_x, effect_pos_y = player_start_x, player_start_y  # Starting position for special effect

    for step in range(steps):
        screen.fill(BG_COLOR)  # This clears the screen each frame

    # This animates physical movement 
        current_player_x = player_start_x + dx * step
        current_player_y = player_start_y + dy * step
        screen.blit(self.front_sprite, (current_player_x, current_player_y)) # This draws player's sprite

        current_opponent_x = opponent_start_x + opponent_dx * step
        current_opponent_y = opponent_start_y + opponent_dy * step
        screen.blit(opponent.front_sprite, (current_opponent_x, current_opponent_y))  # This draws opponent's sprite

        # This animates special effects
        if move.effect_image:
            screen.blit(effect_image, (effect_pos_x, effect_pos_y))  # This draws the effect
            effect_pos_x += dx  # This moves the effect towards the opponent
            effect_pos_y += dy

        pygame.display.flip()  # This updates the display
        pygame.time.delay(100) # This controls the animation speed

    # This moves both player and opponent back to their original positions
    for step in range(steps):
        screen.fill(BG_COLOR)  # This clears the screen each frame


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_HEIGHT, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock - pygame.time.Clock()


    if__name__ == "__main__":
    main()