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
    "Water Gun": Move("Water Gun", "Water", 40, 25, "assets/sounds/water_gun.wav", "assets/effects/watergun.png", is_physical=False),
    "Gust": Move("Gust", "Wind", 40, 25, "assets/sounds/gust.wav", "assets/effects/gust.png", is_physical=False)
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
        player_start_x = 100
        player_start_y = 300
        opponent_start_x = 500
        opponent_start_y = 100

        # End positions, where the player and opponent will meet
        player_end_x = opponent_start_x
        player_end_y = opponent_start_y
        opponent_end_x = player_start_x
        opponent_end_y = player_start_y

        # Time of animation in milliseconds
        duration = 1000
        steps = duration // 100
        dx = (player_end_x - player_start_x) / steps
        dy = (player_end_y - player_start_y) / steps

        # For the opponent's movement
        opponent_dx = (opponent_end_x - opponent_start_x) / steps
        opponent_dy = (opponent_end_y - opponent_start_y) / steps

        # Special effect images
        effect_image = None
        if move.effect_image:
            effect_image = pygame.image.load(move.effect_image)
            effect_pos_x, effect_pos_y = player_start_x, player_start_y

        for step in range(steps):
            screen.fill(BG_COLOR)

            # Animates physical movement
            current_player_x = player_start_x + dx * step
            current_player_y = player_start_y + dy * step
            screen.blit(self.front_sprite, (current_player_x, current_player_y))

            current_opponent_x = opponent_start_x + opponent_dx * step
            current_opponent_y = opponent_start_y + opponent_dy * step
            screen.blit(opponent.front_sprite, (current_opponent_x, current_opponent_y))

            # Animates special effects
            if move.effect_image:
                screen.blit(effect_image, (effect_pos_x, effect_pos_y))
                effect_pos_x += dx
                effect_pos_y += dy

            pygame.display.flip()
            pygame.time.delay(100)

        # Return to original positions
        for step in range(steps):
            screen.fill(BG_COLOR)

            current_player_x = player_end_x - dx * (steps - step)
            current_player_y = player_end_y - dy * (steps - step)
            screen.blit(self.front_sprite, (current_player_x, current_player_y))

            current_opponent_x = opponent_end_x - opponent_dx * (steps - step)
            current_opponent_y = opponent_end_y - opponent_dy * (steps - step)
            screen.blit(opponent.front_sprite, (current_opponent_x, current_opponent_y))

            if move.effect_image:
                screen.blit(effect_image, (effect_pos_x, effect_pos_y))
                effect_pos_x -= dx
                effect_pos_y -= dy

            pygame.display.flip()
            pygame.time.delay(60)

def show_start_screen(screen):
    font = pygame.font.Font(None, 60)
    title_text = font.render("Monsoon Rumble", True, (255, 255, 255))
    prompt_text = pygame.font.Font(None, 36).render("Press SPACE to Start", True, (200, 200, 200))

    while True:
        screen.fill((0, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, 300))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def show_select_screen(screen, all_monsoons):
    font = pygame.font.Font(None, 36)
    selected_index = 0

    while True:
        screen.fill((30, 30, 30))

        title = pygame.font.Font(None, 48).render("Choose Your Monsoon", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        for i, mon in enumerate(all_monsoons):
            text_color = (255, 255, 0) if i == selected_index else (255, 255, 255)
            label = font.render(mon.name, True, text_color)
            screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 150 + i * 40))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(all_monsoons)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(all_monsoons)
                elif event.key == pygame.K_RETURN:
                    return all_monsoons[selected_index]
                    
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock = pygame.time.Clock()

    show_start_screen(screen)

    all_monsoons = [
        Monsoons("Thyladon", ["Normal"], {"hp": 150, "attack": 67, "defense": 40}, ["Ember", "Tackle"]),
        Monsoons("Baitfish", ["Water"], {"hp": 160, "attack": 54, "defense": 60}, ["Water Gun", "Tackle"]),
        Monsoons("Flydrake", ["Wind"], {"hp": 130, "attack": 60, "defense": 40}, ["Gust", "Tackle"]),
    ]

    player = show_select_screen(screen, all_monsoons)

    opponent = random.choice([m for m in all_monsoons if m != player])

    running = True
    while running:
        screen.fill(BG_COLOR)
        screen.blit(player.back_sprite, (100, 300))
        screen.blit(opponent.front_sprite, (500, 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

if __name__ == "__main__":
    main()