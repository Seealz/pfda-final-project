import pygame
import random
import os

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BG_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

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
TYPE_EFFECTIVENESS["Normal"].update({"Fire": 1.0, "Water": 1.0, "Plant": 1.0, "Wind": 1.0, "Electric": 1.0, "Psychic": 1.0, "Earth": 1.0})

class Move:
    def __init__(self, name, move_type, power, pp, sound=None, effect_image=None, is_physical=False):
        self.name = name
        self.type = move_type
        self.power = power
        self.pp = pp
        self.effect_image = effect_image
        self.is_physical = is_physical
        self.sound = None

class Monsoons:
    def __init__(self, name, types, stats, move_names):
        self.name = name
        self.types = types
        self.stats = stats
        self.max_hp = stats["hp"]
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

    def attack(self, move_index, opponent, screen):
        move = self.moves[move_index]
        if move.pp <= 0:
            return False, f"{move.name} has no PP left!"
        move.pp -= 1
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

def draw_hp_bar(screen, x, y, current_hp, max_hp):
    pygame.draw.rect(screen, RED, (x, y, 200, 20))
    green_width = int((current_hp / max_hp) * 200)
    pygame.draw.rect(screen, GREEN, (x, y, green_width, 20))

def draw_text_box(screen, text):
    font = pygame.font.Font(None, 28)
    box = pygame.Rect(50, 500, 700, 80)
    pygame.draw.rect(screen, (50, 50, 50), box)
    pygame.draw.rect(screen, WHITE, box, 2)
    rendered_text = font.render(text, True, WHITE)
    screen.blit(rendered_text, (box.x + 10, box.y + 30))

def show_start_screen(screen):
    font = pygame.font.Font(None, 60)
    title = font.render("Monsoon Rumble", True, WHITE)
    prompt = pygame.font.Font(None, 36).render("Click to Start", True, (200, 200, 200))
    while True:
        screen.fill(BG_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
        screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 300))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

def show_select_screen(screen, all_monsoons):
    font = pygame.font.Font(None, 36)
    selected = 0
    button_rects = []
    while True:
        screen.fill((30, 30, 30))
        title = pygame.font.Font(None, 48).render("Choose Your Monsoon", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        button_rects.clear()
        for i, mon in enumerate(all_monsoons):
            label = font.render(mon.name, True, WHITE)
            rect = label.get_rect(center=(SCREEN_WIDTH // 2, 150 + i * 60))
            screen.blit(label, rect.topleft)
            button_rects.append((rect, mon))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, mon in button_rects:
                    if rect.collidepoint(event.pos):
                        return mon

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock = pygame.time.Clock()

    global MOVES
    MOVES = {
          "Tackle": Move("Tackle", "Normal", 40, 35),
        "Ember": Move("Ember", "Fire", 50, 25),
        "Water Gun": Move("Water Gun", "Water", 40, 25),
        "Gust": Move("Gust", "Wind", 40, 25),
        "Vine Whip": Move("Vine Whip", "Plant", 45, 25),
        "Confuse Ray": Move("Confuse Ray", "Psychic", 40, 20),
        "Shock": Move("Shock", "Electric", 45, 25),
        "Quake": Move("Quake", "Earth", 50, 20)
    }

    all_monsoons = [
        Monsoons("Voltail", ["Electric"], {"hp": 100, "attack": 40, "defense": 35}, ["Shock", "Tackle"]),
        Monsoons("Burnrat", ["Fire"], {"hp": 90, "attack": 50, "defense": 25}, ["Ember", "Tackle"]),
        Monsoons("Thyladon", ["Plant"], {"hp": 110, "attack": 35, "defense": 40}, ["Vine Whip", "Tackle"]),
        Monsoons("Pseye", ["Psychic"], {"hp": 95, "attack": 45, "defense": 30}, ["Confuse Ray", "Tackle"]),
        Monsoons("Flydo", ["Wind"], {"hp": 85, "attack": 40, "defense": 25}, ["Gust", "Tackle"]),
        Monsoons("Drillizard", ["Earth"], {"hp": 120, "attack": 50, "defense": 45}, ["Quake", "Tackle"]),
        Monsoons("Clawdon", ["Normal"], {"hp": 100, "attack": 45, "defense": 30}, ["Tackle"]),
        Monsoons("Baitinphish", ["Water"], {"hp": 105, "attack": 42, "defense": 35}, ["Water Gun", "Tackle"]),
        Monsoons("Cataboo", ["Psychic"], {"hp": 95, "attack": 38, "defense": 32}, ["Confuse Ray", "Tackle"])
    ]

    show_start_screen(screen)
    player = show_select_screen(screen, all_monsoons)
    opponent = random.choice([m for m in all_monsoons if m != player])

    running = True
    battle_text = "Battle Start!"

    while running:
        screen.fill(BG_COLOR)
        screen.blit(player.back_sprite, (100, 300))
        screen.blit(opponent.front_sprite, (500, 100))

        draw_hp_bar(screen, 100, 270, player.stats["hp"], player.max_hp)
        draw_hp_bar(screen, 500, 70, opponent.stats["hp"], opponent.max_hp)
        draw_text_box(screen, battle_text)

        font = pygame.font.Font(None, 28)
        move_buttons = []
        for i, move in enumerate(player.moves):
            label = font.render(f"{move.name} (PP: {move.pp})", True, WHITE)
            rect = label.get_rect(topleft=(50, 400 + i * 30))
            screen.blit(label, rect)
            move_buttons.append((rect, i))

        pygame.display.flip()

        selected_move = None
        while selected_move is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, i in move_buttons:
                        if rect.collidepoint(event.pos):
                            selected_move = i

        success, msg = player.attack(selected_move, opponent, screen)
        battle_text = msg
        if opponent.stats["hp"] <= 0:
            battle_text += f" {opponent.name} fainted!"
            pygame.time.wait(1500)
            break

        opponent_move = random.choice([i for i in range(len(opponent.moves)) if opponent.moves[i].pp > 0])
        success, msg = opponent.attack(opponent_move, player, screen)
        battle_text = msg
        if player.stats["hp"] <= 0:
            battle_text += f" {player.name} fainted!"
            pygame.time.wait(1500)
            break

        clock.tick(FPS)

if __name__ == "__main__":
    main()
