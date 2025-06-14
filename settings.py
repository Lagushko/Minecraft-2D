import pygame, json, os

blocks = {
    "grass": {"break": 0.75, "drop": ["dirt"], "sound": ("grass", "grass", "grass")},
    "dirt": {"break": 0.75, "sound": ("gravel", "gravel", "gravel")},
    "sand": {"break": 0.5, "physics": True, "sound": ("sand", "sand", "sand")},
    "stone": {"break": 1.5, "drop": ["cobblestone"], "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "cobblestone": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "lava": {"break": float('inf'), "liquid": [1, 0], "sound": (None, None, None)},
    "water": {"break": float('inf'), "liquid": [0.5, 0], "sound": (None, None, None)},
    "bedrock": {"break": float('inf'), "sound": ("stone", "stone", "stone")},
    "wood": {"break": 1.0, "sound": ("wood", "wood", "wood")},
    "leaves": {"break": 0.25, "drop": ["leaves"]*9+["apple"], "notooldrop": [None]*9+["apple"], "tools": "scissors", "sound": ("grass", "stone", "grass")},
    "sandstone": {"break": 1.0, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "gravel": {"break": 0.75, "drop": ["gravel"]*9+["flint"], "physics": True, "sound": ("gravel", "gravel", "gravel")},
    "coal_ore": {"break": 1.5, "drop": ["coal"], "tools": "_pickaxe", "exc": ["wood_pickaxe"], "sound": ("stone", "stone", "stone")},
    "iron_ore": {"break": 1.5, "tools": "_pickaxe", "exc": ["wood_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "gold_ore": {"break": 1.5, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "diamond_ore": {"break": 1.5, "drop": ["diamond"], "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "emerald_ore": {"break": 1.5, "drop": ["emerald"], "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "redstone_ore": {"break": 1.5, "drop": ["redstone"], "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "lapis_ore": {"break": 1.5, "drop": (["lapis"], 7), "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe"], "sound": ("stone", "stone", "stone")},
    "planks": {"break": 1.0, "sound": ("wood", "wood", "wood")},
    "crafting_table": {"break": 1.0, "sound": ("wood", "wood", "wood")},
    "clay": {"break": 0.6, "drop": (["clay_ball"], 4), "sound": ("gravel", "gravel", "gravel")},
    "glass": {"break": 0.4, "drop": [None], "sound": (None, "stone", "stone")},
    "obsidian": {"break": 9.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "iron_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "snow": {"break": 0.3, "drop": (["snowball"], 4), "sound": ("snow", "snow", "snow")},
    "ice": {"break": 0.5, "sound": (None, "snow", "stone")},
    "nether_bricks": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "netherrack": {"break": 0.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "soul_sand": {"break": 0.8, "sound": ("sand", "sand", "sand")},
    "glowstone": {"break": 0.6, "drop": (["glowstone_dust"], 4), "sound": (None, "stone", "stone")},
    "bricks": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "quartz_ore": {"break": 1.5, "drop": ["quartz"], "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "end_stone": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "anvil": {"break": 5.0, "tools": "_pickaxe", "physics": True, "sound": ("stone", "stone", "stone")},
    "iron_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "gold_block": {"break": 3.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "diamond_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "emerald_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "lapis_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe"], "sound": ("stone", "stone", "stone")},
    "redstone_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe", "stone_pickaxe", "gold_pickaxe"], "sound": ("stone", "stone", "stone")},
    "coal_block": {"break": 5.0, "tools": "_pickaxe", "exc": ["wood_pickaxe"], "sound": ("stone", "stone", "stone")},
    "quartz_block": {"break": 5.0, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "diorite": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "andesite": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "granite": {"break": 1.5, "tools": "_pickaxe", "sound": ("stone", "stone", "stone")},
    "wool": {"break": 0.25, "sound": ("cloth", "stone", "cloth")},
    "cobweb": {"break": 20, "drop": ["string"], "tools": "_sword", "sound": (None, None, None)},
    "melon": {"break": 0.5, "drop": (["melon_slice"], 4), "sound": ("wood", "stone", "wood")}
}
# break - time for breaking block in seconds
# drop - items or blocks that will drop if don't block drop themself (if more than 1 items it will be chosen randomly, and if make it a tuple the second value is an amount of drop)
# notooldrop - same as drop, but ignores tools and exc conditions
# physics - add if block will have physics like sand
# tools - name of only tool that can break this block to have drop
# exc - exceptions for tools that can't break this block
# liquid - speed at which the liquid spreads in seconds, last time updated (just leave 0)
# sound - sound name while breaking block, sound name while moving on the block

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

    # food
    "apple": {"hunger": 4},
    "bread": {"hunger": 5},
    "carrot": {"hunger": 3},
    "melon_slice": {"hunger": 2},
    "potato": {"hunger": 1},
    "baked_potato": {"hunger": 5},
    "beef": {"hunger": 2},
    "cooked_beef": {"hunger": 8},
    "chicken": {"hunger": 2},
    "cooked_chicken": {"hunger": 6},
    "rabbit": {"hunger": 1},
    "cooked_rabbit": {"hunger": 5},
    "rabbit_stew": {"hunger": 5},
    "golden_apple": {"hunger": 4},

    # other
    "water_bucket": {"block": "water", "remain": "bucket"},
    "lava_bucket": {"block": "lava", "remain": "bucket"},
}
# dig - how many times faster a targeted block breaks (targeted blocks are in dict mining)
# strength - number of uses of the item to break
# damage - damage that this item deals
# hunger - how many hunger units it will give
# block - if you can place this item in the form of a block
# remain - if after using an item another one should appear

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
    "brick": ([None, None, None, None, "clay_ball", None, None, "coal", None], 1),
    "scissors": ([None, None, None, None, "iron", None, "iron", None, None], 238),
    "bucket": ([None, None, None, "iron", None, "iron", None, "iron", None], 1),
    "cooked_beef": ([None, None, None, None, "beef", None, None, "coal", None], 1),
    "cooked_chicken": ([None, None, None, None, "chicken", None, None, "coal", None], 1),
    "cooked_rabbit": ([None, None, None, None, "rabbit", None, None, "coal", None], 1),
    "baked_potato": ([None, None, None, None, "potato", None, None, "coal", None], 1),
    "rabbit_stew": ([None, "cooked_rabbit", None, "carrot", "baked_potato", "mushroom", None, "bowl", None], 1),
    "bowl": ([None, None, None, "planks", None, "planks", None, "planks", None], 1),
    "coal": ([None, None, None, None, "coal_block", None, None, None, None], 9),
    "iron.d1": ([None, None, None, None, "iron_block", None, None, None, None], 9),
    "gold.d1": ([None, None, None, None, "gold_block", None, None, None, None], 9),
    "diamond": ([None, None, None, None, "diamond_block", None, None, None, None], 9),
    "emerald": ([None, None, None, None, "emerald_block", None, None, None, None], 9),
    "lapis": ([None, None, None, None, "lapis_block", None, None, None, None], 9),
    "redstone": ([None, None, None, None, "redstone_block", None, None, None, None], 9),
    "quartz": ([None, None, None, None, "quartz_block", None, None, None, None], 9),
    "golden_apple": (["gold", "gold", "gold", "gold", "apple", "gold", "gold", "gold", "gold"], 1),
}
# key is a item that you can craft, if item have many crafts just add .d1, .d2 and so on to name
# value is a tuple where first is list of items that needed for craft
# and where second is count of items that you will get from craft

mining = {
    "_axe": ["wood", "planks", "crafting_table"],
    "_pickaxe": ["stone", "ore", "bricks", "anvil", "netherrack", "_block", "andesite", "diorite", "granite"],
    "_shovel": ["grass", "grass", "sand", "snow", "gravel"],
    "scissors": ["leaves", "wool"],
    "_sword": ["cobweb"]
}
# key is a type of tool that needed
# value is a list with blocks that this tool can break 
# also you can put a part of the name so as not to write a lot of identical blocks (like _block for diamond, iron _block)

pygame.init()

screen_info = pygame.display.Info()
screen_width, screen_height = screen_info.current_w, screen_info.current_h
BLOCK_SIZE = screen_height//30*3

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

extra_health = 0
health = 20
hunger = 20
time = 0

VERSION = "Beta-0.13.0"

translated = {
    "Play": "Play",
    "Settings": "Settings",
    "Exit": "Exit",
    "Back": "Back",
    "Creative mode": "Creative mode",
    "Flat world": "Flat world",
    "Keep inventory": "Keep inventory",
    "Daylight cycle": "Daylight cycle",
    "Weather cycle": "Weather cycle",
    "Mob spawning": "Mob spawning",
    "Mob loot": "Mob loot",
    "Left": "Left",
    "Right": "Right",
    "Jump": "Jump",
    "Sneak": "Sneak",
    "Run": "Run",
    "Inventory": "Inventory",
    "Background build": "Background build",
    "Albanian": "Albanian",
    "Belarusian": "Belarusian",
    "Bulgarian": "Bulgarian",
    "Croatian": "Croatian",
    "Czech": "Czech",
    "Danish": "Danish",
    "Dutch": "Dutch",
    "English": "English",
    "Estonian": "Estonian",
    "Finnish": "Finnish",
    "French": "French",
    "German": "German",
    "Greek": "Greek",
    "Hungarian": "Hungarian",
    "Icelandic": "Icelandic",
    "Italian": "Italian",
    "Latvian": "Latvian",
    "Lithuanian": "Lithuanian",
    "Macedonian": "Macedonian",
    "Norwegian": "Norwegian",
    "Polish": "Polish",
    "Portuguese": "Portuguese",
    "Romanian": "Romanian",
    "Russian": "Russian",
    "Serbian": "Serbian",
    "Slovak": "Slovak",
    "Slovenian": "Slovenian",
    "Spanish": "Spanish",
    "Swedish": "Swedish",
    "Turkish": "Turkish",
    "Ukrainian": "Ukrainian",
    "Controls": "Controls",
    "Languages": "Languages",
    "Load world": "Load world",
    "Generate world": "Generate world",
    "Loading world": "Loading world",
    "Generating world": "Generating world",
    "ERROR file is damaged. Generating new world": "ERROR file is damaged. Generating new world",
    "Sound effects": "Sound effects",
    "Music": "Music",
    "Sounds": "Sounds"
}
language = "en"
vol_music = 1.0
vol_sound = 1.0

# controls
LEFT = [pygame.K_a]
RIGHT = [pygame.K_d]
JUMP = [pygame.K_SPACE]
SNEAK = [pygame.K_LSHIFT]
RUN = [pygame.K_LCTRL]
WINDOW = [pygame.K_e]
BACK_BUILD = [pygame.K_s]
MENU = [pygame.K_ESCAPE]

def get_key(key_name):
    key_name = key_name.lower().replace(" ", "_")
    for attr in dir(pygame):
        if attr.startswith("K_") and attr[2:].lower() == key_name:
            return getattr(pygame, attr)
    raise ValueError()

files_path = str(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(files_path, "other", "memory.json")
with open(json_path, "r") as file:
    data = json.load(file)
for key, value in data.items():
    if key in ["language", "vol_music", "vol_sound"]:
        globals()[key] = value
    else:
        try:
            globals()[key] = [get_key(value)]
        except Exception as e:
            continue

# rules
creative_mode = [False]
flat_world = [False]
keep_inventory = [False]
daylight_cycle = [True]
weather_cycle = [True]
mob_spawning = [True]
mob_loot = [True]
