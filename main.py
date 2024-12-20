import random, noise
from math import sin, cos, sqrt, pi
from tkinter import filedialog
from deep_translator import GoogleTranslator
from settings import *

clock = pygame.time.Clock()
state = "menu"
FPS = 25

class Block:
    def __init__(self, x, y, type, collide=True, parent=None, liquidlevel=0):
        self.x = x
        self.y = y
        self.type = type
        
        self.platform = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        self.collide = collide

        self.broke = False
        self.breaktime = 0

        self.liquided = False
        self.liquidlevel = liquidlevel
        self.parent = parent
    def breaking(self, endtime):
        global mouse_pos, platforms, inventory, inv_num, chunks, cur_chunk, creative_mode, vol_sound
        if mouse_pos != (self.x, self.y):
            self.broke = False
            self.breaktime = 0
        if self.broke:
            self.breaktime += 1  
        if self.breaktime >= endtime * FPS or creative_mode[0]:
            count = 1
            if "drop" in blocks[self.type]:
                if len(blocks[self.type]["drop"]) > 1 and type(blocks[self.type]["drop"][0]) is list:
                    drop = random.choice(blocks[self.type]["drop"][0])
                    count = int(blocks[self.type]["drop"][1])
                else:
                    drop = random.choice(blocks[self.type]["drop"])
            else:
                drop = self.type
            notooldrop = random.choice(blocks[self.type].get("notooldrop", [None])) or False
            tools = str(blocks[self.type].get("tools", inventory[inv_num][0]))
            exc = blocks[self.type].get("exc", "")
            if self in platforms:
                platforms.remove(self)
                if "sound" in blocks[self.type] and blocks[self.type]["sound"][0] != None:
                    sound = blocks[self.type]["sound"][0] + str(random.randint(1, 4))
                    sound_path = os.path.join(files_path, "sounds", "dig", f"{sound}.ogg")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                try:
                    chunks[cur_chunk][0].remove(self)
                except: None
            blks = [get_block_at(mouse=(self.x, self.y-BLOCK_SIZE)), get_block_at(mouse=(self.x-BLOCK_SIZE, self.y)), get_block_at(mouse=(self.x+BLOCK_SIZE, self.y))]
            for b in blks:
                if b:
                    b.liquided = False
            self.broke = False
            if ((tools in str(inventory[inv_num][0]) and not str(inventory[inv_num][0]) in exc) or notooldrop is not False) and not creative_mode[0]:
                if notooldrop is not False and not (tools in str(inventory[inv_num][0]) and not str(inventory[inv_num][0]) in exc):
                    drop = notooldrop
                if drop is not None:
                    if any(drop in sublist for sublist in inventory):
                        inventory[next(i for i, sublist in enumerate(inventory) if drop in sublist)][1] += count
                    else:
                        if inventory.count([None, 0]) > 0:
                            ind = 0
                            for i, a in enumerate(inventory):
                                if a[0] == None:
                                    ind = i
                                    break
                            inventory[ind] = [drop, count]
            if inventory[inv_num][0] is not None and any(key in inventory[inv_num][0] for key in mining.keys()):
                inventory[inv_num][1] -= 1
                if inventory[inv_num][1] == 0:
                    inventory[inv_num][0] = None 
        elif endtime * FPS // 5 > 0:
            if self.breaktime % (endtime * FPS // 5) == 0:
                if "sound" in blocks[self.type] and blocks[self.type]["sound"][2] != None and False:
                    sound = blocks[self.type]["sound"][2] + str(random.randint(1, 4))
                    sound_path = os.path.join(files_path, "sounds", "dig", f"{sound}.ogg")
                    pygame.mixer.Sound(sound_path).play()
    def liquid(self):
        global platforms, chunks, cur_chunk
        opp = ("water", "cobblestone", 3) if self.type == "lava" else ("lava", "obsidian", 7)
        block_down = get_block_at(mouse=(self.x, self.y+BLOCK_SIZE))
        block_left = get_block_at(mouse=(self.x-BLOCK_SIZE, self.y))
        block_right = get_block_at(mouse=(self.x+BLOCK_SIZE, self.y))
        for b in [block_down, block_left, block_right]:
            if b and (b.type == opp[0] or (self.type=="lava" and b.type=="ice")):
                if self.type == "lava":
                    if b.type == "ice": block = Block(self.x, self.y, "soul_sand")
                    else:block = Block(self.x, self.y, opp[1])
                    platforms.append(block)
                    chunks[cur_chunk][0].append(block)
                    if self in platforms:
                        platforms.remove(self)
                        try:
                            chunks[cur_chunk][0].remove(self)
                        except: None
                    block_up = get_block_at(mouse=(self.x, self.y-BLOCK_SIZE))
                    if block_up:
                        block_up.liquided = False
                else:
                    block = Block(b.x, b.y, opp[1])
                    platforms.append(block)
                    chunks[cur_chunk][0].append(block)
                    if b in platforms:
                        platforms.remove(b)
                        try:
                            chunks[cur_chunk][0].remove(b)
                        except: None
                    block_up = get_block_at(mouse=(b.x, b.y-BLOCK_SIZE))
                    if block_up:
                        block_up.liquided = False
                return
            if b == block_down == None or (b and block_down and b == block_down and b.type == self.type):
                break
        
        if block_down and block_down.type != self.type:
            if self.liquidlevel < opp[2]/(opp[2]+1):
                if not block_left:
                    block = Block(self.x-BLOCK_SIZE, self.y, self.type, parent=self, liquidlevel=self.liquidlevel+1/(opp[2]+1), collide=False)
                    platforms.append(block)
                    chunks[cur_chunk][0].append(block)
                if not block_right:
                    block = Block(self.x+BLOCK_SIZE, self.y, self.type, parent=self, liquidlevel=self.liquidlevel+1/(opp[2]+1), collide=False)
                    platforms.append(block)
                    chunks[cur_chunk][0].append(block)
        elif not block_down:
            block = Block(self.x, self.y+BLOCK_SIZE, self.type, parent=self, liquidlevel=0, collide=False)
            platforms.append(block)
            chunks[cur_chunk][0].append(block)
        elif block_down.type == self.type:
            block_down.liquidlevel = 0
        self.liquided = True

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Minecraft 2D")

WORLD_WIDTH = screen_width//BLOCK_SIZE+4
WORLD_HEIGHT = 15
BEDROCK_Y = -BLOCK_SIZE*64
WORLD_LEFT_X = -BLOCK_SIZE * (WORLD_WIDTH // 2)
WORLD_RIGHT_X = BLOCK_SIZE * (WORLD_WIDTH // 2)
PLATFORM_HEIGHT = BLOCK_SIZE * WORLD_HEIGHT
menu_platforms = []
menu_pos = []
scale = 500
octaves = 4
persistence = 0.5 
lacunarity = 2.0
def tree(x, ground_y):
    global menu_platforms, menu_pos
    tree_height = random.randint(3, 6)
    leaf_radius = random.randint(2, 3)

    for i in range(tree_height):
        if not (x, ground_y - i * BLOCK_SIZE) in menu_pos:
            menu_pos.append((x, ground_y - i * BLOCK_SIZE))
            menu_platforms.append(Block(x, ground_y - i * BLOCK_SIZE, "wood"))
        else:
            if menu_platforms[menu_pos.index((x, ground_y - i * BLOCK_SIZE))].type == "leaves":
                menu_platforms[menu_pos.index((x, ground_y - i * BLOCK_SIZE))].type = "wood"

    leaf_top_y = ground_y - tree_height * BLOCK_SIZE
    for dx in range(-leaf_radius - 1, leaf_radius + 2):
        for dy in range(-leaf_radius - 1, leaf_radius + 2):
            distance = (dx**2 + dy**2)**0.5
            if distance <= leaf_radius + random.uniform(-0.5, 0.5):
                if random.random() < 0.9:
                    if not (x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE) in menu_pos:
                        menu_platforms.append(Block(x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE, "leaves"))
                        menu_pos.append((x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE))
for x in range(WORLD_WIDTH):
    block_x = WORLD_LEFT_X + x * BLOCK_SIZE

    height = int(noise.pnoise1(x / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity) * 20)
    ground_y = height * BLOCK_SIZE

    for y in range(WORLD_HEIGHT):
        block_y = -BLOCK_SIZE*7 + y * BLOCK_SIZE

        if block_y < ground_y - BLOCK_SIZE * random.randint(3, 4):
            block_type = "stone" 
        elif block_y < ground_y - BLOCK_SIZE:
            block_type = "dirt"
        elif block_y < ground_y:
            block_type = "grass"
        else:   
            continue

        if block_y != -3200:
            if not (block_x, -block_y) in menu_pos:
                menu_platforms.append(Block(block_x, -block_y, block_type))
                menu_pos.append((block_x, -block_y))

    if random.random() < 0.1 and block_type == "grass":
        tree(block_x, -ground_y)

save = None
save_path = None
play_open = False
controls_open = False
languages_open = False
sounds_open = False
settings_open = False
scroll = 0

waiting_for_key = False
current_key = None
current_key_name = None

camera_x, camera_y = 0, 0
mouse_pos = (0, 0)

inventory = [[None, 0] for _ in range(36)]
inv_num = 0

background_path = os.path.join(files_path, "images", "_sys_loadbackground.png")
background_image = pygame.image.load(background_path)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
txt = "Generating"

def loading_screen(progress):
    global screen, state
    if state == "loading":
        screen.blit(background_image, (0, 0))

        font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
        text = font.render(VERSION, True, (255, 255, 255))
        text_rect = text.get_rect(topleft=(5, 5))
        screen.blit(text, text_rect)

        font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
        text = font.render(f"{translated.get(f"{txt} world", f"{txt} world")}...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_width//2, screen_height//2-50))
        screen.blit(text, text_rect)

        bar_x, bar_y, bar_width, bar_height = screen_width//4, screen_height//2, screen_width//2, 30
        border_radius = 15
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=border_radius)

        fill_width = int(bar_width * progress)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=border_radius)

        pygame.display.flip()
def stateload(WORLD_WIDTH=200, CHUNK=0):
    global save, save_path, progress, platforms, txt, inventory, player_x, player_y, state, loading_screen, health, hunger, extra_health, time, chunks, pos
    if save:
        try:
            if not ("__" in save[1] and "!" in save[1] and ";" in save[1]):
                raise ValueError()
            save_path = save[0]
            data_save = save[1].split("__")

            plr = data_save[0].split(",")
            player_x, player_y = float(plr[0])*BLOCK_SIZE, float(plr[1])*BLOCK_SIZE-2
            health, hunger, extra_health, time = int(plr[2]), int(plr[3]), int(plr[4]), int(plr[5])
            progress = 0.25
            loading_screen(progress)

            if len(data_save[1]) > 0:
                inv = list(data_save[1].split(";"))
                for num, i in enumerate(inv):
                    if i != "":
                        item = i.split(',')[0]
                        count = int(i.split(',')[1])
                        if count > 0:
                            inventory[num] = [item, count]
                        progress += (1/4)/36
                        loading_screen(progress)
            progress = 0.5
            loading_screen(progress)

            if len(data_save[2]) > 0:
                chunk_data = data_save[2].split("!")
                current_chunk = None
                batch_size = 1000

                for i in range(0, len(chunk_data), batch_size):
                    batch = chunk_data[i:i + batch_size]
                    for entry in batch:
                        if entry == "":
                            continue

                        if entry.isdigit() or (entry.startswith("-") and entry[1:].isdigit()):
                            current_chunk = int(entry)
                            if current_chunk not in chunks:
                                chunks[current_chunk] = [[], []]
                        else:
                            ablocks = entry.split(";")
                            for b in ablocks:
                                if b:
                                    type = b.split(',')[0]
                                    posx = float(b.split(',')[1])
                                    posy = float(b.split(',')[2])

                                    new_block = Block(posx * BLOCK_SIZE, posy * BLOCK_SIZE, type)
                                    chunks[current_chunk][0].append(new_block)
                                    chunks[current_chunk][1].append((posx * BLOCK_SIZE, posy * BLOCK_SIZE))
                        
            progress = 0.75
            loading_screen(progress)
                
            if len(data_save[3]) > 0:
                chunk_data = data_save[3].split("!")
                current_chunk = None

                for i in range(0, len(chunk_data), batch_size):
                    batch = chunk_data[i:i + batch_size]
                    for entry in batch:
                        if entry == "":
                            continue

                        if entry.isdigit() or (entry.startswith("-") and entry[1:].isdigit()):
                            current_chunk = int(entry)
                            if current_chunk not in chunks:
                                chunks[current_chunk] = [[], []]
                        else:
                            ablocks = entry.split(";")
                            for b in ablocks:
                                if b:
                                    type = b.split(',')[0]
                                    posx = float(b.split(',')[1])
                                    posy = float(b.split(',')[2])

                                    new_block = Block(posx * BLOCK_SIZE, posy * BLOCK_SIZE, type, collide=False)
                                    chunks[current_chunk][0].append(new_block)
                                    chunks[current_chunk][1].append((posx * BLOCK_SIZE, posy * BLOCK_SIZE))
                        
            progress = 1
            loading_screen(progress)
            state = "game"
        except:
            save = None
            save_path = None
            player_x, player_y = 0, -BLOCK_SIZE*4
            health, hunger, extra_health, time = 20, 20, 0, 0
            progress = 0
            chunks = {}
            inventory = [[None, 0]]*36
            txt = "ERROR file is damaged. Generating new"
            stateload(-1)
            stateload(0)
            stateload(1)
            state = "game"
    if not save:
        WORLD_HEIGHT = 96
        BEDROCK_Y = -BLOCK_SIZE*64
        WORLD_LEFT_X = CHUNK*(BLOCK_SIZE*WORLD_WIDTH)-WORLD_WIDTH//2*BLOCK_SIZE
        WORLD_RIGHT_X = (CHUNK+1)*BLOCK_SIZE*WORLD_WIDTH-WORLD_WIDTH//2*BLOCK_SIZE

        if not flat_world[0]:
            scale = 50
            octaves = 4
            persistence = 0.5 
            lacunarity = 2.0

            sand_biomes = []
            mountain_biomes = []
            water_biomes = []
            for _ in range(random.randint(WORLD_WIDTH//300, WORLD_WIDTH//100)):
                start = random.randint(WORLD_LEFT_X//BLOCK_SIZE, WORLD_RIGHT_X//BLOCK_SIZE) * BLOCK_SIZE
                width = random.randint(10, 50) * BLOCK_SIZE
                sand_biomes.append((start, start + width))
            for _ in range(random.randint(WORLD_WIDTH//150, WORLD_WIDTH//75)):
                start = random.randint(WORLD_LEFT_X//BLOCK_SIZE, WORLD_RIGHT_X//BLOCK_SIZE) * BLOCK_SIZE
                width = random.randint(20, 40) * BLOCK_SIZE
                mountain_biomes.append((start, start + width))
            for _ in range(random.randint(WORLD_WIDTH // 200, WORLD_WIDTH // 100)):
                while True:
                    start = random.randint(WORLD_LEFT_X//BLOCK_SIZE, WORLD_RIGHT_X//BLOCK_SIZE) * BLOCK_SIZE
                    width = random.randint(15, 30) * BLOCK_SIZE
                    overlap = any(start <= end_m and start + width >= start_m for start_m, end_m in mountain_biomes)
                    if not overlap:
                        water_biomes.append((start, start + width))
                        break

            def is_mountain_biome(x):
                for start, end in mountain_biomes:
                    if start <= x <= end:
                        return True
                return False
            
            def is_sand_biome(x):
                for start, end in sand_biomes:
                    if start <= x <= end:
                        return True
                return False
            
            def is_water_biome(x):
                for start, end in water_biomes:
                    if start <= x <= end:
                        return True
                return False

            def calculate_mountain_height(x, start, end, peak_height):
                center = (start + end) // 2
                distance_from_center = abs(x - center)
                max_distance = (end - start) // 2
                height_modifier = max(0, peak_height - (peak_height * distance_from_center // max_distance))
                return height_modifier
            
            def calculate_water_depth(x, start, end, max_depth):
                center = (start + end) // 2
                distance_from_center = abs(x - center)
                max_distance = (end - start) // 2
                depth_modifier = max(0, max_depth - (max_depth * distance_from_center // max_distance))
                return -depth_modifier

            def generate_tree(x, ground_y):
                global platforms, pos
                tree_height = random.randint(3, 6)
                leaf_radius = random.randint(2, 3)

                for i in range(tree_height):
                    if not (x, ground_y - i * BLOCK_SIZE) in pos:
                        pos.append((x, ground_y - i * BLOCK_SIZE))
                        platforms.append(Block(x, ground_y - i * BLOCK_SIZE, "wood"))
                    else:
                        if platforms[pos.index((x, ground_y - i * BLOCK_SIZE))].type == "leaves":
                            platforms[pos.index((x, ground_y - i * BLOCK_SIZE))].type = "wood"

                leaf_top_y = ground_y - tree_height * BLOCK_SIZE
                for dx in range(-leaf_radius - 1, leaf_radius + 2):
                    for dy in range(-leaf_radius - 1, leaf_radius + 2):
                        distance = (dx**2 + dy**2)**0.5
                        if distance <= leaf_radius + random.uniform(-0.5, 0.5):
                            if random.random() < 0.9:
                                if not (x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE) in pos:
                                    platforms.append(Block(x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE, "leaves"))
                                    pos.append((x + dx * BLOCK_SIZE, leaf_top_y + dy * BLOCK_SIZE))

            def generate_vein(start_x, start_y, ore_type, vein_size):
                global platforms, pos
                    
                vein_blocks = []
                visited = set()
                    
                def is_valid(x, y):
                    return (x, y) not in visited
                    
                def get_neighbors(x, y):
                    neighbors = [
                        (x + BLOCK_SIZE, y),
                        (x - BLOCK_SIZE, y),
                        (x, y + BLOCK_SIZE),
                        (x, y - BLOCK_SIZE)
                    ]
                    return [pos for pos in neighbors if is_valid(*pos)]

                current_blocks = [(start_x, start_y)]
                visited.add((start_x, start_y))
                
                while len(vein_blocks) < vein_size and current_blocks:
                    block = random.choice(current_blocks)
                    neighbors = get_neighbors(*block)
                        
                    if neighbors:
                        new_block = random.choice(neighbors)
                        vein_blocks.append(new_block)
                        visited.add(new_block)
                        current_blocks.append(new_block)
                    else:
                        current_blocks.remove(block)

                for new_block in vein_blocks:
                    if new_block not in pos:
                        platforms.append(Block(new_block[0], new_block[1], ore_type))
                        pos.append(new_block)
                    elif platforms[pos.index(new_block)].type == "stone":
                        platforms[pos.index(new_block)].type = ore_type
            
            def generate_caves():
                global platforms, pos, progress
                cave_radius = 1

                progress_add = (1/3) / (WORLD_WIDTH+20)

                for _ in range(WORLD_WIDTH//15):
                    start_x = random.randint(WORLD_LEFT_X, WORLD_RIGHT_X)//BLOCK_SIZE * BLOCK_SIZE
                    start_y = random.randint(-60, -25) * BLOCK_SIZE

                    angle = random.uniform(0, 2 * pi)
                    horizontal_bias = 0.6

                    for _ in range(random.randint(15, 50)):
                        x = start_x + cos(angle) * BLOCK_SIZE
                        y = start_y + sin(angle) * BLOCK_SIZE

                        for dx in range(-cave_radius, cave_radius + 1):
                            for dy in range(-cave_radius, cave_radius + 1):
                                distance = sqrt(dx**2 + dy**2)
                                if distance <= cave_radius:
                                    cave_x = round(x + dx * BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE
                                    cave_y = round(y + dy * BLOCK_SIZE) // BLOCK_SIZE * BLOCK_SIZE

                                    if (cave_x, -cave_y) in pos:
                                        idx = pos.index((cave_x, -cave_y))
                                        if platforms[idx].type != "bedrock":
                                            del platforms[idx]
                                            del pos[idx]
                        angle_change = random.uniform(-pi / 8, pi / 8)
                        if random.random() < horizontal_bias:
                            angle_change = random.uniform(-pi / 12, pi / 12)
                        angle += angle_change
                        start_x, start_y = x, y

                    progress += progress_add
                    loading_screen(progress)
                for x in range(WORLD_LEFT_X//BLOCK_SIZE, WORLD_RIGHT_X//BLOCK_SIZE):
                    for y in range(-60, -20):
                        if random.random() <= 0.0025:
                            water_x = x * BLOCK_SIZE
                            water_y = -(y * BLOCK_SIZE)

                            neighbors = [
                                (water_x + BLOCK_SIZE, water_y),
                                (water_x - BLOCK_SIZE, water_y),
                                (water_x, water_y + BLOCK_SIZE)
                            ]

                            if any(neighbor not in pos for neighbor in neighbors):
                                pos.append((water_x, water_y))
                                platforms.append(Block(water_x, water_y, "water", collide=False))
                        elif random.random() <= 0.0085:
                            lava_x = x * BLOCK_SIZE
                            lava_y = -(y * BLOCK_SIZE)

                            neighbors = [
                                (lava_x + BLOCK_SIZE, lava_y),
                                (lava_x - BLOCK_SIZE, lava_y),
                                (lava_x, lava_y + BLOCK_SIZE)
                            ]

                            if any(neighbor not in pos for neighbor in neighbors):
                                pos.append((lava_x, lava_y))
                                platforms.append(Block(lava_x, lava_y, "lava", collide=False))

            progress_add = (1/3)/(WORLD_WIDTH+20)
            water = False
            water_accept = True
            for x in range(WORLD_WIDTH):
                block_x = WORLD_LEFT_X + x * BLOCK_SIZE

                mountain_biome = is_mountain_biome(block_x)
                sand_biome = is_sand_biome(block_x)
                water_biome = is_water_biome(block_x)

                base_height = int(noise.pnoise1(
                    x / scale, octaves=octaves,
                    persistence=persistence, lacunarity=lacunarity
                ) * 20)

                if mountain_biome:
                    for start, end in mountain_biomes:
                        if start <= block_x <= end:
                            mountain_height = calculate_mountain_height(block_x, start, end, peak_height=random.randint(8, 12))
                            base_height += mountain_height
                            break
                elif water_biome:
                    for start, end in water_biomes:
                        if start <= block_x <= end:
                            water_depth = calculate_water_depth(block_x, start, end, max_depth=random.randint(4, 8))
                            base_height += water_depth
                            break
                
                height = min(max(base_height, -10), 32)
                ground_y = height * BLOCK_SIZE

                if ground_y <= 0 and water_accept:
                    water = (random.random() < 0.25)
                    water_accept = False
                if ground_y > 0:
                    water = False
                    water_accept = True

                for y in range(WORLD_HEIGHT):
                    block_y = BEDROCK_Y + y * BLOCK_SIZE

                    if block_y < ground_y - BLOCK_SIZE * random.randint(3, 4):
                        if not sand_biome:
                            block_type = "stone" 
                        else:
                            block_type = "sandstone" if block_y > ground_y - BLOCK_SIZE * random.randint(9, 10) else "stone"
                    elif block_y < ground_y - BLOCK_SIZE:
                        block_type = "dirt" if not sand_biome else "sand"
                    elif block_y < ground_y:
                        block_type = "grass" if not (sand_biome or water) else "sand"
                    elif block_y < 0 and water:
                        block_type = "water"
                    else:   
                        continue
                    
                    collide = True
                    if "liquid" in blocks[block_type]:
                        collide = False
                    if block_y != -3200:
                        if not (block_x, -block_y) in pos:
                            platforms.append(Block(block_x, -block_y, block_type, collide=collide))
                            pos.append((block_x, -block_y))
                            
                        if block_type == "stone":
                            if block_y > BEDROCK_Y + BLOCK_SIZE * 30 and random.random() < 0.01:
                                generate_vein(block_x, -block_y, "coal_ore", random.randint(4, 7))
                            elif BEDROCK_Y + BLOCK_SIZE * 48 >= block_y > BEDROCK_Y and random.random() < 0.0075:
                                generate_vein(block_x, -block_y, "iron_ore", random.randint(3, 6))
                            elif BEDROCK_Y + BLOCK_SIZE * 32 >= block_y > BEDROCK_Y and random.random() < 0.0075:
                                generate_vein(block_x, -block_y, "gold_ore", random.randint(2, 5))
                            elif BEDROCK_Y + BLOCK_SIZE * 16 >= block_y > BEDROCK_Y and random.random() < 0.0025:
                                generate_vein(block_x, -block_y, "diamond_ore", random.randint(1, 4))
                            elif BEDROCK_Y + BLOCK_SIZE * 45 >= block_y > BEDROCK_Y and height > 10 and random.random() < 0.0025:
                                generate_vein(block_x, -block_y, "emerald_ore", 1)
                            elif BEDROCK_Y + BLOCK_SIZE * 30 >= block_y > BEDROCK_Y and random.random() < 0.005:
                                generate_vein(block_x, -block_y, "redstone_ore", random.randint(4, 6))
                            elif BEDROCK_Y + BLOCK_SIZE * 16 >= block_y > BEDROCK_Y and random.random() < 0.005:
                                generate_vein(block_x, -block_y, "lapis_ore", random.randint(2, 4))
                            elif BEDROCK_Y + BLOCK_SIZE * 64 >= block_y > BEDROCK_Y and random.random() < 0.015:
                                generate_vein(block_x, -block_y, "andesite", random.randint(3, 8))
                            elif BEDROCK_Y + BLOCK_SIZE * 64 >= block_y > BEDROCK_Y and random.random() < 0.015:
                                generate_vein(block_x, -block_y, "diorite", random.randint(3, 8))
                            elif BEDROCK_Y + BLOCK_SIZE * 64 >= block_y > BEDROCK_Y and random.random() < 0.015:
                                generate_vein(block_x, -block_y, "granite", random.randint(3, 8))
                            elif BEDROCK_Y + BLOCK_SIZE * 64 >= block_y > BEDROCK_Y and random.random() < 0.0025:
                                generate_vein(block_x, -block_y, "dirt", random.randint(5, 10))

                    if not (sand_biome or water) and random.random() < 0.1 and block_type == "grass" and (block_x <= -BLOCK_SIZE*5 or block_x >= BLOCK_SIZE*5):
                        generate_tree(block_x, -ground_y)

                progress += progress_add
                loading_screen(progress)

            generate_caves()

            for x in range(WORLD_WIDTH):
                block_x = WORLD_LEFT_X + x * BLOCK_SIZE
                block_y = BEDROCK_Y
                platforms.append(Block(block_x, -block_y, "bedrock"))
        else:
            for i in range(WORLD_LEFT_X//BLOCK_SIZE, WORLD_RIGHT_X//BLOCK_SIZE):
                platforms.append(Block(i*BLOCK_SIZE, 0, "grass"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*2, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*3, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*4, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*5, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*6, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*7, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*8, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*9, "dirt"))
                platforms.append(Block(i*BLOCK_SIZE, BLOCK_SIZE*10, "bedrock"))
        chunks[CHUNK] = [platforms.copy(), pos.copy()]
        platforms = []
        pos = []
        return None

def b_resume():
    global menu_open
    menu_open = False
def b_save():
    global chunks, inventory, player_x, player_y, save_path, health, hunger, extra_health, time
    
    if not save_path:
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return
        save_num = 1
        while os.path.exists(os.path.join(folder_selected, f"save{save_num}.mc2")):
            save_num += 1
        name = f"save{save_num}"
        filename = os.path.join(folder_selected, f"{name}.mc2")
    else:
        filename = os.path.join(save_path)
    
    with open(filename, "w") as file:
        file.write(f"{player_x/BLOCK_SIZE},{player_y/BLOCK_SIZE},{health},{hunger},{extra_health},{time}")
        file.write("__")
        for i in range(36):
            file.write(f"{inventory[i][0]},{inventory[i][1]};")
        file.write("__")
        default = f""
        uncollide = f""
        for num, chunk in chunks.items():
            default += f"!{num}!"
            uncollide += f"!{num}!"
            for p in chunk[0]:
                if p.collide:
                    default += f"{p.type},{p.x//BLOCK_SIZE},{p.y//BLOCK_SIZE};"
                else:
                    uncollide += f"{p.type},{p.x//BLOCK_SIZE},{p.y//BLOCK_SIZE};"
        file.write(f"{default}__{uncollide}")
def b_exit():
    global state, save, save_path, progress, platforms, inventory, pos, player_x, player_y, menu_open, dx, dy, chunks, cur_chunk, list_chunks, player_velocity_y, time, camera_fixation, on_ground, block_at_mouse, last_block_at_mouse, inventory_open, crafting_open, button_rects, crafting_base_count, crafting_base, result_craft, dragging_item, original_slot, doubling_item, is_rain, rain_off, raindrops, all_time, rain_update, eating_update, health_update, time_update, sum_distance, red_timer, lava_damage_timer, game_tick, health, hunger, extra_health, time
    state = "menu"
    dx, dy = 0, 0
    menu_open = False
    save = None
    save_path = None
    health = 20
    hunger = 20
    extra_health = 0
    time = 0
    progress = 0
    platforms = []
    pos = []
    list_chunks = [-1, 0, 1]
    cur_chunk = None
    chunks = {}
    player_velocity_y = 0
    time = 0
    player_x, player_y = 0, -BLOCK_SIZE*4
    inventory = [[None, 0] for _ in range(36)]
    camera_fixation = True
    on_ground = False
    block_at_mouse = None
    last_block_at_mouse = None
    inventory_open = False
    crafting_open = False
    button_rects = []
    crafting_base_count = [0]*4
    crafting_base = [None]*4
    result_craft = [None, 0]
    dragging_item = None
    original_slot = None
    doubling_item = False
    is_rain = False
    rain_off = False
    raindrops = [{"x": random.randint(0, screen_width), "y": random.randint(0, screen_height)} for _ in range(screen_width//4)]
    all_time = 0
    rain_update = [0, 0]
    eating_update = 0
    health_update = 0
    time_update = 0
    sum_distance = 0
    red_timer = 0
    lava_damage_timer = 0
    game_tick = 1000

def b2_exit():
    global running
    running = False
def b2_play():
    global play_open
    play_open = True
def b2_controls():
    global controls_open, settings_open
    controls_open = True
    settings_open = False
def b2_languages():
    global languages_open, settings_open
    languages_open = True
    settings_open = False
def b2_sounds():
    global sounds_open, settings_open
    sounds_open = True
    settings_open = False

def b2_settings():
    global settings_open
    settings_open = True

progress = 0
list_chunks = [-1, 0, 1]
cur_chunk = None
chunks = {}
platforms = []
pos = []

def get_block_at(mouse=False):
    global platforms, mouse_pos
    if not mouse: mouse = mouse_pos
    for p in platforms:
        if p.collide:
            if p.platform.collidepoint(mouse):
                return p
    for p in platforms:
        if not p.collide:
            if p.platform.collidepoint(mouse):
                return p
    return None

def item_draw(x, y, type, count):
    if type is not None:
        item_type = type
        item_image_path = os.path.join(files_path, "images", f"{item_type}.png")
        if os.path.exists(item_image_path):
            item_image = pygame.image.load(item_image_path)
            item_image = pygame.transform.scale(item_image, (40, 40))
            screen.blit(item_image, (x + 5, y + 5))
        else:
            block_color = (255, 0, 255)
            pygame.draw.rect(screen, block_color, (x + 5, y + 5, 40, 40))

        if int(count) > 0:
            if item_type in items and items[item_type] is not None and "strength" in items[item_type]:
                percent = round(count/items[item_type]["strength"]*100)
                red = max(255 - int(percent * 2.55), 0)
                green = min(int(percent * 2.55), 255)
                color = (red, green, 0)
                if percent != 100:
                    pygame.draw.rect(screen, (0, 0, 0), (x + 5, y + 40, 40, 3))
                    filled_width = int(percent * 0.4)
                    pygame.draw.rect(screen, color, (x + 5, y + 40, filled_width, 3))
            else:
                if int(count) > 1:
                    font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
                    count_text = font.render(str(count), True, (255, 255, 255))
                    screen.blit(count_text, (x + 35 - count_text.get_width() // 2, y + 23))

def darken_surface(surface, factor):
    dark_surface = surface.copy()
    dark_surface.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    dark_surface.set_alpha(255-int(255 * (1 - factor)))
    return dark_surface

def key_to_name(key):
    return pygame.key.name(key).upper()

def adjust_image(image_path, target_width, target_height):
    original_image = pygame.image.load(image_path).convert_alpha()
    original_width, original_height = original_image.get_size()
    original_ratio = original_width / original_height
    target_ratio = target_width / target_height
    if target_ratio == original_ratio:
        return pygame.transform.scale(original_image, (target_width, target_height))
    new_width = int(original_height * target_ratio)
    strip_width = new_width // 2
    resized_image = pygame.Surface((target_width, target_height), pygame.SRCALPHA)
    left_strip = original_image.subsurface((0, 0, strip_width, original_height))
    right_strip = original_image.subsurface((original_width - strip_width, 0, strip_width, original_height))
    left_strip = pygame.transform.scale(left_strip, (target_width // 2, target_height))
    right_strip = pygame.transform.scale(right_strip, (target_width // 2, target_height))
    resized_image.blit(left_strip, (0, 0))
    resized_image.blit(right_strip, (target_width // 2, 0))

    return resized_image

def deal_damage(num):
    global red_timer, health, extra_health
    if extra_health > 0:
        extra_health -= num
        if extra_health < 0:
            health += extra_health
            extra_health = 0
    else:
        health -= num
    health = min(max(health, 0), 20)
    red_timer = pygame.time.get_ticks() + 300

def translate_game():
    global translated, translator, language
    text_to_translate = "\n".join(translated.keys())
    translator = GoogleTranslator(source='en', target=language)
    translated_text = translator.translate(text_to_translate)
    translated_texts = translated_text.split("\n")
    for original, new_text in zip(translated.keys(), translated_texts):
        translated[original] = new_text

translate_game()

camera_fixation = True
is_flying = False
jump_pressed = False
last_jump_time = 0
double_jump_delay = 300

on_ground = False
block_at_mouse = None
last_block_at_mouse = None
inventory_open = False
crafting_open = False
menu_open = False
button_rects = []

crafting_base_count = [0]*4
crafting_base = [None]*4
result_craft = [None, 0]

dragging_item = None
original_slot = None
doubling_item = False

is_rain = False
rain_off = False
raindrops = [{"x": random.randint(0, screen_width), "y": random.randint(0, screen_height)} for _ in range(screen_width//4)]
all_time = 0
rain_update = [0, 0, 0]
eating_update = 0
health_update = 0
splash_update = 0
time_update = 0
sum_distance = 0
x_distance = 0
red_timer = 0
lava_damage_timer = 0
game_tick = 1000

path = os.path.join(files_path, "images", "_sys_heart2.png")
gold_heart = pygame.image.load(path).convert_alpha()
for pix_x in range(gold_heart.get_width()):
    for pix_y in range(gold_heart.get_height()):
        color = gold_heart.get_at((pix_x, pix_y))
        r, g, b, a = color

        if r > g and r > b and a > 0:
            yellow_shade = (r, r * 0.8, 0, a)
            gold_heart.set_at((pix_x, pix_y), yellow_shade)

gold_heart = pygame.transform.scale(gold_heart, (18, 18))

for name in blocks.keys():
    if "liquid" in blocks[name]:
        continue
    path = os.path.join(files_path, "images", f"{name}.png")

    if os.path.exists(path):
        texture = pygame.image.load(path).convert_alpha()

        for pix_x in range(texture.get_width()):
            for pix_y in range(texture.get_height()):
                color = texture.get_at((pix_x, pix_y))
                r, g, b, a = color
                if a > 0:
                    darker_shade = (max(0, r * 0.65), max(0, g * 0.65), max(0, b * 0.65), a)
                    texture.set_at((pix_x, pix_y), darker_shade)

        texture = pygame.transform.scale(texture, (BLOCK_SIZE, BLOCK_SIZE))
        blocks[name]["back"] = texture

sound_path = os.path.join(files_path, "sounds", "background.mp3")
backmusic = pygame.mixer.Sound(sound_path)
backmusic.play(loops=-1)
backmusic.set_volume(0.5*vol_music)

lava_play = False
sound_path = os.path.join(files_path, "sounds", "lava.mp3")
lavasound = pygame.mixer.Sound(sound_path)
lavasound.play(loops=-1)
lavasound.set_volume(0.0)

water_play = False
sound_path = os.path.join(files_path, "sounds", "water.mp3")
watersound = pygame.mixer.Sound(sound_path)
watersound.play(loops=-1)
watersound.set_volume(0.0)

sound_path = os.path.join(files_path, "sounds", "rain1.wav")
rainsound = pygame.mixer.Sound(sound_path)
rainplay = False

eat = False
sound_path = os.path.join(files_path, "sounds", "splash1.mp3")
splashsound = pygame.mixer.Sound(sound_path)
splashplay = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == "menu":
            if waiting_for_key:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting_for_key = False
                    else:
                        current_key[0] = event.key
                        waiting_for_key = False
                continue
            if not any([controls_open, settings_open, play_open, languages_open, sounds_open]) and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(mbutton_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        button_function = list(mbuttons.values())[i]
                        button_function()
            elif controls_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(c_button_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        waiting_for_key = True
                        current_key = list(c_buttons.values())[i]
                        current_key_name = list(c_buttons.keys())[i]
                        break
                if exit_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    controls_open = False
                    b2_settings()
            elif settings_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(sbutton_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        button_function = list(sbuttons.values())[i]
                        button_function()
                if exit_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    settings_open = False
            elif languages_open and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, rect in enumerate(lbutton_rects):
                        if rect.collidepoint(mouse_pos) and 50 <= rect.y <= screen_height-150:
                            sound_path = os.path.join(files_path, "sounds", "click.mp3")
                            sound = pygame.mixer.Sound(sound_path)
                            sound.set_volume(vol_sound)
                            sound.play()
                            language = list(lbuttons.values())[i]
                            translate_game()
                    if exit_button_rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        languages_open = False
                        b2_settings()
            elif languages_open and event.type == pygame.MOUSEWHEEL:
                scroll += event.y*14
                scroll = max(min(scroll, 0), -(70*len(lbuttons)+70)+screen_height-150)
            elif sounds_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(msbutton_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        percent = (mouse_pos[0] - rect.left - 5) / (rect.width - 10)
                        percent = max(0, min(1, percent))
                        if i == 0:
                            vol_music = percent
                            backmusic.set_volume(0.25*vol_music)
                        elif i == 1:
                            vol_sound = percent
                        
                if exit_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    sounds_open = False
                    b2_settings()
            elif play_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(p_button_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        key = list(p_buttons.keys())[i]
                        p_buttons[key][0] = not p_buttons[key][0]
                if exit_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    play_open = False
                if generate_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    txt = "Generating"
                    state = "loading"
                    play_open = False
                    stateload(CHUNK=-1)
                    stateload(CHUNK=0)
                    e = stateload(CHUNK=1)
                    state = "game"
                if load_button_rect.collidepoint(mouse_pos):
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    file_path = filedialog.askopenfilename(filetypes=[("MC2 Files", "*.mc2")])
                    if file_path:
                        with open(file_path, 'r') as f:
                            file_content = f.read()
                        save = [file_path, file_content]
                        txt = "Loading"
                        state = "loading"
                        play_open = False
                        stateload()
        if state == "game":
            if event.type == pygame.KEYDOWN and not menu_open:
                if pygame.K_1 <= event.key <= pygame.K_9:
                    inv_num = event.key - pygame.K_1
                    eating_update = pygame.time.get_ticks()
                if event.key == WINDOW[0] and dragging_item is None:
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    if not crafting_open:
                        inventory_open = not inventory_open
                    crafting_open = False
                    if not inventory_open:
                        result_craft = (None, 0)
                        for i, atype in enumerate(crafting_base):
                            if atype is not None:
                                ind = 0
                                for a in range(36):
                                    if inventory[a][0] is None or (inventory[a][0] == atype and not (inventory[a][0] in items and items[inventory[a][0]] is not None and "strength" in items[inventory[a][0]])):
                                        ind = a
                                        break
                                inventory[ind] = [atype, inventory[ind][1] + crafting_base_count[i]]
                        crafting_base = [None]*4
                        crafting_base_count = [0]*4
                if event.key == MENU[0]:
                    sound_path = os.path.join(files_path, "sounds", "click.mp3")
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(vol_sound)
                    sound.play()
                    menu_open = True
                if event.key == pygame.K_t and creative_mode[0]:
                    block = input("Enter a block/item: ")
                    count = items.get(block, {}).get("strength", None) or 64
                    inventory[inv_num] = [block, count]
                if event.key == pygame.K_z and creative_mode[0]:
                    camera_fixation = not camera_fixation
            if menu_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        sound_path = os.path.join(files_path, "sounds", "click.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        button_function = list(buttons.values())[i]
                        button_function()
            if event.type == pygame.MOUSEBUTTONDOWN and not (inventory_open or menu_open or crafting_open): 
                if event.button == 3:
                    block = get_block_at()
                    if block:
                        if block.type == "crafting_table":
                            sound_path = os.path.join(files_path, "sounds", "click.mp3")
                            sound = pygame.mixer.Sound(sound_path)
                            sound.set_volume(vol_sound)
                            sound.play()
                            crafting_open = True
            if event.type == pygame.MOUSEBUTTONDOWN and (inventory_open or crafting_open or menu_open):
                if event.button == 1:
                    doubling_item = False
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    for i in range(36):
                        x = 8 + start_x + (i % 9) * 50 - 2 * (i % 9)
                        row = (i - 9) // 9 if i >= 9 else 0
                        y_offset = y - 175 + row * 50 - row * 2 if i >= 9 else y

                        slot_rect = pygame.Rect(x, y_offset, 50, 50)
                        if slot_rect.collidepoint(mouse_x, mouse_y):
                            if inventory[i][0] is not None:
                                dragging_item = i
                                original_slot = i
                            break
                    
                    if inventory_open:
                        for i in range(4):
                            x_a = 8 + start_x + (i % 2) * 50 - 2 * (i % 2) + 129
                            y_a = screen_height - 100 - 255 - (1 - i // 2) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if crafting_base[i] is not None:
                                    dragging_item = i + 100
                                    original_slot = i + 100
                                break
                    elif crafting_open:
                        for i in range(9):
                            x_a = 8 + start_x + (i % 3) * 50 - 2 * (i % 3) + 104
                            y_a = screen_height - 100 - 255 - (2 - i // 3) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if crafting_base[i] is not None:
                                    dragging_item = i + 100
                                    original_slot = i + 100
                                break
                    
                    if inventory_open:
                        x_b = 8 + start_x + 254
                        y_b = screen_height - 100 - 279
                        result_rect = pygame.Rect(x_b, y_b, 50, 50)
                        if result_rect.collidepoint(mouse_x, mouse_y):
                            if result_craft[0] is not None:
                                sound_path = os.path.join(files_path, "sounds", "click.mp3")
                                pygame.mixer.Sound(sound_path).play()
                                dragging_item = 110
                                original_slot = 110
                    elif crafting_open:
                        x_b = 8 + start_x + 279
                        y_b = screen_height - 100 - 303
                        result_rect = pygame.Rect(x_b, y_b, 50, 50)
                        if result_rect.collidepoint(mouse_x, mouse_y):
                            if result_craft[0] is not None:
                                sound_path = os.path.join(files_path, "sounds", "click.mp3")
                                sound = pygame.mixer.Sound(sound_path)
                                sound.set_volume(vol_sound)
                                sound.play()
                                dragging_item = 110
                                original_slot = 110
                elif event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for i in range(36):
                        x = 8 + start_x + (i % 9) * 50 - 2 * (i % 9)
                        row = (i - 9) // 9 if i >= 9 else 0
                        y_offset = y - 175 + row * 50 - row * 2 if i >= 9 else y

                        slot_rect = pygame.Rect(x, y_offset, 50, 50)
                        if slot_rect.collidepoint(mouse_x, mouse_y):
                            if inventory[i][0] is not None and inventory[i][1] > 1:
                                doubling_item = True
                                dragging_item = i
                                original_slot = i
                                split_count = inventory[i][1] // 2
                                inventory[i][1] -= split_count
                                temp_item = (inventory[i][0], split_count)
                            break
                    if inventory_open:
                        for i in range(4):
                            x_a = 8 + start_x + (i % 2) * 50 - 2 * (i % 2) + 129
                            y_a = screen_height - 100 - 255 - (1 - i // 2) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if crafting_base[i] is not None and crafting_base_count[i] > 1:
                                    doubling_item = True
                                    dragging_item = i + 100
                                    original_slot = i + 100
                                    split_count = crafting_base_count[i] // 2
                                    crafting_base_count[i] -= split_count
                                    temp_item = (crafting_base[i], split_count)
                                break
                    elif crafting_open:
                        for i in range(9):
                            x_a = 8 + start_x + (i % 3) * 50 - 2 * (i % 3) + 104
                            y_a = screen_height - 100 - 255 - (2 - i // 3) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if len(crafting_base) == 9 and crafting_base[i] is not None and crafting_base_count[i] > 1:
                                    doubling_item = True
                                    dragging_item = i + 100
                                    original_slot = i + 100
                                    split_count = crafting_base_count[i] // 2
                                    crafting_base_count[i] -= split_count
                                    temp_item = (crafting_base[i], split_count)
                                break
            if event.type == pygame.MOUSEBUTTONUP and dragging_item is not None and not menu_open:
                doubling_item = False
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    for i in range(36):
                        x = 8 + start_x + (i % 9) * 50 - 2 * (i % 9)
                        row = (i - 9) // 9 if i >= 9 else 0
                        y_offset = y - 175 + row * 50 - row * 2 if i >= 9 else y

                        slot_rect = pygame.Rect(x, y_offset, 50, 50)
                        if slot_rect.collidepoint(mouse_x, mouse_y):
                            if i == original_slot:
                                dragging_item = None
                                original_slot = None
                                break

                            if dragging_item < 100:
                                if inventory[i][0] == inventory[dragging_item][0] and not (inventory[i][0] in items and items[inventory[i][0]] is not None and "strength" in items[inventory[i][0]]):
                                    inventory[i][1] += inventory[dragging_item][1]
                                    inventory[dragging_item][0] = None
                                    inventory[dragging_item][1] = 0
                                else:
                                    inventory[i][0], inventory[dragging_item][0] = inventory[dragging_item][0], inventory[i][0]
                                    inventory[i][1], inventory[dragging_item][1] = inventory[dragging_item][1], inventory[i][1]

                            elif 100 <= dragging_item < 110:
                                craft_index = dragging_item - 100
                                if inventory[i][0] == crafting_base[craft_index] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                    inventory[i][1] += crafting_base_count[craft_index]
                                    crafting_base[craft_index] = None
                                    crafting_base_count[craft_index] = 0
                                else:
                                    inventory[i][0], crafting_base[craft_index] = crafting_base[craft_index], inventory[i][0]
                                    inventory[i][1], crafting_base_count[craft_index] = crafting_base_count[craft_index], inventory[i][1]

                            if dragging_item == 110:
                                if inventory[i][0] is None:
                                    inventory[i][0] = result_craft[0]
                                    inventory[i][1] = result_craft[1]
                                    result_craft = (None, 0)
                                elif result_craft[0] == inventory[i][0]:
                                    inventory[i][1] += result_craft[1]
                                    result_craft = (None, 0)
                                dragging_item = None
                                original_slot = None
                                for a, b in enumerate(crafting_base_count):
                                    if b > 0:
                                        crafting_base_count[a] = b - 1
                                        if b - 1 == 0:
                                            crafting_base[a] = None
                                break

                            dragging_item = None
                            original_slot = None
                            break
                    
                    if inventory_open:
                        for i in range(4):
                            x_a = 8 + start_x + (i % 2) * 50 - 2 * (i % 2) + 129
                            y_a = screen_height - 100 - 255 - (1 - i // 2) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if i == original_slot - 100:
                                    dragging_item = None
                                    original_slot = None
                                    break

                                if dragging_item < 100:
                                    if crafting_base[i] == inventory[dragging_item][0] and not (crafting_base[i] in items and items[crafting_base[i]] is not None and "strength" in items[crafting_base[i]]):
                                        crafting_base_count[i] += inventory[dragging_item][1]
                                        inventory[dragging_item][0] = None
                                        inventory[dragging_item][1] = 0
                                    else:
                                        crafting_base[i], inventory[dragging_item][0] = inventory[dragging_item][0], crafting_base[i]
                                        crafting_base_count[i], inventory[dragging_item][1] = inventory[dragging_item][1], crafting_base_count[i]

                                elif 100 <= dragging_item < 110:
                                    craft_index = dragging_item - 100
                                    if crafting_base[i] == crafting_base[craft_index] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                        crafting_base_count[i] += crafting_base_count[craft_index]
                                        crafting_base[craft_index] = None
                                        crafting_base_count[craft_index] = 0
                                    else:
                                        crafting_base[i], crafting_base[craft_index] = crafting_base[craft_index], crafting_base[i]
                                        crafting_base_count[i], crafting_base_count[craft_index] = crafting_base_count[craft_index], crafting_base_count[i]

                                dragging_item = None
                                original_slot = None
                                break
                    elif crafting_open:
                        for i in range(9):
                            x_a = 8 + start_x + (i % 3) * 50 - 2 * (i % 3) + 104
                            y_a = screen_height - 100 - 255 - (2 - i // 3) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if i == original_slot - 100:
                                    dragging_item = None
                                    original_slot = None
                                    break

                                if dragging_item < 100:
                                    if crafting_base[i] == inventory[dragging_item][0] and not (crafting_base[i] in items and items[crafting_base[i]] is not None and "strength" in items[crafting_base[i]]):
                                        crafting_base_count[i] += inventory[dragging_item][1]
                                        inventory[dragging_item][0] = None
                                        inventory[dragging_item][1] = 0
                                    else:
                                        crafting_base[i], inventory[dragging_item][0] = inventory[dragging_item][0], crafting_base[i]
                                        crafting_base_count[i], inventory[dragging_item][1] = inventory[dragging_item][1], crafting_base_count[i]

                                elif 100 <= dragging_item < 110:
                                    craft_index = dragging_item - 100
                                    if crafting_base[i] == crafting_base[craft_index] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                        crafting_base_count[i] += crafting_base_count[craft_index]
                                        crafting_base[craft_index] = None
                                        crafting_base_count[craft_index] = 0
                                    else:
                                        crafting_base[i], crafting_base[craft_index] = crafting_base[craft_index], crafting_base[i]
                                        crafting_base_count[i], crafting_base_count[craft_index] = crafting_base_count[craft_index], crafting_base_count[i]

                                dragging_item = None
                                original_slot = None
                                break

                    if dragging_item == 110:
                        for i in range(36):
                            if inventory[i][0] is None:
                                inventory[i][0] = result_craft[0]
                                inventory[i][1] = result_craft[1]
                                result_craft = (None, 0)
                                break
                            elif result_craft[0] == inventory[i][0] and not (inventory[i][0] in items and items[inventory[i][0]] is not None and "strength" in items[inventory[i][0]]):
                                inventory[i][1] += result_craft[1]
                                result_craft = (None, 0)
                                break

                        for a, b in enumerate(crafting_base_count):
                            if b > 0:
                                crafting_base_count[a] = b - 1
                                if b - 1 == 0:
                                    crafting_base[a] = None

                    dragging_item = None
                elif event.button == 3:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    returned = False

                    for i in range(36):
                        x = 8 + start_x + (i % 9) * 50 - 2 * (i % 9)
                        row = (i - 9) // 9 if i >= 9 else 0
                        y_offset = y - 175 + row * 50 - row * 2 if i >= 9 else y

                        slot_rect = pygame.Rect(x, y_offset, 50, 50)
                        if slot_rect.collidepoint(mouse_x, mouse_y):
                            if i == original_slot:
                                inventory[original_slot][1] += temp_item[1]
                                dragging_item = None
                                original_slot = None
                                returned = True
                                break

                            if dragging_item < 100:
                                if inventory[i][0] is None:
                                    inventory[i][0] = temp_item[0]
                                    inventory[i][1] = temp_item[1]
                                elif inventory[i][0] == temp_item[0] and not (inventory[i][0] in items and items[inventory[i][0]] is not None and "strength" in items[inventory[i][0]]):
                                    inventory[i][1] += temp_item[1]
                                else:
                                    inventory[original_slot][1] += temp_item[1]
                            returned = True
                            dragging_item = None
                            original_slot = None
                            break
                    
                    if inventory_open:
                        for i in range(4):
                            x_a = 8 + start_x + (i % 2) * 50 - 2 * (i % 2) + 129
                            y_a = screen_height - 100 - 255 - (1 - i // 2) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if i + 100 == original_slot:
                                    crafting_base_count[original_slot - 100] += temp_item[1]
                                    dragging_item = None
                                    original_slot = None
                                    returned = True
                                    break

                                if dragging_item < 100:
                                    if crafting_base[i] is None:
                                        crafting_base[i] = temp_item[0]
                                        crafting_base_count[i] = temp_item[1]
                                    elif crafting_base[i] == temp_item[0] and not (crafting_base[i] in items and items[crafting_base[i]] is not None and "strength" in items[crafting_base[i]]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        inventory[original_slot][1] += temp_item[1]
                                elif 100 <= dragging_item < 110:
                                    craft_index = dragging_item - 100
                                    if crafting_base[i] is None:
                                        crafting_base[i] = temp_item[0]
                                        crafting_base_count[i] = temp_item[1]
                                    elif crafting_base[i] == temp_item[0] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        crafting_base_count[craft_index] += temp_item[1]
                                returned = True
                                dragging_item = None
                                original_slot = None
                                break
                    elif crafting_open:
                        for i in range(9):
                            x_a = 8 + start_x + (i % 3) * 50 - 2 * (i % 3) + 104
                            y_a = screen_height - 100 - 255 - (2 - i // 3) * 48

                            slot_rect = pygame.Rect(x_a, y_a, 50, 50)
                            if slot_rect.collidepoint(mouse_x, mouse_y):
                                if i + 100 == original_slot:
                                    crafting_base_count[original_slot - 100] += temp_item[1]
                                    dragging_item = None
                                    original_slot = None
                                    returned = True
                                    break

                                if dragging_item < 100:
                                    if crafting_base[i] is None:
                                        crafting_base[i] = temp_item[0]
                                        crafting_base_count[i] = temp_item[1]
                                    elif crafting_base[i] == temp_item[0] and not (crafting_base[i] in items and items[crafting_base[i]] is not None and "strength" in items[crafting_base[i]]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        inventory[original_slot][1] += temp_item[1]
                                elif 100 <= dragging_item < 110:
                                    craft_index = dragging_item - 100
                                    if crafting_base[i] is None:
                                        crafting_base[i] = temp_item[0]
                                        crafting_base_count[i] = temp_item[1]
                                    elif crafting_base[i] == temp_item[0] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        crafting_base_count[craft_index] += temp_item[1]
                                returned = True
                                dragging_item = None
                                original_slot = None
                                break

                    if not returned:
                        if dragging_item < 100:
                            inventory[original_slot][1] += temp_item[1]
                        elif 100 <= dragging_item < 110:
                            crafting_base_count[original_slot - 100] += temp_item[1]
                        dragging_item = None
                        original_slot = None
            if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP) and (inventory_open or crafting_open or menu_open):
                if event.button == 1 or event.button == 3:
                    result_craft = (None, 0)
                    for i, c in craft.items():
                        a = c[0].copy()
                        if inventory_open:
                            if a[0] is None and a[1] is None and a[2] is None and a[5] is None and a[8] is None:
                                for index in sorted([0, 1, 2, 5, 8], reverse=True):
                                    a.pop(index)
                        if a == crafting_base:
                            if ".d" in i:
                                i = i.split('.')[0]
                            result_craft = (i, c[1])
                            break
    if state == "menu":
        screen.fill((135, 206, 235))
        if not any([play_open, settings_open, controls_open, languages_open, sounds_open]):
            mbuttons = {
                translated.get("Play", "Play"): b2_play, 
                translated.get("Settings", "Settings"): b2_settings, 
                translated.get("Exit", "Exit"): b2_exit,
            }
            camera_x = 0 - screen_width // 2 + player_width//2
            camera_y = -BLOCK_SIZE*3 - screen_height // 2 + player_height//2
            
            for p in menu_platforms:
                platform = p.platform
                image_path = os.path.join(files_path, "images", f"{p.type}.png")
                
                if os.path.exists(image_path):
                    texture = pygame.image.load(image_path)
                    texture = pygame.transform.scale(texture, (platform.width, platform.height))
                    screen.blit(texture, (platform.x - camera_x, platform.y - camera_y))
                else:
                    pygame.draw.rect(screen, (255, 0, 255), 
                                    (platform.x - camera_x, platform.y - camera_y, platform.width, platform.height))

            logo_path = os.path.join(files_path, "images", f"_sys_logo{VERSION.split("-")[0].lower()}.png")
            logo_image = pygame.image.load(logo_path)
            logo_image = pygame.transform.scale(logo_image, (1024, 284))
            screen.blit(logo_image, ((screen_width-1024)//2, 200))

            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            button_width = 400
            button_height = 50
            spacing = 20

            mbutton_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(mbuttons) * button_height + (len(mbuttons) - 1) * spacing
            start_y = (screen_height - total_height) // 2

            for i, text in enumerate(mbuttons.keys()):
                x = (screen_width - button_width) // 2
                y = start_y + i * (button_height + spacing) + 100
                mbutton_rects.append(pygame.Rect(x, y, button_width, button_height))
            for i, rect in enumerate(mbutton_rects):
                button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                button_image = adjust_image(button_image_path, 400, 50)
                screen.blit(button_image, (rect.x, rect.y))

                text = font.render(list(mbuttons.keys())[i], True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
        elif settings_open:
            screen.blit(background_image, (0, 0))
            sbuttons = {
                translated.get("Controls", "Controls"): b2_controls,
                translated.get("Languages", "Languages"): b2_languages,
                translated.get("Sounds", "Sounds"): b2_sounds,
            }
            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            button_width = 400
            button_height = 50
            spacing = 20

            sbutton_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(sbuttons) * button_height + (len(sbuttons) - 1) * spacing
            start_y = (screen_height - total_height) // 2

            for i, text in enumerate(sbuttons.keys()):
                x = (screen_width - button_width) // 2
                y = start_y + i * (button_height + spacing)
                sbutton_rects.append(pygame.Rect(x, y, button_width, button_height))
            for i, rect in enumerate(sbutton_rects):
                button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                button_image = adjust_image(button_image_path, 400, 50)
                screen.blit(button_image, (rect.x, rect.y))

                text = font.render(list(sbuttons.keys())[i], True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
        elif sounds_open:
            screen.blit(background_image, (0, 0))
            msbuttons = {
                translated.get("Music", "Music"): vol_music,
                translated.get("Sound effects", "Sound effects"): vol_sound,
            }
            font = pygame.font.Font(files_path + "/other/Minecraftia.ttf", 27)
            button_width = 400
            button_height = 15
            spacing = 125

            msbutton_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(msbuttons) * button_height + (len(msbuttons) - 1) * spacing
            start_y = (screen_height - total_height) // 2

            button_image_path = os.path.join(files_path, "images", "_sys_button.png")
            button_image = adjust_image(button_image_path, 30, 30)

            for i, text in enumerate(msbuttons.keys()):
                x = (screen_width - button_width) // 2
                y = start_y + i * (button_height + spacing)
                msbutton_rects.append(pygame.Rect(x, y, button_width, button_height))

            for i, rect in enumerate(msbutton_rects):
                pygame.draw.rect(screen, (0, 0, 0), rect)

                text_surface = font.render(list(msbuttons.keys())[i], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(rect.centerx, rect.top - 30))
                screen.blit(text_surface, text_rect)

                value = list(msbuttons.values())[i]
                button_x = rect.left + int(value * (rect.width - 30))
                button_y = rect.centery - 15
                
                screen.blit(button_image, (button_x, button_y))
        elif languages_open:
            screen.blit(background_image, (0, 0))
            lbuttons = {
                translated.get("Albanian", "Albanian"): "sq",
                translated.get("Belarusian", "Belarusian"): "be",
                translated.get("Bulgarian", "Bulgarian"): "bg",
                translated.get("Croatian", "Croatian"): "hr",
                translated.get("Czech", "Czech"): "cs",
                translated.get("Danish", "Danish"): "da",
                translated.get("Dutch", "Dutch"): "nl",
                translated.get("English", "English"): "en",
                translated.get("Estonian", "Estonian"): "et",
                translated.get("Finnish", "Finnish"): "fi",
                translated.get("French", "French"): "fr",
                translated.get("German", "German"): "de",
                translated.get("Greek", "Greek"): "el",
                translated.get("Hungarian", "Hungarian"): "hu",
                translated.get("Icelandic", "Icelandic"): "is",
                translated.get("Italian", "Italian"): "it",
                translated.get("Latvian", "Latvian"): "lv",
                translated.get("Lithuanian", "Lithuanian"): "lt",
                translated.get("Macedonian", "Macedonian"): "mk",
                translated.get("Norwegian", "Norwegian"): "no",
                translated.get("Polish", "Polish"): "pl",
                translated.get("Portuguese", "Portuguese"): "pt",
                translated.get("Romanian", "Romanian"): "ro",
                translated.get("Russian", "Russian"): "ru",
                translated.get("Serbian", "Serbian"): "sr",
                translated.get("Slovak", "Slovak"): "sk",
                translated.get("Slovenian", "Slovenian"): "sl",
                translated.get("Spanish", "Spanish"): "es",
                translated.get("Swedish", "Swedish"): "sv",
                translated.get("Turkish", "Turkish"): "tr",
                translated.get("Ukrainian", "Ukrainian"): "uk",
            }
            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            button_width = 400
            button_height = 50
            spacing = 20

            lbutton_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(lbuttons) * button_height + (len(lbuttons) - 1) * spacing
            start_y = 100

            for i, text in enumerate(lbuttons.keys()):
                x = (screen_width - button_width) // 2
                y = start_y + i * (button_height + spacing) + scroll
                lbutton_rects.append(pygame.Rect(x, y, button_width, button_height))
            for i, rect in enumerate(lbutton_rects):
                if 50 <= rect.y <= screen_height-150:
                    button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                    button_image = adjust_image(button_image_path, 400, 50)
                    screen.blit(button_image, (rect.x, rect.y))

                    text = font.render(list(lbuttons.keys())[i], True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
        elif controls_open:
            screen.blit(background_image, (0, 0))
            c_buttons = {
                translated.get("Left", "Left"): LEFT,
                translated.get("Right", "Right"): RIGHT,
                translated.get("Jump", "Jump"): JUMP,
                translated.get("Sneak", "Sneak"): SNEAK,
                translated.get("Run", "Run"): RUN,
                translated.get("Inventory", "Inventory"): WINDOW,
                translated.get("Background build", "Background build"): BACK_BUILD,
            }
            button_width = 300
            button_height = 50
            spacing = 20
            value_box_size = 150

            c_button_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(c_buttons) * button_height + (len(c_buttons) - 1) * spacing
            start_y = (screen_height - total_height) // 2
            for i, (text, value) in enumerate(c_buttons.items()):
                x = (screen_width - button_width - value_box_size - spacing) // 2
                y = start_y + i * (button_height + spacing)

                font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
                button_rect = pygame.Rect(x, y, button_width, button_height)
                button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                button_image = adjust_image(button_image_path, button_width, button_height)
                screen.blit(button_image, (x, y))

                button_text = font.render(text, True, (255, 255, 255))
                button_text_rect = button_text.get_rect(center=button_rect.center)
                screen.blit(button_text, button_text_rect)

                value_box_rect = pygame.Rect(x + button_width + spacing, y, value_box_size, button_height)
                value_box_image = adjust_image(button_image_path, value_box_size, button_height)
                screen.blit(value_box_image, (x + button_width + spacing, y))

                c_button_rects.append(value_box_rect)

                value_text = font.render(key_to_name(value[0]), True, (255, 255, 255))
                value_text_rect = value_text.get_rect(center=value_box_rect.center)
                screen.blit(value_text, value_text_rect)
        elif play_open:
            screen.blit(background_image, (0, 0))
            p_buttons = {
                translated.get("Creative mode", "Creative mode"): creative_mode,
                translated.get("Flat world", "Flat world"): flat_world,
                translated.get("Keep inventory", "Keep inventory"): keep_inventory,
                translated.get("Daylight cycle", "Daylight cycle"): daylight_cycle,
                translated.get("Weather cycle", "Weather cycle"): weather_cycle,
                translated.get("Mob spawning", "Mob spawning"): mob_spawning,
                translated.get("Mob loot", "Mob loot"): mob_loot,
            }
            button_width = 300
            button_height = 50
            spacing = 20
            value_box_size2 = 50

            p_button_rects = []
            screen_width, screen_height = screen.get_size()
            start_y = 250
            for i, (text, value) in enumerate(p_buttons.items()):
                x = (screen_width - button_width - value_box_size2 - spacing) // 2
                y = start_y + i * (button_height + spacing)

                font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
                button_rect = pygame.Rect(x, y, button_width, button_height)
                button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                button_image = adjust_image(button_image_path, button_width, button_height)
                screen.blit(button_image, (x, y))

                button_text = font.render(text, True, (255, 255, 255))
                button_text_rect = button_text.get_rect(center=button_rect.center)
                screen.blit(button_text, button_text_rect)
                
                value_box_rect = pygame.Rect(x + button_width + spacing, y, value_box_size2, button_height)
                value_box_image = adjust_image(button_image_path, value_box_size2, button_height)
                screen.blit(value_box_image, (x + button_width + spacing, y))

                p_button_rects.append(value_box_rect)

                value_text = font.render("X" if value[0] else " ", True, (255, 255, 255))
                value_text_rect = value_text.get_rect(center=value_box_rect.center)
                screen.blit(value_text, value_text_rect)
            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            generate_x = (screen_width - 400) // 2
            generate_y = screen_height - 140
            generate_button_rect = pygame.Rect(generate_x, generate_y, 400, 50)

            button_image_path = os.path.join(files_path, "images", "_sys_button.png")
            generate_image = adjust_image(button_image_path, 400, 50)
            screen.blit(generate_image, (generate_x, generate_y))

            generate_text = font.render(translated.get("Generate world", "Generate world"), True, (255, 255, 255))
            generate_text_rect = generate_text.get_rect(center=generate_button_rect.center)
            screen.blit(generate_text, generate_text_rect)

            load_x = (screen_width - 400) // 2
            load_y = screen_height - 210
            load_button_rect = pygame.Rect(load_x, load_y, 400, 50)

            load_image = adjust_image(button_image_path, 400, 50)
            screen.blit(load_image, (load_x, load_y))

            load_text = font.render(translated.get("Load world", "Load world"), True, (255, 255, 255))
            load_text_rect = load_text.get_rect(center=load_button_rect.center)
            screen.blit(load_text, load_text_rect)

        if any([controls_open, play_open, settings_open, languages_open, sounds_open]):
            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            exit_x = (screen_width - 200) // 2
            exit_y = screen_height - 70
            exit_button_rect = pygame.Rect(exit_x, exit_y, 200, 50)

            button_image_path = os.path.join(files_path, "images", "_sys_button.png")
            button_image = adjust_image(button_image_path, 200, 50)
            screen.blit(button_image, (exit_x, exit_y))

            exit_text = font.render(translated.get("Back", "Back"), True, (255, 255, 255))
            exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
            screen.blit(exit_text, exit_text_rect)
    elif state == "game":
        current_time = pygame.time.get_ticks()
        if daylight_cycle[0] and not menu_open:
            if current_time-time_update >= 50:
                time_update = current_time
                time = (time+1) % 24000
                all_time += 1
        if weather_cycle[0] and not menu_open:
            if all_time % 48000 == 0:
                is_rain = True
                rain_off = False
                raindrops = [{"x": random.randint(0, screen_width), "y": random.randint(0, screen_height)} for _ in range(screen_width//4)]
                rain_update = [all_time, random.randint(6000, 12000), current_time]
            elif all_time - rain_update[0] >= rain_update[1] and is_rain:
                is_rain = False
                rain_off = True

        COLORS = {
            0: (135, 206, 235),
            12000: (255, 94, 77),
            18000: (25, 25, 112),
            24000: (135, 206, 235)
        }
        keys = sorted(COLORS.keys())
        bg_color = (0, 0, 0)
        for i in range(len(keys) - 1):
            if keys[i] <= time < keys[i + 1]:
                t = (time - keys[i]) / (keys[i + 1] - keys[i])
                bg_color = tuple(int(COLORS[keys[i]][j] + (COLORS[keys[i + 1]][j] - COLORS[keys[i]][j]) * t) for j in range(3))
                break
        else:
            bg_color = COLORS[keys[-1]]
        screen.fill((bg_color))

        if cur_chunk == None:
            cur_chunk = 0
            platforms = []
            pos = []
            for c in list_chunks:
                platforms += chunks[c][0]
                pos += chunks[c][1]
        left = cur_chunk*(BLOCK_SIZE*200)-200//2*BLOCK_SIZE
        right = (cur_chunk+1)*BLOCK_SIZE*200-200//2*BLOCK_SIZE
        if not (left <= camera_x <= right):
            cur_chunk = int(((camera_x + screen_width // 2 - player_width//2) + (200 // 2) * BLOCK_SIZE) // (BLOCK_SIZE * 200))
            list_chunks = [cur_chunk - 1, cur_chunk, cur_chunk + 1]
            platforms = []
            pos = []
            for c in list_chunks:
                if not c in chunks:
                    e = stateload(CHUNK=c)
            for c in list_chunks:
                platforms += chunks[c][0]
                pos += chunks[c][1]

        old_height = player_height
        old_player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        keys = pygame.key.get_pressed()
        if not menu_open:
            if keys[SNEAK[0]]:
                if not is_flying:
                    player_speed = default_speed / speed_multiplier
                player_width, player_height = shift_width, shift_height
            elif keys[RUN[0]] and hunger > 6:
                player_speed = default_speed * speed_multiplier
                player_width, player_height = default_width, default_height
            else:
                player_speed = default_speed
                player_width, player_height = default_width, default_height

        player_y += old_height - player_height

        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        
        ignore = []
        visible_platforms = [
            p for p in platforms
            if (
                p.platform.x + p.platform.width > camera_x and
                p.platform.x < camera_x + screen_width and
                p.platform.y + p.platform.height > camera_y and
                p.platform.y < camera_y + screen_height
            )
        ]
        for p in visible_platforms:
            if p.type == "lava":
                lava_play = True
            if p.type == "water":
                water_play = True
            platform = p.platform
            if "physics" in blocks[p.type]:
                is_supported = any(
                    other.platform.y == platform.y + platform.height and 
                    other.platform.x < platform.x + platform.width and 
                    other.platform.x + other.platform.width > platform.x
                    for other in visible_platforms
                ) or ((platform.y + BLOCK_SIZE >= camera_y + screen_height) and platform.y % BLOCK_SIZE == 0)
                if not is_supported:
                    platform.y += BLOCK_SIZE / 3
                    p.y += BLOCK_SIZE / 3
            if player_rect.colliderect(platform) and p.collide:
                ignore.append(p)
                if old_player_rect.bottom <= platform.top:
                    player_y = platform.top - player_height
                elif old_player_rect.top >= platform.bottom:
                    player_y = platform.bottom
                elif old_player_rect.right <= platform.left: 
                    player_x = platform.left - player_width
                elif old_player_rect.left >= platform.right:
                    player_x = platform.right
                break
        if lava_play: lavasound.set_volume(1.0*vol_sound)
        else: lavasound.set_volume(0.0)
        if water_play: watersound.set_volume(1.0*vol_sound)
        else: watersound.set_volume(0.0)

        dx, dy = 0, 0
        if not menu_open:
            if keys[LEFT[0]]:
                dx -= player_speed
            if keys[RIGHT[0]]:
                dx += player_speed
            if (keys[LEFT[0]] or keys[RIGHT[0]]) and not in_liquid:
                for p in visible_platforms:
                    platform = p.platform
                    if p.collide:
                        if pygame.Rect(player_x + dx, player_y+5, player_width, player_height).colliderect(platform) and platform.y >= player_rect.bottom and x_distance >= BLOCK_SIZE:
                            if p.type in blocks:
                                if "sound" in blocks[p.type] and blocks[p.type]["sound"][1] != None:
                                    sound = blocks[p.type]["sound"][1] + str(random.randint(1, 4))
                                    sound_path = os.path.join(files_path, "sounds", "step", f"{sound}.ogg")
                                    sound = pygame.mixer.Sound(sound_path)
                                    sound.set_volume(vol_sound)
                                    sound.play()
                                    walking_update = current_time
                                    x_distance -= BLOCK_SIZE
                                    break

            if keys[SNEAK[0]] and (keys[LEFT[0]] or keys[RIGHT[0]]) and not keys[JUMP[0]] and not is_flying:
                temp_rect = pygame.Rect(player_x + dx, player_y+5, player_width, player_height)
                can_move = False

                for p in visible_platforms:
                    platform = p.platform
                    if temp_rect.colliderect(platform) and player_y<=p.y and p not in ignore and p.collide:
                        can_move = True
                        break

                if not can_move:
                    dx = 0

            if keys[JUMP[0]]:
                if creative_mode[0]:
                    if not jump_pressed:
                        jump_pressed = True
                        if current_time - last_jump_time <= double_jump_delay:
                            is_flying = not is_flying
                            player_velocity_y = 0
                        last_jump_time = current_time
                if on_ground and not is_flying:
                    player_velocity_y = player_jump_speed
                    on_ground = False
            else:
                jump_pressed = False

        in_liquid = False
        dealed_damage = False
        for p in visible_platforms:
            platform = p.platform
            if not p.collide and "liquid" in blocks[p.type] and player_rect.colliderect(platform):
                in_liquid = p.type
                if p.type == "lava":
                    dealed_damage = True
                break
        if in_liquid:
            if not is_flying:
                if keys[SNEAK[0]]:
                    player_velocity_y += gravity 
                else:
                    player_velocity_y += gravity / 3
                if keys[JUMP[0]]:
                    player_velocity_y = -gravity * 5
            if (not splashplay or current_time - splash_update >= 3000) and (keys[LEFT[0]] or keys[RIGHT[0]]) and in_liquid == "water":
                number = random.randint(1, 2)
                sound_path = os.path.join(files_path, "sounds", f"splash{number}.mp3")
                splashsound = pygame.mixer.Sound(sound_path)
                splashplay.set_volume(vol_sound)
                splashplay = splashsound.play()
                splash_update = current_time
        elif not menu_open:
            if is_flying and creative_mode[0]:
                if keys[JUMP[0]]:
                    player_velocity_y = +player_jump_speed
                elif keys[SNEAK[0]]:
                    player_velocity_y = -player_jump_speed
                else:
                    player_velocity_y = 0
            else:
                player_velocity_y += gravity
        dy += player_velocity_y
        if dealed_damage and not creative_mode[0]:
            current_time = pygame.time.get_ticks()
            if current_time >= lava_damage_timer:
                deal_damage(4)
                sound_path = os.path.join(files_path, "sounds", "hit.mp3")
                sound = pygame.mixer.Sound(sound_path)
                sound.set_volume(vol_sound)
                sound.play()
                lava_damage_timer = current_time + 750
            
        player_rect = pygame.Rect(player_x + dx, player_y, player_width, player_height)
        on_ground = False
        for p in visible_platforms:
            platform = p.platform
            if p.collide and player_rect.colliderect(platform) and p not in ignore:
                if dx > 0:
                    player_x = platform.left - player_width
                    dx = 0
                elif dx < 0:
                    player_x = platform.right
                    dx = 0

        player_rect = pygame.Rect(player_x, player_y + dy, player_width, player_height)
        for p in visible_platforms:
            platform = p.platform
            if p.collide and player_rect.colliderect(platform) and p not in ignore:
                if dy > 0:
                    if abs(player_velocity_y) > ((BLOCK_SIZE*3)*2*gravity)**(1/2) and not in_liquid:
                        damage = int(abs(((player_velocity_y) ** 2) / (2 * gravity)) // 50 - 3)
                        if not creative_mode[0]:
                            deal_damage(damage)
                        sound_path = os.path.join(files_path, "sounds", "fallbig.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                    elif abs(player_velocity_y) > gravity and not in_liquid:
                        sound_path = os.path.join(files_path, "sounds", "fallsmall.mp3")
                        fall = pygame.mixer.Sound(sound_path)
                        fall.play()
                        fall.set_volume(0.5*vol_sound)
                    player_y = platform.top - player_height
                    player_velocity_y = 0
                    dy = 0
                    on_ground = True
                elif dy < 0:
                    player_y = platform.bottom
                    player_velocity_y = 0
                    dy = 0

        if camera_fixation and not menu_open:
            player_x += dx
            player_y += dy

            x_distance += abs(dx)
            sum_distance += sqrt(dx**2+dy**2) * (1+int(keys[RUN[0]]))
            if sum_distance >= 80*BLOCK_SIZE and not creative_mode[0]:
                sum_distance -= 80*BLOCK_SIZE
                hunger -= 1
                hunger = max(hunger, 0)

        if player_y > -BEDROCK_Y or health == 0:
            player_x = 0
            player_y = -BLOCK_SIZE*4
            health = 20
            hunger = 20
            if not keep_inventory[0] and not creative_mode[0]:
                inventory = [[None, 0] for _ in range(36)]

        if camera_fixation:
            camera_x = player_x - screen_width // 2 + player_width//2
            camera_y = player_y - screen_height // 2 + player_height//2
        else:
            if keys[pygame.K_LEFT]:
                camera_x -= screen_height//30
            if keys[pygame.K_RIGHT]:
                camera_x += screen_height//30
            if keys[pygame.K_UP]:
                camera_y -= screen_height//30
            if keys[pygame.K_DOWN]:
                camera_y += screen_height//30

        player_image_path = os.path.join(files_path, "images", "steve.png")
        player_image = pygame.image.load(player_image_path)
        player_image = pygame.transform.scale(player_image, (player_width, player_height))

        if red_timer > current_time:
            red_overlay = pygame.Surface(player_image.get_size(), flags=pygame.SRCALPHA)
            red_overlay.fill((128, 0, 0))
            player_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        liquid_updating = []
        for p in reversed(visible_platforms):
            platform = p.platform
            if not p.collide:
                if "back" in blocks[p.type]:
                    darken = blocks[p.type]["back"]
                    screen.blit(darken, (platform.x - camera_x, platform.y - camera_y))
                    continue
                image_path = os.path.join(files_path, "images", f"{p.type}.png")
                
                if os.path.exists(image_path):
                    texture = pygame.image.load(image_path)
                    texture = pygame.transform.scale(texture, (platform.width, platform.height))
                    crop = round(p.liquidlevel * BLOCK_SIZE)
                    texture = texture.subsurface((0, crop, platform.width, texture.get_height() - crop))
                    screen.blit(texture, (platform.x - camera_x, platform.y - camera_y + crop))
                else:
                    pygame.draw.rect(screen, (255, 0, 255), 
                                    (platform.x - camera_x, platform.y - camera_y + round(p.liquidlevel*BLOCK_SIZE), platform.width, platform.height-round(p.liquidlevel*BLOCK_SIZE)))
                    
                if "liquid" in blocks[p.type]:
                    if current_time - blocks[p.type]["liquid"][1] >= blocks[p.type]["liquid"][0]*1000:
                        if not p.liquided:
                            p.liquid()
                        elif p.parent:
                            if not p.parent in platforms:
                                if p in platforms:
                                    platforms.remove(p)
                        if not p.type in liquid_updating:
                            liquid_updating.append(p.type)
                    
        for u in liquid_updating:
            blocks[u]["liquid"][1] = current_time

        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))
        
        for p in visible_platforms:
            platform = p.platform
            if p.collide:
                image_path = os.path.join(files_path, "images", f"{p.type}.png")
                
                if os.path.exists(image_path):
                    texture = pygame.image.load(image_path)
                    texture = pygame.transform.scale(texture, (platform.width, platform.height))
                    screen.blit(texture, (platform.x - camera_x, platform.y - camera_y))
                else:
                    pygame.draw.rect(screen, (255, 0, 255), 
                                    (platform.x - camera_x, platform.y - camera_y, platform.width, platform.height))

        if not menu_open:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            block_x = (mouse_x + camera_x) // BLOCK_SIZE * BLOCK_SIZE
            block_y = (mouse_y + camera_y) // BLOCK_SIZE * BLOCK_SIZE
            pygame.draw.rect(screen, (225, 225, 225), (block_x - camera_x, block_y - camera_y, BLOCK_SIZE, BLOCK_SIZE), 2)
            mouse_pos = (block_x, block_y)
            
            block_at_mouse = get_block_at()
            if last_block_at_mouse != block_at_mouse:
                if last_block_at_mouse is not None:
                    last_block_at_mouse.broke = False
                    last_block_at_mouse.breaktime = 0
                last_block_at_mouse = block_at_mouse

            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and not (inventory_open or crafting_open):
                if block_at_mouse is not None and (blocks[block_at_mouse.type]["break"] != float('inf') or creative_mode[0]):
                    btype = inventory[inv_num][0]
                    doubler=1
                    
                    for breaktool in mining.keys():
                        if btype is not None and breaktool in btype and sum([int(b in block_at_mouse.type) for b in mining[breaktool]]) > 0:
                            doubler = items[btype]["dig"]
                            break

                    block_at_mouse.broke = True
                    block_at_mouse.breaking(blocks[block_at_mouse.type]["break"]/doubler)

                    break_progress = min(block_at_mouse.breaktime / ((blocks[block_at_mouse.type]["break"]*2/doubler) * FPS), 1.0)
                    scale_factor = 1 + break_progress * 0.5
                    if not block_at_mouse.collide and not "liquid" in blocks[block_at_mouse.type]:
                        break_progress = min(block_at_mouse.breaktime / ((blocks[block_at_mouse.type]["break"]*2/doubler) * FPS)+0.25, 1.0)
                    block_width = block_height = BLOCK_SIZE * scale_factor

                    texturepath = os.path.join(files_path, "images", f"{block_at_mouse.type}.png")

                    if not os.path.exists(texturepath):
                        original_color = (255, 0, 255)

                        r = original_color[0] * (1 - break_progress)
                        g = original_color[1] * (1 - break_progress)
                        b = original_color[2] * (1 - break_progress)

                        color = (int(r), int(g), int(b))
                        pygame.draw.rect(screen, color, (block_x - camera_x - (block_width - BLOCK_SIZE) // 2, block_y - camera_y - (block_height - BLOCK_SIZE) // 2, block_width, block_height))
                    else:
                        texture = pygame.image.load(texturepath).convert_alpha()
                        texture = pygame.transform.scale(texture, (block_width, block_height))
                        darkened_texture = darken_surface(texture, break_progress)
                        screen.blit(texture, (block_x - camera_x - (block_width - BLOCK_SIZE) // 2, block_y - camera_y - (block_height - BLOCK_SIZE) // 2))
                        screen.blit(darkened_texture, (block_x - camera_x - (block_width - BLOCK_SIZE) // 2, block_y - camera_y - (block_height - BLOCK_SIZE) // 2))
            elif block_at_mouse is not None:
                block_at_mouse.broke = False
                block_at_mouse.breaktime = 0

            if mouse_buttons[2] and not (inventory_open or crafting_open):
                t = inventory[inv_num][0]
                if t is not None:
                    if t in items and "hunger" in items[t]:
                        if current_time - 120 <= eating_update <= current_time and (hunger < 20 or t == "golden_apple"):
                            sound_path = os.path.join(files_path, "sounds", "eating.mp3")
                            eat = pygame.mixer.Sound(sound_path)
                            eat.set_volume(vol_sound)
                            eat.play()
                        if current_time - eating_update >= 1600 and (hunger < 20 or t == "golden_apple"):
                            hunger += items[t]["hunger"]
                            hunger = min(hunger, 20)
                            inventory[inv_num][1] -= 1
                            if inventory[inv_num][1] <= 0:
                                inventory[inv_num][0] = None
                            if t == "golden_apple":
                                extra_health += 4
                            eating_update = current_time
                    elif t == "bucket":
                        if block_at_mouse and "liquid" in blocks[block_at_mouse.type] and block_at_mouse.parent is None:
                            ind = 0
                            for i, item in enumerate(inventory):
                                if item == [None, 0]:
                                    ind = i
                                    break
                            inventory[ind][0] = block_at_mouse.type + "_bucket"
                            inventory[inv_num][1] -= 1
                            if inventory[inv_num][1] <= 0:
                                inventory[inv_num][0] = None
                            if not block_at_mouse.collide:
                                platforms.remove(block_at_mouse)
                                block_up = get_block_at(mouse=(block_x, block_y-BLOCK_SIZE))
                                if block_up:
                                    block_up.liquided = False
                                try:
                                    chunks[cur_chunk][0].remove(block_at_mouse)
                                except: None
                    elif block_at_mouse is None or ("liquid" in blocks[block_at_mouse.type] and block_at_mouse.type != t and (block_at_mouse.type != items[t]["block"] if t in items and "block" in items[t] else True)) or (not block_at_mouse.collide and not "liquid" in blocks[block_at_mouse.type] and not keys[BACK_BUILD[0]]):
                        remain = None
                        if t in items and "block" in items[t]:
                            if "remain" in items[t]:
                                remain = items[t]["remain"]
                            t = items[t]["block"]
                        if t in blocks:
                            if not pygame.Rect(block_x, block_y, BLOCK_SIZE, BLOCK_SIZE).colliderect(player_rect) or keys[BACK_BUILD[0]]:
                                if "sound" in blocks[t] and blocks[t]["sound"][0] != None:
                                    sound = blocks[t]["sound"][0] + str(random.randint(1, 4))
                                    sound_path = os.path.join(files_path, "sounds", "dig", f"{sound}.ogg")
                                    sound = pygame.mixer.Sound(sound_path)
                                    sound.set_volume(vol_sound)
                                    sound.play()
                                if block_at_mouse is not None and "liquid" in blocks[block_at_mouse.type]:
                                    platforms.remove(block_at_mouse)
                                    try:
                                        chunks[cur_chunk][0].remove(block_at_mouse)
                                    except: None
                                if not "liquid" in blocks[t] and not keys[BACK_BUILD[0]]:
                                    new_block = Block(block_x, block_y, t)
                                else:
                                    new_block = Block(block_x, block_y, t, collide=False)
                                platforms.append(new_block)
                                pos.append((block_x, block_y))
                                chunks[cur_chunk][0].append(new_block)
                                chunks[cur_chunk][1].append((block_x, block_y))
                                block_up = get_block_at(mouse=(block_x, block_y-BLOCK_SIZE))
                                if block_up:
                                    block_up.liquided = False
                                inventory[inv_num][1] -= 1
                                if inventory[inv_num][1] <= 0:
                                    inventory[inv_num][0] = None
                                if remain:
                                    for i in range(36):
                                        if inventory[i][0] == None and inventory[i][1] == 0:
                                            inventory[i][0] = remain
                                            inventory[i][1] = 1
                                            break
            else:
                eating_update = current_time
                if eat:
                    eat.stop()

            if not creative_mode[0]:
                if hunger == 20 and health < 20:
                    if current_time - health_update >= game_tick:
                        health += 1
                        health = min(health, 20)
                        health_update = current_time
                elif hunger == 0:
                    if current_time - health_update >= game_tick:
                        deal_damage(1)
                        sound_path = os.path.join(files_path, "sounds", "hit.mp3")
                        sound = pygame.mixer.Sound(sound_path)
                        sound.set_volume(vol_sound)
                        sound.play()
                        health_update = current_time
                elif extra_health > 0:
                    if current_time - health_update >= 10000:
                        extra_health -= 2
                        extra_health = max(extra_health, 0)
                        health_update = current_time

        if is_rain or rain_off:
            if not rainplay or current_time - rain_update[2] >= 1000:
                number = random.randint(1, 4)
                sound_path = os.path.join(files_path, "sounds", f"rain{number}.wav")
                rainsound = pygame.mixer.Sound(sound_path)
                rainsound.set_volume(vol_sound)
                rainplay = rainsound.play()
                rain_update[2] = current_time
            for drop in raindrops:
                pygame.draw.line(screen, (193, 205, 217), (drop["x"], drop["y"]), (drop["x"], drop["y"] + screen_height//60), screen_width//400)
                drop["y"] += 50

                if drop["y"] > screen_height and is_rain:
                    drop["y"] = random.randint(0, screen_height//15)
                    drop["x"] = random.randint(0, screen_width)
            if rain_off:
                offing = True
                for drop in raindrops:
                    if drop["y"] < screen_height:
                        offing = False
                if offing:
                    rain_off = False

        inventory_width = 9 * 50
        y = screen_height - 100
        start_x = (screen_width - inventory_width) // 2
        
        if not creative_mode[0]:
            for i in range(10):
                x = 8 + start_x + 20*i
                y_offset = y - 20
                if health - i * 2 >= 2:
                    level = 2
                elif health - i * 2 == 1:
                    level = 1
                else:
                    level = 0
                path = os.path.join(files_path, "images", f"_sys_heart{level}.png")
                if os.path.exists(path):
                    item_image = pygame.image.load(path)
                    item_image = pygame.transform.scale(item_image, (18, 18))
                    screen.blit(item_image, (x, y_offset))
                else:
                    block_color = (255, 0, 255)
                    pygame.draw.rect(screen, block_color, (x, y_offset, 18, 18))

            for i in range(10):
                x = 8 + start_x + 416 - 20*i
                y_offset = y - 20
                if hunger - i * 2 >= 2:
                    level = 2
                elif hunger - i * 2 == 1:
                    level = 1
                else:
                    level = 0
                path = os.path.join(files_path, "images", f"_sys_hunger{level}.png")
                if os.path.exists(path):
                    item_image = pygame.image.load(path)
                    item_image = pygame.transform.scale(item_image, (18, 18))
                    screen.blit(item_image, (x, y_offset))
                else:
                    block_color = (255, 0, 255)
                    pygame.draw.rect(screen, block_color, (x, y_offset, 18, 18))
            
            for i in range(round(extra_health/2)):
                x = 8 + start_x + 20*(i%10)
                y_offset = y - 40 - 20*(i//10)
                screen.blit(gold_heart, (x, y_offset))

        if inventory_open or crafting_open:
            if inventory_open:
                pygame.draw.rect(screen, (192, 192, 192), (start_x - 5, y - 325, inventory_width + 10, 390), border_radius=15)
            elif crafting_open:
                pygame.draw.rect(screen, (192, 192, 192), (start_x - 5, y - 375, inventory_width + 10, 440), border_radius=15)
            for i in range(9, 36):
                x = 8 + start_x + (i % 9) * 50 - 2 * (i % 9)
                row = (i - 9) // 9
                y_offset = y - 175 + row * 50 - row*2

                transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                transparent_surface.fill((64, 64, 64, 128))
                screen.blit(transparent_surface, (x, y_offset))
                pygame.draw.rect(screen, (64, 64, 64), (x, y_offset, 50, 50), 2)
                if dragging_item != i or doubling_item:
                    item_draw(x, y_offset, inventory[i][0], inventory[i][1])
        
        if inventory_open:
            if len(crafting_base) != 4: crafting_base = [None]*4
            if len(crafting_base_count) != 4: crafting_base_count = [0]*4
            for i in range(4):
                x_a = 8 + start_x + (i % 2) * 50 - 2 * (i % 2) + 129
                y_a = y - 255 - (1 - i//2)*48

                transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                transparent_surface.fill((64, 64, 64, 128))
                screen.blit(transparent_surface, (x_a, y_a))
                pygame.draw.rect(screen, (64, 64, 64), (x_a, y_a, 50, 50), 2)

                if dragging_item != i+100 or doubling_item:
                    item_draw(x_a, y_a, crafting_base[i], crafting_base_count[i])
            x_b = 8 + start_x + 254
            y_b = y - 279

            transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            transparent_surface.fill((64, 64, 64, 128))
            screen.blit(transparent_surface, (x_b, y_b))
            pygame.draw.rect(screen, (64, 64, 64), (x_b, y_b, 50, 50), 2)

            if dragging_item != 110:
                item_draw(x_b, y_b, result_craft[0], result_craft[1])

        if crafting_open:
            if len(crafting_base) != 9: crafting_base = [None]*9
            if len(crafting_base_count) != 9: crafting_base_count = [0]*9
            for i in range(9):
                x_a = 8 + start_x + (i % 3) * 50 - 2 * (i % 3) + 104
                y_a = screen_height - 100 - 255 - (2 - i//3)*48

                transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
                transparent_surface.fill((64, 64, 64, 128))
                screen.blit(transparent_surface, (x_a, y_a))
                pygame.draw.rect(screen, (64, 64, 64), (x_a, y_a, 50, 50), 2)

                if dragging_item != i+100 or doubling_item:
                    item_draw(x_a, y_a, crafting_base[i], crafting_base_count[i])
            x_b = 8 + start_x + 279
            y_b = screen_height - 100 - 303

            transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            transparent_surface.fill((64, 64, 64, 128))
            screen.blit(transparent_surface, (x_b, y_b))
            pygame.draw.rect(screen, (64, 64, 64), (x_b, y_b, 50, 50), 2)

            if dragging_item != 110:
                item_draw(x_b, y_b, result_craft[0], result_craft[1])

        for i in range(9):
            x = 8 + start_x + i * 50 - 2 * i
            transparent_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            transparent_surface.fill((64, 64, 64, 128))
            screen.blit(transparent_surface, (x, y))
            pygame.draw.rect(screen, (64, 64, 64), (x, y, 50, 50), 2)

            if dragging_item != i or doubling_item:
                item_draw(x, y, inventory[i][0], inventory[i][1])

        pygame.draw.rect(screen, (225, 225, 225), (8 + start_x + inv_num * 50 - inv_num*2 -5, y-5, 60, 60), 5)

        if dragging_item is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if dragging_item < 100:
                item_type = inventory[dragging_item][0]
            else:
                if dragging_item == 110:
                    item_type = result_craft[0]
                else:
                    item_type = crafting_base[dragging_item-100]
            item_image_path = os.path.join(files_path, "images", f"{item_type}.png")
            if os.path.exists(item_image_path):
                item_image = pygame.image.load(item_image_path)
                item_image = pygame.transform.scale(item_image, (40, 40))
                screen.blit(item_image, (mouse_x - 20, mouse_y - 20))
            else:
                block_color = (255, 0, 255)
                pygame.draw.rect(screen, block_color, (mouse_x - 20, mouse_y - 20, 40, 40))

        if menu_open:
            buttons = {
                translated.get("Resume", "Resume"): b_resume, 
                translated.get("Save", "Save"): b_save, 
                translated.get("Exit", "Exit"): b_exit,
            }
            button_width = 400
            button_height = 50
            spacing = 20

            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))

            button_rects = []
            screen_width, screen_height = screen.get_size()
            total_height = len(buttons) * button_height + (len(buttons) - 1) * spacing
            start_y = (screen_height - total_height) // 2

            for i, text in enumerate(buttons.keys()):
                x = (screen_width - button_width) // 2
                y = start_y + i * (button_height + spacing)
                button_rects.append(pygame.Rect(x, y, button_width, button_height))
            for i, rect in enumerate(button_rects):
                button_image_path = os.path.join(files_path, "images", "_sys_button.png")
                button_image = adjust_image(button_image_path, button_width, button_height)
                screen.blit(button_image, (rect.x, rect.y))

                text = font.render(list(buttons.keys())[i], True, (255, 255, 255))
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

        lava_play = False
        water_play = False

    font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
    text = font.render(VERSION, True, (255, 255, 255))
    text_rect = text.get_rect(topleft=(5, 5))
    screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)
keys_to_save = {
    "language": language,
    "vol_music": vol_music,
    "vol_sound": vol_sound,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
    "JUMP": JUMP,
    "SNEAK": SNEAK,
    "RUN": RUN,
    "WINDOW": WINDOW,
    "BACK_BUILD": BACK_BUILD,
}
data_to_save = {}
for key, value in keys_to_save.items():
    if isinstance(value, list) and len(value) == 1 and hasattr(pygame, "key"):
        key_code_name = pygame.key.name(value[0])
        data_to_save[key] = key_code_name
    else:
        data_to_save[key] = value

with open(json_path, "w") as file:
    json.dump(data_to_save, file, indent=4)
    
pygame.quit()
