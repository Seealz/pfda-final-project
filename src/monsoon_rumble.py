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

# Load sounds (placeholders, actual files must exist)
MOVE_SOUND = pygame.mixer.Sound("assets/sounds/move.wav")
FAINT_SOUND = pygame.mixer.Sound("assets/sounds/faint.wav")

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
        self.speed = stats.get("speed", 50)
        self.status = None
        self.moves = []
        for move_name in move_names:
            original_move = MOVES[move_name]
            self.moves.append(Move(original_move.name, original_move.type, original_move.power, original_move.max_pp))
    
        try:
            front = pygame.image.load(f"assets/sprites/{name.lower()}_front.png").convert_alpha()
            back = pygame.image.load(f"assets/sprites/{name.lower()}_back.png").convert_alpha()
        except:
            front = pygame.Surface((50, 50)); front.fill((255, 0, 0))
            back = pygame.Surface((50, 50)); back.fill((0, 0, 255))

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

        MOVE_SOUND.play()
        move.pp -= 1
        multiplier = 1.0
        for t in target.types:
            multiplier *= TYPE_EFFECTIVENESS.get(move.type, {}).get(t, 1.0)
        damage = max(1, int((move.power + self.attack_stat - target.defense) * multiplier))
        target.hp = max(0, target.hp - damage)

        log = f"{self.name} used {move.name}! It dealt {damage} damage."
        if multiplier > 1:
            log += " It's super effective!"
        elif multiplier < 1:
            log += " It's not very effective."

        if move.name == "Confuse Ray":
            target.status = "Confused"
            log += f" {target.name} became confused!"

        if move.name == "Thunder Wave":
            target.status = "Paralyzed"
            log += f" {target.name} is paralyzed!"

        if target.hp <= 0:
            FAINT_SOUND.play()
            log += f" {target.name} fainted!"

        return log
    
    def battle_turn(player, opponent, player_move_index, opponent_move_index, log):
        first, second = (player, opponent)
        first_move, second_move = (player_move_index, opponent_move_index)

        if opponent.speed > player.speed:
            first, second = opponent, player
            first_move, second_move = opponent_move_index, player_move_index

        log.append(first.attack(first_move, second))
        if second.hp > 0:
            log.append(second.attack(second_move, first))

