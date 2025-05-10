import pygame
import random
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0, 0, 0)

# Typings
TYPES = ["Fire", "Water", "Plant", "Normal", "Wind", "Electric", "Psychic", "Earth"]
TYPE_EFFECTIVENESS = {t: {op: 1.0 for op in TYPES} for t in TYPES}

# Strengths and Weaknesses
TYPE_EFFECTIVENESS["Fire"].update({"Plant": 2.0, "Normal": 2.0, "Earth": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Water"].update({"Fire": 2.0, "Earth": 2.0, "Plant": 0.5, "Electric": 0.5})
TYPE_EFFECTIVENESS["Plant"].update({"Water": 2.0, "Earth": 2.0, "Fire": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Wind"].update({"Fire": 2.0, "Plant": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Electric"].update({"Water": 2.0, "Wind": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Psychic"].update({"Normal": 1.0, "Water": 1.0, "Psychic": 0.5})
TYPE_EFFECTIVENESS["Earth"].update({"Fire": 2.0, "Electric": 2.0, "Water": 0.5, "Plant": 0.5})
TYPE_EFFECTIVENESS["Normal"].update({
    "Fire": 1.0,  # Normal does neutral damage to Fire
    "Water": 1.0,  # Normal does neutral damage to Water
    "Plant": 1.0,  # Normal does neutral damage to Plant
    "Wind": 1.0,  # Normal does neutral damage to Wind
    "Electric": 1.0,  # Normal does neutral damage to Electric
    "Psychic": 1.0,  # Normal does neutral damage to Psychic
    "Earth": 1.0  # Normal does neutral damage to Earth
})

class Move:
    def __init__(self, name, move_type, power, pp, sound=None, effect_image=None, is_physical=False):
        self.name = name
        self.type = move_type
        self.power = power
        self.pp = pp
        self.effect_image = effect_image
        self.is_physical = is_physical

        if sound:
            sound_path = os.path.abspath(sound)
            try:
                self.sound = pygame.mixer.Sound(sound_path) if os.path.exists(sound_path) else None
            except pygame.error:
                self.sound = None
        else:
            self.sound = None

    def play_sound(self):
        if self.sound:
            self.sound.play()

class Monsoons:
    def __init__(self, name, types, stats, move_names):
        self.name = name
        self.types = types
        self.stats = stats
        self.moves = [MOVES[name] for name in move_names]
        self.load_sprites()

    def load_sprites(self):
        try:
            self.front_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_front.png").convert_alpha()
            self.back_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_back.png").convert_alpha()
        except:
            self._create_placeholder_sprites()

    def _create_placeholder_sprites(self):
        placeholder_sprite = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(placeholder_sprite, (255, 0, 255), (0, 0, 100, 100))
        self.front_sprite = self.back_sprite = placeholder_sprite
    def load_sprites(self):
        try:
            self.front_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_front.png").convert_alpha()
            self.back_sprite = pygame.image.load(f"assets/sprites/{self.name.lower()}_back.png").convert_alpha()
        except:
            self._create_placeholder_sprites()

def _create_placeholder_sprites(self):
        placeholder_sprite = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(placeholder_sprite, (255, 0, 255), (0, 0, 100, 100))
        self.front_sprite = self.back_sprite = placeholder_sprite

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
        player_start_x, player_start_y = 100, 300
        opponent_start_x, opponent_start_y = 500, 100
        duration, steps = 1000, 10
        dx = (opponent_start_x - player_start_x) / steps
        dy = (opponent_start_y - player_start_y) / steps

        for step in range(steps):
            screen.fill(BG_COLOR)
            screen.blit(self.front_sprite, (player_start_x + dx * step, player_start_y + dy * step))
            screen.blit(opponent.front_sprite, (opponent_start_x - dx * step, opponent_start_y - dy * step))
            if move.effect_image:
                effect_img = pygame.image.load(move.effect_image)
                screen.blit(effect_img, (player_start_x + dx * step, player_start_y + dy * step))
            pygame.display.flip()
            pygame.time.delay(100)

        pygame.time.delay(500)

def show_start_screen(screen):
    font = pygame.font.Font(None, 60)
    title = font.render("Monsoon Rumble", True, (255, 255, 255))
    prompt = pygame.font.Font(None, 36).render("Press SPACE to Start", True, (200, 200, 200))
    while True:
        screen.fill(BG_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 300))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return

def show_select_screen(screen, all_monsoons):
    font = pygame.font.Font(None, 36)
    selected = 0
    while True:
        screen.fill((30, 30, 30))
        title = pygame.font.Font(None, 48).render("Choose Your Monsoon", True, (255, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        for i, mon in enumerate(all_monsoons):
            color = (255, 255, 0) if i == selected else (255, 255, 255)
            label = font.render(mon.name, True, color)
            screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2, 150 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(all_monsoons)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(all_monsoons)
                elif event.key == pygame.K_RETURN:
                    return all_monsoons[selected]

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock = pygame.time.Clock()
    try:
        pygame.mixer.init()
    except:
        print("Warning: Sound mixer couldn't be initialized.")

    global MOVES
    MOVES = {
        "Tackle": Move("Tackle", "Normal", 40, 35, "assets/sounds/tackle.wav", is_physical=True),
        "Ember": Move("Ember", "Fire", 50, 25, "assets/sounds/ember.wav", "assets/effects/ember.png"),
        "Water Gun": Move("Water Gun", "Water", 40, 25, "assets/sounds/water_gun.wav", "assets/effects/watergun.png"),
        "Gust": Move("Gust", "Wind", 40, 25, "assets/sounds/gust.wav", "assets/effects/gust.png")
    }

    all_monsoons = [
        Monsoons("Voltail", ["Electric"], {"hp": 100, "attack": 40, "defense": 30}, ["Water Gun", "Tackle"]),
        Monsoons("Flydo", ["Wind"], {"hp": 100, "attack": 40, "defense": 30}, ["Water Gun", "Tackle"]),
        Monsoons("Burnrat", ["Fire"], {"hp": 100, "attack": 40, "defense": 30}, ["Ember", "Tackle"])
    ]

    show_start_screen(screen)
    player = show_select_screen(screen, all_monsoons)
    opponent = random.choice([m for m in all_monsoons if m != player])

    running = True
    while running:
        screen.fill(BG_COLOR)
        screen.blit(player.back_sprite, (100, 300))
        screen.blit(opponent.front_sprite, (500, 100))

        font = pygame.font.Font(None, 36)
        screen.blit(font.render(f"{player.name} HP: {player.stats['hp']}", True, (255, 255, 255)), (100, 450))
        screen.blit(font.render(f"{opponent.name} HP: {opponent.stats['hp']}", True, (255, 255, 255)), (500, 50))

        pygame.display.flip()

        move_choice = None
        while move_choice is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        move_choice = 0
                    elif event.key == pygame.K_2:
                        move_choice = 1

        success, msg = player.attack(move_choice, opponent, screen)
        print(msg)
        if opponent.stats["hp"] <= 0:
            print(f"{opponent.name} fainted!")
            break

        if opponent.stats["hp"] > 0:
            opponent_move = random.choice([0, 1])
            success, msg = opponent.attack(opponent_move, player, screen)
            print(msg)
            if player.stats["hp"] <= 0:
                print(f"{player.name} fainted!")
                break

        clock.tick(FPS)

if __name__ == "__main__":
    main()