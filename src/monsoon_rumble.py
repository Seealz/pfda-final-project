import pygame
import random
import os

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
FPS = 60
BG_COLOR = (245, 245, 245)
WHITE = (255, 255, 255)
SPRITE_SCALE_FACTOR = 3
MOVE_PANEL_COLOR = (220, 220, 220)
TEXT_BOX_COLOR = (240, 240, 240)

# Global dictionaries for sounds
sounds = {}
cries = {}

# Helper functions
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
    # Draw health fill
    health_width = max(0, int(width * health_ratio))
    health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 255, 0) if health_ratio > 0.2 else (255, 0, 0)
    pygame.draw.rect(screen, health_color, (x, y, health_width, height))
    # Draw text
    font = pygame.font.SysFont(None, 18)
    health_text = f"{int(monster.display_hp)}/{int(monster.max_hp)}"
    text_surface = font.render(health_text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
    screen.blit(text_surface, text_rect)

def animate_hp(monster, target_hp):
    steps = 20
    current_hp = int(monster.display_hp)
    target_hp = int(target_hp)
    delta = (current_hp - target_hp) / steps
    for _ in range(steps):
        current_hp = max(target_hp, current_hp - delta)
        monster.display_hp = current_hp
        yield

def load_move_sounds():
    folder = "assets/sounds"
    if not os.path.exists(folder):
        print("Warning: sounds folder not found.")
        return
    for fname in os.listdir(folder):
        if fname.endswith(".wav"):
            name = os.path.splitext(fname)[0].replace("_", " ").title()
            try:
                sounds[name] = pygame.mixer.Sound(os.path.join(folder, fname))
            except:
                print(f"Failed to load sound: {fname}")
    for s in sounds.values():
        s.set_volume(0.3)

def load_cries():
    folder = "assets/cries"
    if not os.path.exists(folder):
        return
    for fname in os.listdir(folder):
        if fname.endswith(".wav"):
            name = os.path.splitext(fname)[0].capitalize()
            try:
                cry = pygame.mixer.Sound(os.path.join(folder, fname))
                cry.set_volume(0.18)
                cries[name] = cry
            except:
                print(f"Failed to load cry: {fname}")

# Load sounds and cries
load_move_sounds()
load_cries()

# Types and effectiveness
TYPES = ["Fire", "Water", "Plant", "Normal", "Wind", "Electric", "Psychic", "Earth"]
TYPE_EFFECTIVENESS = {t: {op: 1.0 for op in TYPES} for t in TYPES}
TYPE_EFFECTIVENESS["Fire"].update({"Plant": 2.0, "Normal": 2.0, "Earth": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Water"].update({"Fire": 2.0, "Earth": 2.0, "Plant": 0.5, "Electric": 0.5})
TYPE_EFFECTIVENESS["Plant"].update({"Water": 2.0, "Earth": 2.0, "Fire": 0.5, "Wind": 0.5})
TYPE_EFFECTIVENESS["Wind"].update({"Fire": 2.0, "Plant": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Electric"].update({"Water": 2.0, "Wind": 2.0, "Earth": 0.5})
TYPE_EFFECTIVENESS["Psychic"].update({"Psychic": 0.5})
TYPE_EFFECTIVENESS["Earth"].update({"Fire": 2.0, "Electric": 2.0, "Water": 0.5, "Plant": 0.5})

# Type colors
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

# Classes
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
        # Load sprite
        try:
            self.sprite = pygame.image.load("assets/monsoon.png").convert_alpha()
        except:
            self.sprite = pygame.Surface((64, 64))
            self.sprite.fill((100, 100, 255))
        # Load front and back sprites
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
        # Load moves
        for move_name in move_names:
            original_move = MOVES[move_name]
            self.moves.append(Move(original_move.name, original_move.type, original_move.power, original_move.max_pp))

    def draw(self, screen):
        faded_sprite = self.sprite.copy()
        if hasattr(self, 'alpha'):
            faded_sprite.set_alpha(self.alpha)
        screen.blit(faded_sprite, (0, 0))

    def apply_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        if self.hp == 0:
            self.faint()

    def faint(self):
        pass

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

        if move.power >= 0:
            damage = max(1, int((move.power + self.attack_stat - target.defense) * multiplier * crit_multiplier))
        else:
            damage = 0

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
        elif move.power < 0:
            heal_amount = min(abs(move.power), self.max_hp - self.hp)
            self.hp += heal_amount
            log += f" {self.name} recovered for {heal_amount} HP."

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

        return log

def choose_best_move(opponent, player):
    best_move_idx = 0
    max_damage = 0
    for i, move in enumerate(opponent.moves):
        damage = calculate_damage(opponent, move, player)
        if damage > max_damage:
            max_damage = damage
            best_move_idx = i
    return best_move_idx

def calculate_damage(attacker, move, defender):
    multiplier = 1.0
    for t in defender.types:
        multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)
    damage = max(1, int((move.power + attacker.attack_stat - defender.defense) * multiplier))
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
        screen.blit(title_text, title_rect)
        mouse_pos = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (70, 130, 180), button_rect)
        else:
            pygame.draw.rect(screen, (100, 100, 200), button_rect)
        button_text = font_button.render("Start Battle", True, (255, 255, 255))
        btn_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, btn_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    waiting = False
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def animate_hp(monster, target_hp):
    steps = 20
    delta = (monster.display_hp - target_hp) / steps
    for _ in range(steps):
        monster.display_hp = max(target_hp, monster.display_hp - delta)
        yield

def play_battle_animation(screen, attacker, defender, battle_log, move_buttons):
    for _ in range(5):
        defender.offset = [random.randint(-5, 5), random.randint(-5, 5)]
        draw_battle_ui(screen, attacker, defender, battle_log, move_buttons)
        pygame.display.flip()
        pygame.time.wait(50)
    defender.offset = [0, 0]

def draw_battle_ui(screen, player, opponent, battle_log, move_buttons):
    screen.fill(BG_COLOR)

    # Opponents sprite
    screen.blit(opponent.front_sprite, (500 + opponent.offset[0], 80 + opponent.offset[1]))
    draw_health_bar(screen, opponent, 500, 60)

    # Players sprite
    screen.blit(player.back_sprite, (100 + player.offset[0], 250 + player.offset[1]))
    draw_health_bar(screen, player, 100, 230)

    # Draw text box
    pygame.draw.rect(screen, TEXT_BOX_COLOR, (50, 460, 700, 60)) 
    font = pygame.font.SysFont(None, 24)
    if battle_log:
        lines = battle_log[-2:]  
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (60, 465 + i * 20))  

    # Draw move panel
    pygame.draw.rect(screen, MOVE_PANEL_COLOR, (50, 520, 700, 140)) 
    font = pygame.font.SysFont(None, 28)
    for rect, idx in move_buttons:
        move = player.moves[idx]
        color = TYPE_COLORS.get(move.type, (200, 200, 200)) if player.hp > 0 else (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        move_text = f"{move.name} ({move.pp}/{move.max_pp})"
        text = font.render(move_text, True, (0, 0, 0))
        screen.blit(text, (rect.x + 10, rect.y + 5))

wins = 0
losses = 0

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



def show_restart_button(screen, result_text):
    font_button = pygame.font.SysFont("arial", 36)
    restart_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100, 300, 60)
    restart_button_text = font_button.render("Restart", True, (255, 255, 255))

    while True:
        screen.fill((30, 30, 30))
        # Display result
        font_result = pygame.font.SysFont(None, 48)
        result_surface = font_result.render(result_text, True, (255, 0, 0))
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(result_surface, result_rect)

        # Draw the Restart button
        mouse_pos = pygame.mouse.get_pos()
        if restart_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (70, 130, 180), restart_button_rect)
        else:
            pygame.draw.rect(screen, (100, 100, 200), restart_button_rect)
        btn_rect = restart_button_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_button_text, btn_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    return True 

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)



def show_monsoon_selection_screen(screen, all_monsoons):
    font = pygame.font.SysFont("arial", 36, bold=True)
    button_width = 150
    button_height = 150 
    buttons = []
    button_rects = []

    for i, monsoon in enumerate(all_monsoons):
        # Scale the sprite for the button
        sprite = monsoon.front_sprite
        sprite = pygame.transform.scale(sprite, (button_width, button_height))

        # Create clickable area based on the sprite's position
        button_rect = pygame.Rect(150 + (i % 3) * (button_width + 50), 100 + (i // 3) * (button_height + 50), button_width, button_height)
        buttons.append(sprite)
        button_rects.append(button_rect)

    selected_monsoon = None
    waiting = True
    while waiting:
        screen.fill((30, 30, 30))

        # Draw each sprite as a button
        for i, button_rect in enumerate(button_rects):
            screen.blit(buttons[i], button_rect.topleft) 

        # Display instructions
        instructions_text = font.render("Click a sprite to select your Monsoon!", True, (255, 255, 255))
        instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        screen.blit(instructions_text, instructions_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button_rect in enumerate(button_rects):
                    if button_rect.collidepoint(mouse_pos):
                        selected_monsoon = all_monsoons[i]
                        waiting = False 

        pygame.display.flip()
        pygame.time.Clock().tick(FPS)

    return selected_monsoon 


def main():

    global wins, losses

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Monsoon Rumble")
    clock = pygame.time.Clock()

    all_monsoons = [

        Monsoons("Voltail", ["Electric"], {"hp": 80, "attack": 130, "defense": 40, "speed": 200}, ["Shock", "Tackle", "Recover"]),
        Monsoons("Burnrat", ["Fire"], {"hp": 150, "attack": 75, "defense": 75, "speed": 100}, ["Ember", "Tackle", "Recover"]),
        Monsoons("Thyladon", ["Plant"], {"hp": 120, "attack": 120, "defense": 80, "speed": 95}, ["Vine Whip", "Tackle", "Recover"]),
        Monsoons("Pseye", ["Psychic"], {"hp": 90, "attack": 115, "defense": 40, "speed": 150}, ["Confuse Ray", "Tackle", "Heal Pulse"]),
        Monsoons("Flydo", ["Wind"], {"hp": 130, "attack": 60, "defense": 95, "speed": 155}, ["Gust", "Tackle", "Recover"]),
        Monsoons("Drillizard", ["Earth"], {"hp": 150, "attack": 130, "defense": 100, "speed": 45}, ["Quake", "Tackle", "Heal Pulse"]),
        Monsoons("Clawdon", ["Normal"], {"hp": 170, "attack": 90, "defense": 80, "speed": 120}, ["Tackle", "Ember", "Recover"]),
        Monsoons("Baitinphish", ["Water"], {"hp": 350, "attack": 50, "defense": 150, "speed": 30}, ["Water Gun", "Tackle", "Recover"]),
        Monsoons("Cataboo", ["Psychic"], {"hp": 120, "attack": 140, "defense": 50, "speed": 110}, ["Confuse Ray", "Gust", "Heal Pulse"]),
    ]

    selected_monsoon = show_monsoon_selection_screen(screen, all_monsoons)
    if selected_monsoon:
        print(f"Selected Monsoon: {selected_monsoon.name}")
    else:
        print("No Monsoon selected.")
        return
   
    # Show main menu
    show_main_menu(screen)

    # Main game loop
    while True:
        player = selected_monsoon 
        opponent = random.choice([m for m in all_monsoons if m != player])

        for mon in [player, opponent]:
            mon.hp = mon.max_hp
            mon.display_hp = mon.max_hp
            mon.offset = [0, 0]
            for move in mon.moves:
                move.pp = move.max_pp

        battle_log = ["Battle Start!"]
        player.play_cry()
        pygame.time.wait(1000)
        opponent.play_cry()
        pygame.time.wait(1000)

        # Battle loop
        while player.hp > 0 and opponent.hp > 0:
            move_buttons = []
            for i, move in enumerate(player.moves):
                x = 70 + (i % 2) * 350
                y = 550 + (i // 2) * 60
                move_buttons.append((pygame.Rect(x, y, 300, 30), i))
            selected_move = None

            # Waits for player move
            while selected_move is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for rect, idx in move_buttons:
                            if rect.collidepoint(event.pos) and player.moves[idx].pp > 0:
                                selected_move = idx

                draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
                pygame.display.flip()
                clock.tick(FPS)

            # Player attack
            log, sound_name, cry_name, faint_sound = player.attack(selected_move, opponent)
            battle_log.append(log)
            # Play sound
            if sound_name:
                sounds[sound_name].play()
            # Animates attack
            play_battle_animation(screen, player, opponent, battle_log, move_buttons)

            # Animates HP bar
            if opponent.hp < opponent.display_hp:
                for _ in animate_hp(opponent, opponent.hp):
                    draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
                    pygame.display.flip()
                    pygame.time.wait(30)

            # Check if opponent fainted
            if opponent.hp <= 0:
                break

            # Opponent move
            opp_move_idx = choose_best_move(opponent, player)
            log, sound_name, cry_name, faint_sound = opponent.attack(opp_move_idx, player)
            battle_log.append(log)
            if sound_name:
                sounds[sound_name].play()
            play_battle_animation(screen, opponent, player, battle_log, [])

            # Animates HP bar
            if player.hp < player.display_hp:
                for _ in animate_hp(player, player.hp):
                    draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
                    pygame.display.flip()
                    pygame.time.wait(30)

            if player.hp <= 0:
                break

        # Show result
        for mon in [player, opponent]:
            mon.display_hp = mon.hp
        draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
        pygame.display.flip()

        # Determines the result
        if player.hp > 0:
            result_text = "You Win!"
            wins += 1
        else:
            result_text = "You Lose!"
            losses += 1

        # Shows result and restart option
        if show_restart_button(screen, result_text):
            continue
        else:
            break

    pygame.quit()



if __name__ == "__main__":
    main()