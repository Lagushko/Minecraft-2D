import pygame

blocks = {
    "grass": {"break": 0.75, "drop": "dirt"},
    "dirt": {"break": 0.75},
    "sand": {"break": 0.5, "physics": True},
    "stone": {"break": 1.5, "drop": "cobblestone", "tools": "_pickaxe"},
    "cobblestone": {"break": 1.5, "tools": "_pickaxe"},
    "lava": {"break": float('inf'), "liquid": [1, 0]},
    "water": {"break": float('inf'), "liquid": [0.5, 0]},
    "bedrock": {"break": float('inf')},
    "wood": {"break": 1.0},
    "leaves": {"break": 0.25, "tools": "scissors"},
    "sandstone": {"break": 1.0, "tools": "_pickaxe"},
    "gravel": {"break": 0.75, "physics": True},
    "coal_ore": {"break": 1.5, "drop": "coal", "tools": "_pickaxe", "exc": ["wood_pickaxe"]},
    "iron_ore": {"break": 1.5, "tools": "_pickaxe", "exc": ["wood_pickaxe", "gold_pickaxe"]},
    "gold_ore": {"break": 1.5, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "diamond_ore": {"break": 1.5, "drop": "diamond", "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "emerald_ore": {"break": 1.5, "drop": "emerald", "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "redstone_ore": {"break": 1.5, "drop": "redstone", "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "lapis_ore": {"break": 1.5, "drop": "lapis", "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe"]},
    "planks": {"break": 1.0},
    "crafting_table": {"break": 1.0},
    "clay": {"break": 0.6, "drop": "clay_ball"},
    "glass": {"break": 0.4, "drop": None},
    "obsidian": {"break": 9.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "iron_pickaxe", "gold_pickaxe"]},
    "snow": {"break": 0.3, "drop": "snowball"},
    "ice": {"break": 0.5},
    "nether_bricks": {"break": 1.5, "tools": "_pickaxe"},
    "netherrack": {"break": 0.5, "tools": "_pickaxe"},
    "soul_sand": {"break": 0.8},
    "glowstone": {"break": 0.6, "drop": "glowstone_dust"},
    "bricks": {"break": 1.5, "tools": "_pickaxe"},
    "quartz_ore": {"break": 1.5, "drop": "quartz", "tools": "_pickaxe"},
    "end_stone": {"break": 1.5, "tools": "_pickaxe"},
    "anvil": {"break": 5.0, "tools": "_pickaxe", "physics": True},
    "iron_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "gold_block": {"break": 3.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "diamond_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "emerald_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "lapis_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe"]},
    "redstone_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"]},
    "coal_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe"]},
    "quartz_block": {"break": 5.0, "tools": "_pickaxe"},
    "diorite": {"break": 1.5, "tools": "_pickaxe"},
    "andesite": {"break": 1.5, "tools": "_pickaxe"},
    "granite": {"break": 1.5, "tools": "_pickaxe"},
    "wool": {"break": 0.25},
    "cobweb": {"break": 20, "drop": "string", "tools": "_sword"}
}
items = {
    # tools
    "wood_pickaxe": {"dig": 2, "strength": 59},
    "stone_pickaxe": {"dig": 3, "strength": 131},
    "iron_pickaxe": {"dig": 4, "strength": 250},
    "gold_pickaxe": {"dig": 12, "strength": 32}, 
    "diamond_pickaxe": {"dig": 8, "strength": 1561},
    "wood_shovel": {"dig": 2, "strength": 59},
    "stone_shovel": {"dig": 3, "strength": 131},
    "iron_shovel": {"dig": 4, "strength": 250},
    "gold_shovel": {"dig": 12, "strength": 32},
    "diamond_shovel": {"dig": 8, "strength": 1561},
    "wood_axe": {"dig": 2, "strength": 59, "damage": 7},
    "stone_axe": {"dig": 3, "strength": 131, "damage": 9},
    "iron_axe": {"dig": 4, "strength": 250, "damage": 9},
    "gold_axe": {"dig": 12, "strength": 32, "damage": 7},
    "diamond_axe": {"dig": 8, "strength": 1561, "damage": 10},
    "wood_sword": {"dig": 4, "strength": 59, "damage": 4},
    "stone_sword": {"dig": 6, "strength": 131, "damage": 5},
    "iron_sword": {"dig": 8, "strength": 250, "damage": 6},
    "gold_sword": {"dig": 12, "strength": 32, "damage": 4},
    "diamond_sword": {"dig": 10, "strength": 1561, "damage": 7},
    "scissors": {"dig": 5, "strength": 238},
}
craft = {
    # blocks
    "stone": ([None, None, None, None, "cobblestone", None, None, "coal", None], 1),
    "planks": ([None, None, None, None, "wood", None, None, None, None], 4),
    "crafting_table": ([None, None, None, "planks", "planks", None, "planks", "planks", None], 1),
    "snow": ([None, None, None, "snowball", "snowball", None, "snowball", "snowball", None], 1),
    "glowstone": ([None, None, None, "glowstone_dust", "glowstone_dust", None, "glowstone_dust", "glowstone_dust", None], 1),
    "glass": ([None, None, None, None, "sand", None, None, "coal", None], 1),
    "iron_block": (["iron", "iron", "iron", "iron", "iron", "iron", "iron", "iron", "iron"], 1),
    "gold_block": (["gold", "gold", "gold", "gold", "gold", "gold", "gold", "gold", "gold"], 1),
    "diamond_block": (["diamond", "diamond", "diamond", "diamond", "diamond", "diamond", "diamond", "diamond", "diamond"], 1),
    "emerald_block": (["emerald", "emerald", "emerald", "emerald", "emerald", "emerald", "emerald", "emerald", "emerald"], 1),
    "lapis_block": (["lapis", "lapis", "lapis", "lapis", "lapis", "lapis", "lapis", "lapis", "lapis"], 1),
    "redstone_block": (["redstone", "redstone", "redstone", "redstone", "redstone", "redstone", "redstone", "redstone", "redstone"], 1),
    "coal_block": (["coal", "coal", "coal", "coal", "coal", "coal", "coal", "coal", "coal"], 1),
    "quartz_block": (["quartz", "quartz", "quartz", "quartz", "quartz", "quartz", "quartz", "quartz", "quartz"], 1),
    "anvil": (["iron_block", "iron_block", "iron_block", None, "iron", None, "iron", "iron", "iron"], 1),
    "diorite": ([None, None, None, "cobblestone", "quartz", None, "quartz", "cobblestone", None], 1),
    "andesite": ([None, None, None, "diorite", "cobblestone", None, None, None, None], 1),
    "granite": ([None, None, None, "diorite", "quartz", None, None, None, None], 1),
    "bricks": ([None, None, None, "brick", "brick", None, "brick", "brick", None], 1),
    "clay": ([None, None, None, "clay_ball", "clay_ball", None, "clay_ball", "clay_ball", None], 1),
    "wool": ([None, None, None, "string", "string", None, "string", "string", None], 1),

    # items
    "wood_axe": (["planks", "planks", None, None, "stick", None, None, "stick", None], 59),
    "stone_axe": (["cobblestone", "cobblestone", None, None, "stick", None, None, "stick", None], 131),
    "iron_axe": (["iron", "iron", None, None, "stick", None, None, "stick", None], 250),
    "gold_axe": (["gold", "gold", None, None, "stick", None, None, "stick", None], 32),
    "diamond_axe": (["diamond", "diamond", None, None, "stick", None, None, "stick", None], 1561),
    "wood_shovel": ([None, "planks", None, None, "stick", None, None, "stick", None], 59),
    "stone_shovel": ([None, "cobblestone", None, None, "stick", None, None, "stick", None], 131),
    "iron_shovel": ([None, "iron", None, None, "stick", None, None, "stick", None], 250),
    "gold_shovel": ([None, "gold", None, None, "stick", None, None, "stick", None], 32),
    "diamond_shovel": ([None, "diamond", None, None, "stick", None, None, "stick", None], 1561),
    "wood_pickaxe": (["planks", "planks", "planks", None, "stick", None, None, "stick", None], 59),
    "stone_pickaxe": (["cobblestone", "cobblestone", "cobblestone", None, "stick", None, None, "stick", None], 131),
    "iron_pickaxe": (["iron", "iron", "iron", None, "stick", None, None, "stick", None], 250),
    "gold_pickaxe": (["gold", "gold", "gold", None, "stick", None, None, "stick", None], 32),
    "diamond_pickaxe": (["diamond", "diamond", "diamond", None, "stick", None, None, "stick", None], 1561),
    "wood_sword": ([None, "planks", None, None, "planks", None, None, "stick", None], 59),
    "stone_sword": ([None, "cobblestone", None, None, "cobblestone", None, None, "stick", None], 131),
    "iron_sword": ([None, "iron", None, None, "iron", None, None, "stick", None], 250),
    "gold_sword": ([None, "gold", None, None, "gold", None, None, "stick", None], 32),
    "diamond_sword": ([None, "diamond", None, None, "diamond", None, None, "stick", None], 1561),
    "iron": ([None, None, None, None, "iron_ore", None, None, "coal", None], 1),
    "gold": ([None, None, None, None, "gold_ore", None, None, "coal", None], 1),
    "stick": ([None, None, None, None, "planks", None, None, "planks", None], 4),
    "clay_ball": ([None, None, None, None, "clay", None, None, None, None], 1),
    "glowstone_dust": ([None, None, None, None, "glowstone", None, None, None, None], 1),
    "snowball": ([None, None, None, None, "snow", None, None, None, None], 1),
    "quartz": ([None, None, None, None, "quartz_ore", None, None, None, None], 1),
    "brick": ([None, None, None, None, "clay_ball", None, None, "coal", None], 1),
    "scissors": ([None, None, None, None, "iron", None, "iron", None, None], 238),
}
mining = {"_axe": ["wood", "planks", "crafting_table"],
          "_pickaxe": ["stone", "ore", "bricks", "anvil", "netherrack", "_block", "andesite", "diorite", "granite"],
          "_shovel": ["dirt", "grass", "sand", "snow", "gravel"],
          "scissors": ["leaves", "wool"],
          "_sword": ["cobweb"]}

pygame.init()

screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
BLOCK_SIZE = screen_height//10

player_width, player_height = BLOCK_SIZE, BLOCK_SIZE*1.8
player_x, player_y = 0, -BLOCK_SIZE*4
player_speed = BLOCK_SIZE/10
player_jump_speed = -20
player_velocity_y = 0
gravity = 1.25

default_speed = BLOCK_SIZE/10
default_width, default_height = BLOCK_SIZE, BLOCK_SIZE*1.8
shift_width, shift_height = BLOCK_SIZE, BLOCK_SIZE*1.5
speed_multiplier = 1.5

health = 20
hunger = 20

VERSION = "Alpha-0.10.0"

# controls
LEFT = pygame.K_a
RIGHT = pygame.K_d
JUMP = pygame.K_SPACE
SNEAK = pygame.K_LSHIFT
RUN = pygame.K_LCTRL
WINDOW = pygame.K_e
BACK_BUILD = pygame.K_q
SAVE = pygame.K_KP_ENTER

# rules
keep_inventory = True
