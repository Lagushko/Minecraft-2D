import random, noise, os
from math import sin, cos, sqrt, pi
from tkinter import filedialog
from settings import *

files_path = str(os.path.dirname(os.path.abspath(__file__)))
clock = pygame.time.Clock()
state = "menu"
FPS = 25

class Block:
    def __init__(self, x, y, type, parent=None, liquidlevel=0):
        self.x = x
        self.y = y
        self.type = type
        self.broke = False
        self.breaktime = 0
        self.platform = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)

        self.liquided = False
        self.liquidlevel = liquidlevel
        self.parent = parent
    def breaking(self, time):
        global mouse_pos, platforms, inv_counts, inv_items, inv_num
        if mouse_pos != (self.x, self.y):
            self.broke = False
            self.breaktime = 0
        if self.broke:
            self.breaktime += 1
        if self.breaktime >= time * FPS:
            if "drop" in blocks[self.type]:
                drop = blocks[self.type]["drop"]
            else:
                drop = self.type
            if "tools" in blocks[self.type]:
                tools = str(blocks[self.type]["tools"])
            else:
                tools = str(inv_items[inv_num])
            if "exc" in blocks[self.type]:
                exc = blocks[self.type]["exc"]
            else:
                exc = ""
            if self in platforms:
                platforms.remove(self)
            elif self in uncollide_plats:
                uncollide_plats.remove(self)
            blks = [get_block_at(mouse=(self.x, self.y-BLOCK_SIZE)), get_block_at(mouse=(self.x-BLOCK_SIZE, self.y)), get_block_at(mouse=(self.x+BLOCK_SIZE, self.y))]
            for b in blks:
                if b:
                    b.liquided = False
            self.broke = False
            if tools in str(inv_items[inv_num]) and not str(inv_items[inv_num]) in exc:
                if drop in inv_items:
                    inv_counts[inv_items.index(drop)] += 1
                else:
                    if inv_items.count(None) > 0:
                        ind = 0
                        for i, a in enumerate(inv_items):
                            if a == None:
                                ind = i
                                break
                        inv_items[ind] = drop
                        inv_counts[ind] = 1 if drop is not None else 0
            if inv_items[inv_num] is not None and (
                "_pickaxe" in inv_items[inv_num] or 
                "_axe" in inv_items[inv_num] or 
                "_shovel" in inv_items[inv_num] or
                "scissors" in inv_items[inv_num]):
                inv_counts[inv_num]-=1
                if inv_counts[inv_num] == 0:
                    inv_items[inv_num] = None
    
    def liquid(self):
        global platforms, uncollide_plats, uncollide_pos
        opp = ("water", "cobblestone", 3) if self.type == "lava" else ("lava", "obsidian", 7)
        block_down = get_block_at(mouse=(self.x, self.y+BLOCK_SIZE))
        block_left = get_block_at(mouse=(self.x-BLOCK_SIZE, self.y))
        block_right = get_block_at(mouse=(self.x+BLOCK_SIZE, self.y))
        for b in [block_down, block_left, block_right]:
            if b and b.type == opp[0]:
                if self.type == "lava": 
                    platforms.append(Block(self.x, self.y, opp[1]))
                    if self in uncollide_plats:
                        uncollide_plats.remove(self)
                    block_up = get_block_at(mouse=(self.x, self.y-BLOCK_SIZE))
                    if block_up:
                        block_up.liquided = False
                else:
                    platforms.append(Block(b.x, b.y, opp[1]))
                    if b in uncollide_plats:
                        uncollide_plats.remove(b)
                    block_up = get_block_at(mouse=(b.x, b.y-BLOCK_SIZE))
                    if block_up:
                        block_up.liquided = False
                return
            if b == block_down == None or (b and block_down and b == block_down and b.type == self.type):
                break
        
        if block_down and block_down.type != self.type:
            if self.liquidlevel < opp[2]/(opp[2]+1):
                if not block_left:
                    uncollide_plats.append(Block(self.x-BLOCK_SIZE, self.y, self.type, parent=self, liquidlevel=self.liquidlevel+1/(opp[2]+1)))
                if not block_right:
                    uncollide_plats.append(Block(self.x+BLOCK_SIZE, self.y, self.type, parent=self, liquidlevel=self.liquidlevel+1/(opp[2]+1)))
        elif not block_down:
            uncollide_plats.append(Block(self.x, self.y+BLOCK_SIZE, self.type, parent=self, liquidlevel=0))
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
    global menu_platforms, uncollide_plats, menu_pos
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

waiting_for_key = False
current_key = None
current_key_name = None

camera_x, camera_y = 0, 0
mouse_pos = (0, 0)

inv_counts = [0] * 36
inv_items = [None] * 36
inv_num = 0

background_path = os.path.join(files_path, "images", "_sys_loadbackground.png")
background_image = pygame.image.load(background_path)
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
txt = "Generating"

def loading_screen(progress):
    global screen
    screen.blit(background_image, (0, 0))

    font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
    text = font.render(VERSION, True, (255, 255, 255))
    text_rect = text.get_rect(topleft=(5, 5))
    screen.blit(text, text_rect)

    font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
    text = font.render(f"{txt} world...", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen_width//2, screen_height//2-50))
    screen.blit(text, text_rect)

    bar_x, bar_y, bar_width, bar_height = screen_width//4, screen_height//2, screen_width//2, 30
    border_radius = 15
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), border_radius=border_radius)

    fill_width = int(bar_width * progress)
    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=border_radius)

    pygame.display.flip()
def stateload():
    global save, save_path, progress, platforms, uncollide_plats, txt, inv_counts, inv_items, player_x, player_y, state, loading_screen
    if save:
        try:
            save_path = save[0]
            data_save = save[1].split("__")

            plr = data_save[0].split(",")
            player_x, player_y = float(plr[0])*BLOCK_SIZE, float(plr[1])*BLOCK_SIZE-2
            progress = 0.25
            loading_screen(progress)

            if len(data_save[1]) > 0:
                inv = list(data_save[1].split(";"))
                for num, i in enumerate(inv):
                    if i != "":
                        item = i.split(',')[0]
                        count = int(i.split(',')[1])
                        if count > 0:
                            inv_items[num] = item
                            inv_counts[num] = count
                        progress += (1/4)/36
                        loading_screen(progress)
            progress = 0.5
            loading_screen(progress)

            if len(data_save[2]) > 0:
                batch_size = 1000

                ablocks = data_save[2].split(";")
                total_ablocks = len(ablocks)

                for i in range(0, total_ablocks, batch_size):
                    batch = ablocks[i:i + batch_size]
                    for b in batch:
                        if b:
                            type = b.split(',')[0]
                            posx = float(b.split(',')[1])
                            posy = float(b.split(',')[2])
                            new_block = Block(posx * BLOCK_SIZE, posy * BLOCK_SIZE, type)
                            platforms.append(new_block)
                        
            progress = 0.75
            loading_screen(progress)
                
            if len(data_save[3]) > 0:
                batch_size = 1000

                unc_ablocks = data_save[3].split(";")
                unc_total_ablocks = len(unc_ablocks)

                for i in range(0, unc_total_ablocks, batch_size):
                    batch = unc_ablocks[i:i + batch_size]
                    for b in batch:
                        if b:
                            type = b.split(',')[0]
                            posx = float(b.split(',')[1])
                            posy = float(b.split(',')[2])
                            new_block = Block(posx * BLOCK_SIZE, posy * BLOCK_SIZE, type)
                            uncollide_plats.append(new_block)
                        
            progress = 1
            loading_screen(progress)
        except:
            save = None
            save_path = None
            progress = 0
            platforms = []
            uncollide_plats = []
            inv_counts = [0]*36
            inv_items = [None]*36
            txt = "ERROR file is damaged. Generating new"
    if not save:
        WORLD_WIDTH = 750
        WORLD_HEIGHT = 96
        BEDROCK_Y = -BLOCK_SIZE*64
        WORLD_LEFT_X = -BLOCK_SIZE * (WORLD_WIDTH // 2)
        WORLD_RIGHT_X = BLOCK_SIZE * (WORLD_WIDTH // 2)

        if not flat_world[0]:
            scale = 50
            octaves = 4
            persistence = 0.5 
            lacunarity = 2.0

            sand_biomes = []
            mountain_biomes = []
            water_biomes = []
            for _ in range(random.randint(WORLD_WIDTH//300, WORLD_WIDTH//100)):
                start = random.randint(-WORLD_WIDTH // 2, WORLD_WIDTH // 2) * BLOCK_SIZE
                width = random.randint(10, 50) * BLOCK_SIZE
                sand_biomes.append((start, start + width))
            for _ in range(random.randint(WORLD_WIDTH//150, WORLD_WIDTH//75)):
                start = random.randint(-WORLD_WIDTH // 2, WORLD_WIDTH // 2) * BLOCK_SIZE
                width = random.randint(20, 40) * BLOCK_SIZE
                mountain_biomes.append((start, start + width))
            for _ in range(random.randint(WORLD_WIDTH // 200, WORLD_WIDTH // 100)):
                while True:
                    start = random.randint(-WORLD_WIDTH // 2, WORLD_WIDTH // 2) * BLOCK_SIZE
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
                global platforms, uncollide_plats, pos
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

                progress_add = 1 / (WORLD_WIDTH+20)

                for _ in range(WORLD_WIDTH//15):
                    start_x = random.randint(-WORLD_WIDTH//2, WORLD_WIDTH//2) * BLOCK_SIZE
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
                for x in range(-WORLD_WIDTH//2, WORLD_WIDTH//2):
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
                                uncollide_plats.append(Block(water_x, water_y, "water"))
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
                                uncollide_plats.append(Block(lava_x, lava_y, "lava"))

            progress_add = 1/(WORLD_WIDTH+20)
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

                    if block_type in ["water", "lava"]:
                        if not (block_x, -block_y) in uncollide_pos and not (block_x, -block_y) in pos:
                            uncollide_plats.append(Block(block_x, -block_y, block_type))
                            uncollide_pos.append((block_x, -block_y))
                    elif block_y != -3200:
                        if not (block_x, -block_y) in pos and not (block_x, -block_y) in uncollide_pos:
                            platforms.append(Block(block_x, -block_y, block_type))
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
    state = "game"

def b_resume():
    global menu_open
    menu_open = False
def b_save():
    global platforms, inv_counts, inv_items, player_x, player_y, save_path
    
    print(save_path)
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
        file.write(f"{player_x},{player_y}")
        file.write("__")
        for i in range(36):
            file.write(f"{inv_items[i]},{inv_counts[i]};")
        file.write("__")
        for p in platforms:
            file.write(f"{p.type},{p.x//BLOCK_SIZE},{p.y//BLOCK_SIZE};")
        file.write("__")
        for p in uncollide_plats:
            file.write(f"{p.type},{p.x//BLOCK_SIZE},{p.y//BLOCK_SIZE};")
def b_exit():
    global state, save, save_path, progress, platforms, uncollide_plats, inv_counts, inv_items, pos, uncollide_pos, player_x, player_y, menu_open
    state = "menu"
    menu_open = False
    save = None
    save_path = None
    progress = 0
    platforms = []
    uncollide_plats = []
    pos = []
    uncollide_pos = []
    player_x, player_y = 0, -BLOCK_SIZE*4
    inv_counts = [0]*36
    inv_items = [None]*36
def b2_exit():
    global running
    running = False
def b2_play():
    global play_open
    play_open = True
def b2_controls():
    global controls_open
    controls_open = True

progress = 0
platforms = []
uncollide_plats = []
pos = []
uncollide_pos = []

def get_block_at(mouse=False):
    global platforms, uncollide_plats, mouse_pos
    if not mouse: mouse = mouse_pos
    for p in platforms:
        if p.platform.collidepoint(mouse):
            return p
    for p in uncollide_plats:
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

        if count > 0:
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
                if count > 1:
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

health_update = 0
red_timer = 0
lava_damage_timer = 0
game_tick = 1000

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
            if not play_open and not controls_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(mbutton_rects):
                    if rect.collidepoint(mouse_pos):
                        button_function = list(mbuttons.values())[i]
                        button_function()
            elif controls_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(c_button_rects):
                    if rect.collidepoint(mouse_pos):
                        waiting_for_key = True
                        current_key = list(c_buttons.values())[i]
                        current_key_name = list(c_buttons.keys())[i]
                        break
                if exit_button_rect.collidepoint(mouse_pos):
                    controls_open = False
            elif play_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(p_button_rects):
                    if rect.collidepoint(mouse_pos):
                        key = list(p_buttons.keys())[i]
                        p_buttons[key][0] = not p_buttons[key][0]
                if exit_button_rect.collidepoint(mouse_pos):
                    play_open = False
                if generate_button_rect.collidepoint(mouse_pos):
                    txt = "Generating"
                    state = "loading"
                    play_open = False
                    stateload()
                if load_button_rect.collidepoint(mouse_pos):
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
                if event.key == WINDOW[0] and dragging_item is None:
                    if not crafting_open:
                        inventory_open = not inventory_open
                    crafting_open = False
                    if not inventory_open:
                        result_craft = (None, 0)
                        for i, type in enumerate(crafting_base):
                            if type is not None:
                                ind = 0
                                for a in range(36):
                                    if inv_items[a] is None or (inv_items[a] == type and not (inv_items[a] in items and items[inv_items[a]] is not None and "strength" in items[inv_items[a]])):
                                        ind = a
                                        break
                                inv_items[ind] = type
                                inv_counts[ind] = inv_counts[ind] + crafting_base_count[i]
                        crafting_base = [None]*4
                        crafting_base_count = [0]*4
                if event.key == MENU[0]:
                    menu_open = True
                if event.key == pygame.K_t:
                    block = input("Enter a block: ")
                    inv_items[inv_num] = block
                    inv_counts[inv_num] = 1024
            if menu_open and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mouse_pos):
                        button_function = list(buttons.values())[i]
                        button_function()
            if event.type == pygame.MOUSEBUTTONDOWN and not (inventory_open or menu_open or crafting_open): 
                if event.button == 3:
                    block = get_block_at()
                    if block and block.type == "crafting_table":
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
                            if inv_items[i] is not None:
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
                                dragging_item = 110
                                original_slot = 110
                    elif crafting_open:
                        x_b = 8 + start_x + 279
                        y_b = screen_height - 100 - 303
                        result_rect = pygame.Rect(x_b, y_b, 50, 50)
                        if result_rect.collidepoint(mouse_x, mouse_y):
                            if result_craft[0] is not None:
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
                            if inv_items[i] is not None and inv_counts[i] > 1:
                                doubling_item = True
                                dragging_item = i
                                original_slot = i
                                split_count = inv_counts[i] // 2
                                inv_counts[i] -= split_count
                                temp_item = (inv_items[i], split_count)
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
                                if inv_items[i] == inv_items[dragging_item] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                    inv_counts[i] += inv_counts[dragging_item]
                                    inv_items[dragging_item] = None
                                    inv_counts[dragging_item] = 0
                                else:
                                    inv_items[i], inv_items[dragging_item] = inv_items[dragging_item], inv_items[i]
                                    inv_counts[i], inv_counts[dragging_item] = inv_counts[dragging_item], inv_counts[i]

                            elif 100 <= dragging_item < 110:
                                craft_index = dragging_item - 100
                                if inv_items[i] == crafting_base[craft_index] and not (crafting_base[craft_index] in items and items[crafting_base[craft_index]] is not None and "strength" in items[crafting_base[craft_index]]):
                                    inv_counts[i] += crafting_base_count[craft_index]
                                    crafting_base[craft_index] = None
                                    crafting_base_count[craft_index] = 0
                                else:
                                    inv_items[i], crafting_base[craft_index] = crafting_base[craft_index], inv_items[i]
                                    inv_counts[i], crafting_base_count[craft_index] = crafting_base_count[craft_index], inv_counts[i]

                            if dragging_item == 110:
                                if inv_items[i] is None:
                                    inv_items[i] = result_craft[0]
                                    inv_counts[i] = result_craft[1]
                                    result_craft = (None, 0)
                                elif result_craft[0] == inv_items[i]:
                                    inv_counts[i] += result_craft[1]
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
                                    if crafting_base[i] == inv_items[dragging_item] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                        crafting_base_count[i] += inv_counts[dragging_item]
                                        inv_items[dragging_item] = None
                                        inv_counts[dragging_item] = 0
                                    else:
                                        crafting_base[i], inv_items[dragging_item] = inv_items[dragging_item], crafting_base[i]
                                        crafting_base_count[i], inv_counts[dragging_item] = inv_counts[dragging_item], crafting_base_count[i]

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
                                    if crafting_base[i] == inv_items[dragging_item] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                        crafting_base_count[i] += inv_counts[dragging_item]
                                        inv_items[dragging_item] = None
                                        inv_counts[dragging_item] = 0
                                    else:
                                        crafting_base[i], inv_items[dragging_item] = inv_items[dragging_item], crafting_base[i]
                                        crafting_base_count[i], inv_counts[dragging_item] = inv_counts[dragging_item], crafting_base_count[i]

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
                            if inv_items[i] is None:
                                inv_items[i] = result_craft[0]
                                inv_counts[i] = result_craft[1]
                                result_craft = (None, 0)
                                break
                            elif result_craft[0] == inv_items[i] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                inv_counts[i] += result_craft[1]
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
                                inv_counts[original_slot] += temp_item[1]
                                dragging_item = None
                                original_slot = None
                                returned = True
                                break

                            if dragging_item < 100:
                                if inv_items[i] is None:
                                    inv_items[i] = temp_item[0]
                                    inv_counts[i] = temp_item[1]
                                elif inv_items[i] == temp_item[0] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                    inv_counts[i] += temp_item[1]
                                else:
                                    inv_counts[original_slot] += temp_item[1]
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
                                    elif crafting_base[i] == temp_item[0] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        inv_counts[original_slot] += temp_item[1]
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
                                    elif crafting_base[i] == temp_item[0] and not (item_type in items and items[item_type] is not None and "strength" in items[item_type]):
                                        crafting_base_count[i] += temp_item[1]
                                    else:
                                        inv_counts[original_slot] += temp_item[1]
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
                            inv_counts[original_slot] += temp_item[1]
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
                            result_craft = (i, c[1])
                            break
    if state == "menu":
        screen.fill((135, 206, 235))
        if not play_open and not controls_open:
            mbuttons = {
                'Play': b2_play, 
                'Controls': b2_controls, 
                'Exit': b2_exit,
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
        elif controls_open:
            screen.blit(background_image, (0, 0))
            c_buttons = {
                'Left': LEFT, 
                'Right': RIGHT, 
                'Jump': JUMP,
                'Sneak': SNEAK,
                'Run': RUN,
                'Inventory': WINDOW,
                'Background build': BACK_BUILD
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
                "Flat world": flat_world,
                "Keep inventory": keep_inventory,
                "Daylight cycle": daylight_cycle,
                "Weather cycle": weather_cycle,
                "Mob spawning": mob_spawning,
                "Mob loot": mob_loot,
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

            generate_text = font.render("Generate world", True, (255, 255, 255))
            generate_text_rect = generate_text.get_rect(center=generate_button_rect.center)
            screen.blit(generate_text, generate_text_rect)

            load_x = (screen_width - 400) // 2
            load_y = screen_height - 210
            load_button_rect = pygame.Rect(load_x, load_y, 400, 50)

            load_image = adjust_image(button_image_path, 400, 50)
            screen.blit(load_image, (load_x, load_y))

            load_text = font.render("Load world", True, (255, 255, 255))
            load_text_rect = load_text.get_rect(center=load_button_rect.center)
            screen.blit(load_text, load_text_rect)

        if controls_open or play_open:
            font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 27)
            exit_x = (screen_width - 200) // 2
            exit_y = screen_height - 70
            exit_button_rect = pygame.Rect(exit_x, exit_y, 200, 50)

            button_image_path = os.path.join(files_path, "images", "_sys_button.png")
            button_image = adjust_image(button_image_path, 200, 50)
            screen.blit(button_image, (exit_x, exit_y))

            exit_text = font.render("Back", True, (255, 255, 255))
            exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
            screen.blit(exit_text, exit_text_rect)
    elif state == "game":
        screen.fill((135, 206, 235))
        old_height = player_height
        old_player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        keys = pygame.key.get_pressed()
        if not menu_open:
            if keys[SNEAK[0]]:
                player_speed = default_speed / speed_multiplier
                player_width, player_height = shift_width, shift_height
            elif keys[RUN[0]]:
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
        visible_uncollide_plats = [
            p for p in uncollide_plats
            if (
                p.platform.x + p.platform.width > camera_x and
                p.platform.x < camera_x + screen_width and
                p.platform.y + p.platform.height > camera_y and
                p.platform.y < camera_y + screen_height
            )
        ]
        for p in visible_platforms:
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
            if player_rect.colliderect(platform):
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
        
        dx, dy = 0, 0
        if not menu_open:
            if keys[LEFT[0]]:
                dx -= player_speed
            if keys[RIGHT[0]]:
                dx += player_speed

            if keys[SNEAK[0]] and (keys[LEFT[0]] or keys[RIGHT[0]]) and not keys[JUMP[0]]:
                temp_rect = pygame.Rect(player_x + dx, player_y+5, player_width, player_height)
                can_move = False

                for p in visible_platforms:
                    platform = p.platform
                    if temp_rect.colliderect(platform) and player_y<=p.y and p not in ignore:
                        can_move = True
                        break

                if not can_move:
                    dx = 0

            if keys[JUMP[0]] and on_ground:
                player_velocity_y = player_jump_speed
                on_ground = False

        in_liquid = False
        deal_damage = False
        for p in visible_uncollide_plats:
            platform = p.platform
            if "liquid" in blocks[p.type] and player_rect.colliderect(platform):
                in_liquid = True
                if p.type == "lava":
                    deal_damage = True
                break
        if in_liquid:
            if keys[SNEAK[0]]:
                player_velocity_y += gravity 
            else:
                player_velocity_y += gravity / 3
            if keys[JUMP[0]]:
                player_velocity_y = -gravity * 3
        else:
            player_velocity_y += gravity
        dy += player_velocity_y
        if deal_damage:
            current_time = pygame.time.get_ticks()
            if current_time >= lava_damage_timer:
                health -= 4
                health = max(health, 0)
                lava_damage_timer = current_time + 750
                red_timer = current_time + 300
            
        player_rect = pygame.Rect(player_x + dx, player_y, player_width, player_height)
        on_ground = False
        for p in visible_platforms:
            platform = p.platform
            if player_rect.colliderect(platform) and p not in ignore:
                if dx > 0:
                    player_x = platform.left - player_width
                    dx = 0
                elif dx < 0:
                    player_x = platform.right
                    dx = 0

        player_rect = pygame.Rect(player_x, player_y + dy, player_width, player_height)
        for p in visible_platforms:
            platform = p.platform
            if player_rect.colliderect(platform) and p not in ignore:
                if dy > 0:
                    if abs(player_velocity_y) > ((BLOCK_SIZE*3)*2*gravity)**(1/2) and not in_liquid:
                        damage = int(abs(((player_velocity_y) ** 2) / (2 * gravity)) // 50 - 3)
                        health -= damage
                        health = max(health, 0)
                        red_timer = pygame.time.get_ticks() + 300
                    player_y = platform.top - player_height
                    player_velocity_y = 0
                    dy = 0
                    on_ground = True
                elif dy < 0:
                    player_y = platform.bottom
                    player_velocity_y = 0
                    dy = 0

        player_x += dx
        player_y += dy

        if player_y > -BEDROCK_Y or health == 0:
            player_x = 0
            player_y = -BLOCK_SIZE*4
            health = 20
            hunger = 20
            if not keep_inventory[0]:
                inv_counts = [0]*36
                inv_items = [None]*36

        camera_x = player_x - screen_width // 2 + player_width//2
        camera_y = player_y - screen_height // 2 + player_height//2

        player_image_path = os.path.join(files_path, "images", "steve.png")
        player_image = pygame.image.load(player_image_path)
        player_image = pygame.transform.scale(player_image, (player_width, player_height))

        current_time = pygame.time.get_ticks()
        if red_timer > current_time:
            red_overlay = pygame.Surface(player_image.get_size(), flags=pygame.SRCALPHA)
            red_overlay.fill((128, 0, 0))
            player_image.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        liquid_updating = []
        for p in reversed(visible_uncollide_plats):
            platform = p.platform
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
                        if not p.parent in uncollide_plats:
                            if p in uncollide_plats:
                                uncollide_plats.remove(p)
                    if not p.type in liquid_updating:
                        liquid_updating.append(p.type)
            else:
                darken = darken_surface(texture, 0.5)
                screen.blit(darken, (platform.x - camera_x, platform.y - camera_y))
        for u in liquid_updating:
            blocks[u]["liquid"][1] = current_time

        screen.blit(player_image, (player_rect.x - camera_x, player_rect.y - camera_y))
        
        for p in visible_platforms:
            platform = p.platform
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
                if block_at_mouse is not None and blocks[block_at_mouse.type]["break"] != float('inf'):
                    type = inv_items[inv_num]
                    doubler=1
                    
                    for breaktool in mining.keys():
                        if type is not None and breaktool in type and sum([int(b in block_at_mouse.type) for b in mining[breaktool]]) > 0:
                            doubler = items[type]["dig"]
                            break

                    block_at_mouse.broke = True
                    block_at_mouse.breaking(blocks[block_at_mouse.type]["break"]/doubler)

                    break_progress = min(block_at_mouse.breaktime / ((blocks[block_at_mouse.type]["break"]*2/doubler) * FPS), 1.0)
                    scale_factor = 1 + break_progress * 0.5
                    if block_at_mouse in uncollide_plats and not "liquid" in blocks[block_at_mouse.type]:
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
                t = inv_items[inv_num]
                if t is not None:
                    if t == "bucket":
                        if block_at_mouse and "liquid" in blocks[block_at_mouse.type]:
                            inv_items[inv_num] = block_at_mouse.type + "_bucket"
                            if block_at_mouse in uncollide_plats:
                                uncollide_plats.remove(block_at_mouse)
                    elif block_at_mouse is None or ("liquid" in blocks[block_at_mouse.type] and block_at_mouse.type != t and (block_at_mouse.type != items[t]["block"] if t in items and "block" in items[t] else True)):
                        remain = None
                        if t in items and "block" in items[t]:
                            if "remain" in items[t]:
                                remain = items[t]["remain"]
                            t = items[t]["block"]
                        if t in blocks:
                            if not pygame.Rect(block_x, block_y, BLOCK_SIZE, BLOCK_SIZE).colliderect(player_rect):
                                if block_at_mouse in uncollide_plats:
                                    uncollide_plats.remove(block_at_mouse)
                                new_block = Block(block_x, block_y, t)
                                if not "liquid" in blocks[t] and not keys[BACK_BUILD[0]]:
                                    platforms.append(new_block)
                                    pos.append((block_x, block_y))
                                else:
                                    uncollide_plats.append(new_block)
                                    uncollide_pos.append((block_x, block_y))
                                block_up = get_block_at(mouse=(block_x, block_y-BLOCK_SIZE))
                                if block_up:
                                    block_up.liquided = False
                                inv_counts[inv_num] -= 1
                                if inv_counts[inv_num] <= 0:
                                    inv_items[inv_num] = None
                                if remain:
                                    for i in range(36):
                                        if inv_items[i] == None and inv_counts[i] == 0:
                                            inv_items[i] = remain
                                            inv_counts[i] = 1
                                            break

            if hunger == 20 and health < 20:
                if current_time - health_update >= game_tick:
                    health += 1
                    health_update = current_time
            elif hunger == 0:
                if current_time - health_update >= game_tick:
                    health -= 1
                    health_update = current_time

        inventory_width = 9 * 50
        y = screen_height - 100
        start_x = (screen_width - inventory_width) // 2
        
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
                    item_draw(x, y_offset, inv_items[i], inv_counts[i])
        
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
                item_draw(x, y, inv_items[i], inv_counts[i])

        pygame.draw.rect(screen, (225, 225, 225), (8 + start_x + inv_num * 50 - inv_num*2 -5, y-5, 60, 60), 5)

        if dragging_item is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if dragging_item < 100:
                item_type = inv_items[dragging_item]
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
                'Resume': b_resume, 
                'Save': b_save, 
                'Exit': b_exit,
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

    font = pygame.font.Font(files_path+"/other/Minecraftia.ttf", 18)
    text = font.render(VERSION, True, (255, 255, 255))
    text_rect = text.get_rect(topleft=(5, 5))
    screen.blit(text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()
