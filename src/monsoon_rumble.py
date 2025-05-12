import pygame
import random
import os

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (245, 245, 245)
WHITE = (255, 255, 255)
SPRITE_SCALE_FACTOR = 3
MOVE_PANEL_COLOR = (220, 220, 220)
TEXT_BOX_COLOR = (240, 240, 240)

sounds = {}
cries = {}

def wait(time_in_ms):
    pygame.time.wait(time_in_ms)

def draw_health_bar(screen, monster, x, y):
    width = 200
    height = 20
    border = 2
    health_ratio = monster.display_hp / monster.max_hp
    
    # Draw border
    pygame.draw.rect(screen, (0, 0, 0), (x - border, y - border, width + 2*border, height + 2*border))
    
    # Draw background
    pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height))
    
    # Draw health
    health_width = max(0, int(width * health_ratio))
    health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
    pygame.draw.rect(screen, health_color, (x, y, health_width, height))
    
    # Draw text
    font = pygame.font.SysFont(None, 18)
    health_text = f"{monster.display_hp}/{monster.max_hp}"
    text_surface = font.render(health_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surface, text_rect)

def draw_battle_ui(screen, player, opponent, battle_log, move_buttons):
    screen.fill(BG_COLOR)

    # Opponent sprite
    screen.blit(opponent.front_sprite, (500 + opponent.offset[0], 80 + opponent.offset[1]))
    draw_health_bar(screen, opponent, 500, 60)

    # Player sprite
    screen.blit(player.back_sprite, (100 + player.offset[0], 250 + player.offset[1]))
    draw_health_bar(screen, player, 100, 230)

    # Draw text box
    pygame.draw.rect(screen, TEXT_BOX_COLOR, (50, 350, 700, 60))
    font = pygame.font.SysFont(None, 24)
    if battle_log:
        lines = battle_log[-2:]
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (60, 355 + i * 20))

    # Draw move panel
    pygame.draw.rect(screen, MOVE_PANEL_COLOR, (50, 410, 700, 140))
    font = pygame.font.SysFont(None, 28)
    for rect, idx in move_buttons:
        move = player.moves[idx]
        if player.hp > 0:
            color = TYPE_COLORS.get(move.type, (200, 200, 200))
        else:
            color = (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        move_text = f"{move.name} ({move.pp}/{move.max_pp})"
        text = font.render(move_text, True, (0, 0, 0))
        screen.blit(text, (rect.x + 10, rect.y + 5))

# Win/Loss
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

# Type color mapping
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

def load_move_sounds():
    move_sound_folder = "assets/sounds"
    if not os.path.exists(move_sound_folder):
        print("Warning: sounds folder not found.")
        return

    for fname in os.listdir(move_sound_folder):
        if fname.endswith(".wav"):
            move_name = os.path.splitext(fname)[0].replace("_", " ").title()
            try:
                sounds[move_name] = pygame.mixer.Sound(os.path.join(move_sound_folder, fname))
            except Exception as e:
                print(f"Failed to load sound {fname}: {e}")
    for sound in sounds.values():
        sound.set_volume(0.3)

load_move_sounds()

# Load cries
cry_folder = "assets/cries"
if os.path.exists(cry_folder):
    for fname in os.listdir(cry_folder):
        if fname.endswith(".wav"):
            name = os.path.splitext(fname)[0].capitalize()
            try:
                cry = pygame.mixer.Sound(os.path.join(cry_folder, fname))
                cry.set_volume(0.18)
                cries[name] = cry
            except Exception as e:
                print(f"Failed to load cry {fname}: {e}")

# Define classes
class Move:
    def __init__(self, name, type, power, pp):
        self.name = name
        self.type = type
        self.power = power
        self.max_pp = pp
        self.pp = pp

class Monsoons:
    def __init__(self, name, types, stats, move_names):
        self.name = name
        self.types = types
        self.max_hp = stats["hp"]
        self.hp = stats["hp"]
        self.display_hp = self.hp
        self.attack_stat = stats["attack"]
        self.defense = stats["defense"]
        self.speed = stats.get("speed", 50)
        self.statuses = []
        self.moves = []
        self.offset = [0, 0]

        for move_name in move_names:
            original_move = MOVES[move_name]
            self.moves.append(Move(original_move.name, original_move.type, original_move.power, original_move.max_pp))

        try:
            front = pygame.image.load(f"assets/sprites/{name.lower()}_front.png").convert_alpha()
            back = pygame.image.load(f"assets/sprites/{name.lower()}_back.png").convert_alpha()
        except:
            front = pygame.Surface((50, 50))
            front.fill((255, 0, 0))
            back = pygame.Surface((50, 50))
            back.fill((0, 0, 255))

        self.front_sprite = pygame.transform.scale(front, (front.get_width() * SPRITE_SCALE_FACTOR, front.get_height() * SPRITE_SCALE_FACTOR))
        self.back_sprite = pygame.transform.scale(back, (back.get_width() * SPRITE_SCALE_FACTOR, back.get_height() * SPRITE_SCALE_FACTOR))

    def play_cry(self):
        if self.name in cries:
            cries[self.name].play()

    def attack(self, move_index, target):
        move = self.moves[move_index]
        if move.pp <= 0:
            return f"{self.name} tried to use {move.name} but it's out of PP!", None, None, None

        if "Paralyzed" in self.statuses and random.random() < 0.25:
            return f"{self.name} is paralyzed and couldn't move!", None, None, None
        
        if "Confused" in self.statuses and random.random() < 0.5:
            self.hp = max(0, self.hp - 10)
            return f"{self.name} is confused and hurt itself!", None, None, None

        move.pp -= 1
        multiplier = 1.0
        for t in target.types:
            multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)

        is_critical = random.random() < 0.1
        crit_multiplier = 1.5 if is_critical else 1.0

        damage = max(1, int((move.power + self.attack_stat - target.defense) * multiplier * crit_multiplier))

        sound_to_play = move.name if move.name in sounds else None
        cry_to_play = self.name if self.name in cries else None
        faint_sound = "faint" if target.hp - damage <= 0 and "faint" in sounds else None

        log = self.use_move(move, target, damage, is_critical, multiplier, sounds)

        return log, sound_to_play, cry_to_play, faint_sound

    def use_move(self, move, target, damage, is_critical, multiplier, sounds):
        log = f"{self.name} used {move.name}!"

        if move.power > 0:
            target.hp = max(0, target.hp - damage)
            log += f" It dealt {damage} damage."
            if is_critical:
                log += " A critical hit!"
            if multiplier > 1:
                log += " It's super effective!"
            elif multiplier < 1:
                log += " It's not very effective."

        if move.name == "Confuse Ray" and "Confused" not in target.statuses:
            target.statuses.append("Confused")
            log += f" {target.name} became confused!"
        elif move.name == "Thunder Wave" and "Paralyzed" not in target.statuses:
            target.statuses.append("Paralyzed")
            log += f" {target.name} is paralyzed!"

        if target.hp <= 0:
            if "faint" in sounds:
                sounds["faint"].play()
            log += f" {target.name} fainted!"

        if move.power < 0:
            heal = min(-move.power, self.max_hp - self.hp)
            self.hp += heal
            log += f" {self.name} recovered {heal} HP."

        if move.name == "Heal Pulse":
            self.statuses.clear()
            log += f" {self.name} is no longer affected by any status!"

        return log

def choose_best_move(opponent, player):
    # Implement basic logic to choose a move
    best_move_index = 0
    best_damage = 0
    for i, move in enumerate(opponent.moves):
        damage = calculate_damage(opponent, move, player)
        if damage > best_damage:
            best_damage = damage
            best_move_index = i
    return best_move_index

def calculate_damage(attacker, move, defender):
    multiplier = 1.0
    for t in defender.types:
        multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)
    damage = max(1, (move.power + attacker.attack_stat - defender.defense) * multiplier)
    return damage

def show_main_menu(screen):
    font_title = pygame.font.SysFont("arial", 64, bold=True)
    font_button = pygame.font.SysFont("arial", 36)
    
    title_text = font_title.render("Monsoon Rumble", True, (50, 50, 150))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
    
    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 60)
    
    waiting = True
    while waiting:
        screen.fill((30, 30, 30)) 

        # Draw title
        screen.blit(title_text, title_rect)

        # Draw button (hover effect)
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (70, 130, 180), button_rect) 
        else:
            pygame.draw.rect(screen, (100, 100, 200), button_rect)

        # Draw button text
        button_text = font_button.render("Start Battle", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False

        pygame.display.flip()
        pygame.time.Clock().tick(60)

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
        "Quake": Move("Quake", "Earth", 50, 20),
        "Thunder Wave": Move("Thunder Wave", "Electric", 0, 25),
        "Recover": Move("Recover", "Normal", -40, 5),
        "Heal Pulse": Move("Heal Pulse", "Psychic", -30, 5),
    }

    all_monsoons = [
        Monsoons("Voltail", ["Electric"], {"hp": 160, "attack": 30, "defense": 35, "speed": 200}, ["Shock", "Tackle", "Recover"]),
        Monsoons("Burnrat", ["Fire"], {"hp": 158, "attack": 25, "defense": 25, "speed": 120}, ["Ember", "Tackle", "Recover"]),
        Monsoons("Thyladon", ["Plant"], {"hp": 110, "attack": 45, "defense": 40, "speed": 156}, ["Vine Whip", "Tackle", "Recover"]),
        Monsoons("Pseye", ["Psychic"], {"hp": 144, "attack": 45, "defense": 30, "speed": 94}, ["Confuse Ray", "Tackle", "Heal Pulse"]),
        Monsoons("Flydo", ["Wind"], {"hp": 166, "attack": 30, "defense": 25, "speed": 177}, ["Gust", "Tackle", "Recover"]),
        Monsoons("Drillizard", ["Earth"], {"hp": 123, "attack": 50, "defense": 65, "speed": 133}, ["Quake", "Tackle", "Heal Pulse"]),
        Monsoons("Clawdon", ["Normal"], {"hp": 235, "attack": 45, "defense": 40, "speed": 150}, ["Tackle", "Ember", "Recover"]),
        Monsoons("Baitinphish", ["Water"], {"hp": 365, "attack": 22, "defense": 55, "speed": 50}, ["Water Gun", "Tackle", "Recover"]),
        Monsoons("Cataboo", ["Psychic"], {"hp": 200, "attack": 38, "defense": 32, "speed": 100}, ["Confuse Ray", "Gust", "Heal Pulse"]),
    ]

    # Show main menu and wait for start
    show_main_menu(screen)

    running = True
    while running:
        player = random.choice(all_monsoons)
        opponent = random.choice([m for m in all_monsoons if m != player])
    
        for m in [player, opponent]:
            m.hp = m.max_hp
            m.display_hp = m.max_hp
            m.offset = [0, 0]
            for move in m.moves:
                move.pp = move.max_pp

        battle_log = ["Battle Start!"]

        while player.hp > 0 and opponent.hp > 0:
            move_buttons = []
            for i, move in enumerate(player.moves):
                x = 70 + (i % 2) * 350
                y = 420 + (i // 2) * 40
                move_buttons.append((pygame.Rect(x, y, 300, 30), i))

            selected_move = None
            while selected_move is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for rect, idx in move_buttons:
                            if rect.collidepoint(event.pos) and player.moves[idx].pp > 0:
                                selected_move = idx

                draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
                pygame.display.flip()
                clock.tick(FPS)

            # Player's attack
            log, sound_name, cry_name, faint_sound = player.attack(selected_move, opponent)
            battle_log.append(log)
            if cry_name:
                cries[cry_name].play()
            if sound_name:
                sounds[sound_name].play()
            if faint_sound:
                sounds[faint_sound].play()

            draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
            pygame.display.flip()
            pygame.time.wait(1000)

            # Check if opponent fainted
            if opponent.hp <= 0:
                break

            # Opponent's turn
            opponent_move = choose_best_move(opponent, player)
            log, sound_name, cry_name, faint_sound = opponent.attack(opponent_move, player)
            battle_log.append(log)
            if cry_name:
                cries[cry_name].play()
            if sound_name:
                sounds[sound_name].play()
            if faint_sound:
                sounds[faint_sound].play()

            draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
            pygame.display.flip()
            pygame.time.wait(1000)

        # Update HP bars after battle
        for mon in (player, opponent):
            if mon.hp <= 0:
                mon.display_hp = 0
            elif mon.display_hp > mon.hp:
                mon.display_hp -= max(1, (mon.display_hp - mon.hp) // 4)
            elif mon.display_hp < mon.hp:
                mon.display_hp += max(1, (mon.hp - mon.display_hp) // 4)

        draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
        pygame.display.flip()
        pygame.time.wait(2500)

        # Display win/loss message
        font = pygame.font.SysFont(None, 48)
        result_text = "You Win!" if player.hp > 0 else "You Lose!"
        result_surface = font.render(result_text, True, (255, 0, 0))
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(result_surface, result_rect)
        pygame.display.flip()
        pygame.time.wait(3000)

        # Wait for player to press Enter or Escape to proceed
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        waiting = False

if __name__ == "__main__":
    main()