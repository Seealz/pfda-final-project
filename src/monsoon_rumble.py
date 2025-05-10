import pygame
import random



SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
BG_COLOR = (245, 245, 245)
WHITE = (255, 255, 255)
SPRITE_SCALE_FACTOR = 3
PLAYER_SPRITE_POS = (100, 250)
OPPONENT_SPRITE_POS = (500, 50)



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
        self.attack_stat = stats["attack"]
        self.defense = stats["defense"]
        self.move_names = move_names
        self.moves = []
        
        for move_name in move_names:
            original_move = MOVES[move_name]
            new_move = Move(original_move.name, original_move.type, original_move.power, original_move.max_pp)
            self.moves.append(new_move)

        # Load and scale sprites
        front_sprite = pygame.image.load(f"assets/sprites/{name.lower()}_front.png").convert_alpha()
        back_sprite = pygame.image.load(f"assets/sprites/{name.lower()}_back.png").convert_alpha()
        
        self.front_sprite = pygame.transform.scale(
            front_sprite, 
            (front_sprite.get_width() * SPRITE_SCALE_FACTOR, 
             front_sprite.get_height() * SPRITE_SCALE_FACTOR)
        )
        self.back_sprite = pygame.transform.scale(
            back_sprite,
            (back_sprite.get_width() * SPRITE_SCALE_FACTOR,
             back_sprite.get_height() * SPRITE_SCALE_FACTOR)
        )


    def attack(self, move_index, target):
        move = self.moves[move_index]
        if move.pp <= 0:
            return 0, f"{self.name} tried to use {move.name} but it's out of PP!"
        move.pp -= 1
        damage = max(1, move.power + self.attack_stat - target.defense)
        target.hp = max(0, target.hp - damage)
        return damage, f"{self.name} used {move.name}! It dealt {damage} damage!"
    


def draw_hp_bar(screen, x, y, current_hp, max_hp):
    ratio = current_hp / max_hp
    pygame.draw.rect(screen, (0, 0, 0), (x, y, 100, 10), 1)
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(100 * ratio), 10))

def draw_text_box(screen, text):
    font = pygame.font.Font(None, 32)
    text_surface = font.render(text, True, (0, 0, 0))
    pygame.draw.rect(screen, WHITE, (50, SCREEN_HEIGHT - 100, SCREEN_WIDTH - 100, 80))
    pygame.draw.rect(screen, (0, 0, 0), (50, SCREEN_HEIGHT - 100, SCREEN_WIDTH - 100, 80), 2)
    screen.blit(text_surface, (60, SCREEN_HEIGHT - 80))

def show_start_screen(screen):
    font = pygame.font.Font(None, 64)
    screen.fill((220, 220, 220))
    title = font.render("Monsoon Rumble", True, (0, 0, 0))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_select_screen(screen, all_monsoons):
    font = pygame.font.Font(None, 36)
    selection_text = font.render("Select your Monsoon:", True, (0, 0, 0))
    screen.fill((220, 220, 220))
    screen.blit(selection_text, (SCREEN_WIDTH // 2 - selection_text.get_width() // 2, 100))

    monsoon_buttons = []
    for i, monsoon in enumerate(all_monsoons):
        label = font.render(monsoon.name, True, (0, 0, 0))
        rect = label.get_rect(topleft=(SCREEN_WIDTH // 2 - label.get_width() // 2, 200 + i * 40))
        pygame.draw.rect(screen, (240, 240, 240), rect.inflate(20, 10))
        pygame.draw.rect(screen, (0, 0, 0), rect.inflate(20, 10), 2)
        screen.blit(label, rect)
        monsoon_buttons.append((rect, i))

    pygame.display.flip()

    selected_monsoon = None
    while selected_monsoon is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for rect, i in monsoon_buttons:
                    if rect.collidepoint(event.pos):
                        selected_monsoon = all_monsoons[i]
                        return selected_monsoon

def show_end_screen(screen, message, color):
    font = pygame.font.Font(None, 64)
    small_font = pygame.font.Font(None, 36)
    while True:
        screen.fill((220, 220, 220))
        msg = font.render(message, True, color)
        button_text = small_font.render("Return to Main Menu", True, (0, 0, 0))
        button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        pygame.draw.rect(screen, (240, 240, 240), button_rect.inflate(20, 10))
        pygame.draw.rect(screen, (0, 0, 0), button_rect.inflate(20, 10), 2)
        screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
        screen.blit(button_text, button_rect)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                return



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

    running_global = True
    while running_global:
        show_start_screen(screen)
        player = show_select_screen(screen, all_monsoons)
        opponent = random.choice([m for m in all_monsoons if m != player])
        
        # Resets stats for new battle
        player.hp = player.max_hp
        opponent.hp = opponent.max_hp
        for move in player.moves:
            move.pp = move.max_pp
        for move in opponent.moves:
            move.pp = move.max_pp

        running_battle = True
        battle_text = "Battle Start!"
        while running_battle:
            screen.fill(BG_COLOR)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_battle = False
                    running_global = False

            screen.blit(player.back_sprite, PLAYER_SPRITE_POS)
            screen.blit(opponent.front_sprite, OPPONENT_SPRITE_POS)
            
            # Draws HP bars
            draw_hp_bar(screen, PLAYER_SPRITE_POS[0], PLAYER_SPRITE_POS[1] - 30, player.hp, player.max_hp)
            draw_hp_bar(screen, OPPONENT_SPRITE_POS[0], OPPONENT_SPRITE_POS[1] - 30, opponent.hp, opponent.max_hp)
            
            # Draws text box
            draw_text_box(screen, battle_text)

            # Draws move buttons
            font = pygame.font.Font(None, 28)
            move_buttons = []
            for i, move in enumerate(player.moves):
                if move.pp <= 0:
                    text_color = (150, 150, 150)
                else:
                    text_color = WHITE
                label = font.render(f"{move.name} (PP: {move.pp})", True, text_color)
                rect = label.get_rect(topleft=(SCREEN_WIDTH - 250, 400 + i * 30))
                screen.blit(label, rect)
                if move.pp > 0:
                    move_buttons.append((rect, i))

            pygame.display.flip()

            # Move selection
            selected_move = None
            while selected_move is None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        for rect, i in move_buttons:
                            if rect.collidepoint(event.pos):
                                selected_move = i
                clock.tick(FPS)

            # Player attack
            damage, battle_text = player.attack(selected_move, opponent)
            if opponent.hp <= 0:
                battle_text += f" {opponent.name} fainted!"
                pygame.display.flip()
                pygame.time.wait(1500)
                show_end_screen(screen, "You Win!", (0, 200, 0))
                break

            # Opponent attack
            available_moves = [i for i, m in enumerate(opponent.moves) if m.pp > 0]
            if available_moves:
                opponent_move = random.choice(available_moves)
                _, battle_text = opponent.attack(opponent_move, player)
                if player.hp <= 0:
                    battle_text += f" {player.name} fainted!"
                    pygame.display.flip()
                    pygame.time.wait(1500)
                    show_end_screen(screen, "You Lose!", (200, 0, 0))
                    break
            else:
                battle_text = f"{opponent.name} has no moves left!"

            clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()