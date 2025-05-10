import pygame
import random

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (245, 245, 245)
WHITE = (255, 255, 255)
SPRITE_SCALE_FACTOR = 3
PLAYER_SPRITE_POS = (100, 250)
OPPONENT_SPRITE_POS = (500, 50)
MOVE_PANEL_COLOR = (220, 220, 220)
TEXT_BOX_COLOR = (240, 240, 240)

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
TYPE_EFFECTIVENESS["Normal"].update({t: 1.0 for t in TYPES})

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
        self.display_hp = self.hp  # HP bar animation
        self.attack_stat = stats["attack"]
        self.defense = stats["defense"]
        self.speed = stats.get("speed", 50)
        self.status = None
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

    def attack(self, move_index, target):
        move = self.moves[move_index]
        if move.pp <= 0:
            return f"{self.name} tried to use {move.name} but it's out of PP!"

        if self.status == "Paralyzed" and random.random() < 0.25:
            return f"{self.name} is paralyzed and couldn't move!"

        if self.status == "Confused" and random.random() < 0.5:
            self.hp = max(0, self.hp - 10)
            return f"{self.name} is confused and hurt itself!"

        move.pp -= 1

        # Type effectiveness multiplier
        multiplier = 1.0
        for t in target.types:
            multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)

        # Critical hit check (10% chance)
        is_critical = random.random() < 0.1
        crit_multiplier = 1.5 if is_critical else 1.0

        # Final damage calculation
        damage = max(1, int((move.power + self.attack_stat - target.defense) * multiplier * crit_multiplier))
        target.hp = max(0, target.hp - damage)

        # Construct log
        log = f"{self.name} used {move.name}! It dealt {damage} damage."
        if is_critical:
            log += " A critical hit!"
        if multiplier > 1:
            log += " It's super effective!"
        elif multiplier < 1:
            log += " It's not very effective."

        # Apply status if applicable
        if move.name == "Confuse Ray":
            target.status = "Confused"
            log += f" {target.name} became confused!"
        elif move.name == "Thunder Wave":
            target.status = "Paralyzed"
            log += f" {target.name} is paralyzed!"

        if target.hp <= 0:
            log += f" {target.name} fainted!"

        return log

def draw_hp_bar(screen, x, y, display_hp, max_hp):
    ratio = display_hp / max_hp
    pygame.draw.rect(screen, (0, 0, 0), (x, y, 100, 10), 1)
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(100 * ratio), 10))

def draw_battle_ui(screen, player, opponent, log, move_buttons):
    screen_width, screen_height = screen.get_size()
    screen.fill(WHITE)

    player_x = screen_width // 4 - player.back_sprite.get_width() // 2 + player.offset[0]
    player_y = screen_height // 2 + 100 + player.offset[1]
    opponent_x = 3 * screen_width // 4 - opponent.front_sprite.get_width() // 2 + opponent.offset[0]
    opponent_y = screen_height // 4 - 100 + opponent.offset[1]

    screen.blit(player.back_sprite, (player_x, player_y))
    screen.blit(opponent.front_sprite, (opponent_x, opponent_y))


    draw_hp_bar(screen, player_x, player_y - 30, player.display_hp, player.max_hp)
    draw_hp_bar(screen, opponent_x, opponent_y - 30, opponent.display_hp, opponent.max_hp)


    pygame.draw.rect(screen, MOVE_PANEL_COLOR, (50, screen_height - 200, screen_width - 100, 150))
    pygame.draw.rect(screen, (0, 0, 0), (50, screen_height - 200, screen_width - 100, 150), 2)

    font = pygame.font.Font(None, 28)
    for i, (rect, move_idx) in enumerate(move_buttons):
        move = player.moves[move_idx]
        text_color = (0, 0, 0) if move.pp > 0 else (150, 150, 150)
        label = font.render(f"{move.name} (PP: {move.pp})", True, text_color)
        screen.blit(label, rect)

    pygame.draw.rect(screen, TEXT_BOX_COLOR, (50, screen_height - 150, screen_width - 100, 130))
    pygame.draw.rect(screen, (0, 0, 0), (50, screen_height - 150, screen_width - 100, 130), 2)
    font = pygame.font.Font(None, 24)
    for i, line in enumerate(log[-5:]):
        text_surface = font.render(line, True, (0, 0, 0))
        screen.blit(text_surface, (60, screen_height - 140 + i * 24))

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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
        "Confuse Ray": Move("Confuse Ray", "Psychic", 3, 25),
        "Thunder Wave": ("Thunder Wave", "Electric", 1, 25)
    }

    all_monsoons = [
        Monsoons("Voltail", ["Electric"], {"hp": 160, "attack": 30, "defense": 35, "speed": 200}, ["Shock", "Tackle"]),
        Monsoons("Burnrat", ["Fire"], {"hp": 158, "attack": 25, "defense": 25, "speed": 120}, ["Ember", "Tackle"]),
        Monsoons("Thyladon", ["Plant"], {"hp": 110, "attack": 45, "defense": 40, "speed": 156}, ["Vine Whip", "Tackle"]),
        Monsoons("Pseye", ["Psychic"], {"hp": 144, "attack": 45, "defense": 30, "speed": 94}, ["Confuse Ray", "Tackle"]),
        Monsoons("Flydo", ["Wind"], {"hp": 166, "attack": 30, "defense": 25, "speed": 177}, ["Gust", "Tackle"]),
        Monsoons("Drillizard", ["Earth"], {"hp": 123, "attack": 50, "defense": 65, "speed": 133}, ["Quake", "Tackle"]),
        Monsoons("Clawdon", ["Normal"], {"hp": 235, "attack": 45, "defense": 40, "speed": 150}, ["Tackle", "Ember"]),
        Monsoons("Baitinphish", ["Water"], {"hp": 365, "attack": 22, "defense": 55, "speed": 50}, ["Water Gun", "Tackle"]),
        Monsoons("Cataboo", ["Psychic"], {"hp": 200, "attack": 38, "defense": 32, "speed": 100}, ["Confuse Ray", "Gust"])
    ]

    running = True
    while running:
        player = random.choice(all_monsoons)
        opponent = random.choice([m for m in all_monsoons if m != player])
        
        # Reset battle state
        player.hp = player.max_hp
        opponent.hp = opponent.max_hp
        for move in player.moves + opponent.moves:
            move.pp = move.max_pp
        
        battle_log = ["Battle Start!"]
        turn = 0
        
        while player.hp > 0 and opponent.hp > 0:
            screen.fill(BG_COLOR)
            
            # Generate move buttons
            move_buttons = []
            font = pygame.font.Font(None, 28)
            for i, move in enumerate(player.moves):
                x = 70 + (i % 2) * 350
                y = 420 + (i // 2) * 40
                rect = pygame.Rect(x, y, 300, 30)
                move_buttons.append((rect, i))
            
            # Draw UI
            draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
            pygame.display.flip()
            
            # Get player input
            selected_move = None
            while selected_move is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        pygame.quit()
                        return
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for rect, move_idx in move_buttons:
                            if rect.collidepoint(event.pos) and player.moves[move_idx].pp > 0:
                                selected_move = move_idx
                for _ in range(15):  # Adjust for speed/smoothness
                    if player.display_hp > player.hp:
                        player.display_hp -= max(1, (player.display_hp - player.hp) // 4)
                    if player.display_hp < player.hp:
                        player.display_hp += max(1, (player.hp - player.display_hp) // 4)

                    if opponent.display_hp > opponent.hp:
                        opponent.display_hp -= max(1, (opponent.display_hp - opponent.hp) // 4)
                    if opponent.display_hp < opponent.hp:
                        opponent.display_hp += max(1, (opponent.hp - opponent.display_hp) // 4)

                    screen.fill(BG_COLOR)
                    draw_battle_ui(screen, player, opponent, battle_log, move_buttons)
                    pygame.display.flip()
                    
                    clock.tick(60)
            
            # Battle turn
            opponent_move = random.choice([i for i, m in enumerate(opponent.moves) if m.pp > 0])
            turn_log = []
            
            # Speed-based turn order
            if player.speed >= opponent.speed:
                turn_log.append(player.attack(selected_move, opponent))
                if opponent.hp > 0:
                    turn_log.append(opponent.attack(opponent_move, player))
            else:
                turn_log.append(opponent.attack(opponent_move, player))
                if player.hp > 0:
                    turn_log.append(player.attack(selected_move, opponent))
            
            battle_log.extend(turn_log)
            turn += 1
            
            # Check battle end
            if player.hp <= 0 or opponent.hp <= 0:
                break
        
        # Battle end
        if player.hp <= 0:
            battle_log.append("You lost the battle!")
        else:
            battle_log.append("You won the battle!")
        
        # Show final state
        screen.fill(BG_COLOR)
        draw_battle_ui(screen, player, opponent, battle_log, [])
        pygame.display.flip()
        pygame.time.wait(3000)

    pygame.quit()

if __name__ == "__main__":
    main()