# IMPORTING AND INITIALIZING NECCESARY MODULES
import pygame, sys, random, math, time
from pygame.locals import *
pygame.init()

# SETTING UP THE SCREEN
SCREEN = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
FPS = 30
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Agar.io")

# VARIABLES THAT CAN BE CHANGED
cell_count = 2000
bot_count = 20
map_size = 2000
spawn_size = 25
bots_min_size = 25
bots_max_size = 250
respawn_cells = True
respawn_bots = False
player_color = (255, 0, 0)
background_color = (0, 0, 0)
text_color = (255, 255, 255)

# SYSTEM VARIABLES
FONT = pygame.font.Font("freesansbold.ttf", 32)
BIGFONT = pygame.font.Font("freesansbold.ttf", 72)
WIDTH = 1280
HEIGHT = 720
cells = []
bots = []
game_over = False
counter = 0
frame_rate = 30
start_time = 0
frame_rate_delay = 0.5

# CLASS FOR ALL CELLS IN THE GAME
class Cell():
    def __init__(self, x, y, color, radius, name):
        self.name = name
        self.radius = radius
        self.color = color
        self.status = random.randint(1, 8)
        self.x_pos = x
        self.y_pos = y
    
    # MAKES THE BOTS WANDER
    def wander(self):
        randomize = random.randint(1, round(self.radius))
        if randomize == 1:
            self.status = random.randint(1, 8)
        
        if self.status == 1:
            self.y_pos += 300 / self.radius
        elif self.status == 2:
            self.x_pos += 150 / self.radius
            self.y_pos += 150 / self.radius
        elif self.status == 3:
            self.x_pos += 300 / self.radius
        elif self.status == 4:
            self.x_pos += 150 / self.radius
            self.y_pos -= 150 / self.radius
        elif self.status == 5:
            self.y_pos -= 300 / self.radius
        elif self.status == 6:
            self.x_pos -= 150 / self.radius
            self.y_pos -= 150 / self.radius
        elif self.status == 7:
            self.x_pos -= 300 / self.radius
        elif self.status == 8:
            self.x_pos -= 150 / self.radius
            self.y_pos += 150 / self.radius
    
    # CHECKS IF AN CELL IS COLLIDING WITH SOMETHING
    def collide_check(self, player):
        global cells, bots, game_over
        for cell in cells:
            if math.sqrt(((player.x_pos - (WIDTH / 2) + cell.x_pos) ** 2 + (player.y_pos - (HEIGHT / 2) + cell.y_pos) ** 2)) <= cell.radius + player.radius and cell.radius <= player.radius:
                cells.remove(cell)
                player.radius += 0.25
                if respawn_cells:
                    new_cell = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5, "Cell")
                    cells.append(new_cell)
        for bot in bots:
            if math.sqrt(((player.x_pos - (WIDTH / 2) + bot.x_pos) ** 2 + (player.y_pos - (HEIGHT / 2) + bot.y_pos) ** 2)) <= player.radius and bot.radius * 1.1 <= player.radius:
                bot_area = math.pi * (bot.radius ** 2)
                player_area = math.pi * (player.radius ** 2)
                new_area = bot_area + player_area
                new_radius = math.sqrt(new_area / math.pi)
                player.radius += new_radius - player.radius
                bots.remove(bot)
                if respawn_bots:
                    new_bot = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(25, 250), "Bot")
                    bots.append(new_bot)
            elif math.sqrt(((player.x_pos - (WIDTH / 2) + bot.x_pos) ** 2 + (player.y_pos - (HEIGHT / 2) + bot.y_pos) ** 2)) <= bot.radius and bot.radius >= player.radius * 1.1 and not game_over:
                bot_area = math.pi * (bot.radius ** 2)
                player_area = math.pi * (player.radius ** 2)
                new_area = bot_area + player_area
                new_radius = math.sqrt(new_area / math.pi)
                bot.radius += new_radius - bot.radius
                game_over = True
            else:
                for collide_bot in bots:
                    if math.sqrt(((collide_bot.x_pos - bot.x_pos) ** 2 + (collide_bot.y_pos - bot.y_pos) ** 2)) <= bot.radius and bot.radius >= collide_bot.radius * 1.1:
                        bots.remove(collide_bot)
                        bot_area = math.pi * (bot.radius ** 2)
                        collide_bot_area = math.pi * (collide_bot.radius ** 2)
                        new_area = bot_area + collide_bot_area
                        new_radius = math.sqrt(new_area / math.pi)
                        bot.radius += new_radius - bot.radius
                        if respawn_bots:
                            new_bot = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(25, 250), "Bot")
                            bots.append(new_bot)
                for cell in cells:
                    if math.sqrt(((bot.x_pos - cell.x_pos) ** 2 + (bot.y_pos - cell.y_pos) ** 2)) <= cell.radius + bot.radius and cell.radius <= bot.radius:
                        cells.remove(cell)
                        bot.radius += 0.25
                        if respawn_cells:
                            new_cell = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5, "Cell")
                            cells.append(new_cell)
    
    # DRAWS THE CELL TO THE SCREEN
    def draw(self, surface, x, y):
        pygame.draw.circle(surface, self.color, (x, y), int(self.radius))
        if self.name == "Bot" or self.name == "Player":
            text = FONT.render(str(round(self.radius)), False, text_color)
            SCREEN.blit(text, (x - 17.5, y - 12.5))

# SPAWNS THE ORIGINAL CELLS, BOTS AND PLAYER
for i in range(cell_count):
    new_cell = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5, "Cell")
    cells.append(new_cell)
    
for i in range(bot_count):
    new_bot = Cell(random.randint(-map_size, map_size), random.randint(-map_size, map_size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), random.randint(bots_min_size, bots_max_size), "Bot")
    bots.append(new_bot)
    
player_cell = Cell(0, 0, player_color, spawn_size, "Player")
  
# MAIN GAME LOOP
while True:
    # CHECKING FOR INPUT
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION and game_over == False:
            mouse_x, mouse_y = event.pos
        else:
            mouse_x = WIDTH / 2
            mouse_y = HEIGHT / 2
    
    if not game_over:        
        player_cell.collide_check(player_cell)
    
    # MAKING BORDERS FOR THE MAP
    if player_cell.x_pos >= map_size + (WIDTH / 2):
        player_cell.x_pos -= 5
    elif player_cell.x_pos <= -map_size + (WIDTH / 2):
        player_cell.x_pos += 5
    else:
        player_cell.x_pos += round(-((mouse_x - (WIDTH / 2)) / player_cell.radius / 2))
    if player_cell.y_pos >= map_size + (HEIGHT / 2):
        player_cell.y_pos -= 5
    elif player_cell.y_pos <= -map_size + (HEIGHT / 2):
        player_cell.y_pos += 5
    else:
        player_cell.y_pos += round(-((mouse_y - (HEIGHT / 2)) / player_cell.radius))
    
    # DRAWING EVERY CELL TO THE SCREEN AND CALCULATING NEW BOT POSITIONS
    for cell in cells:
        cell.draw(SCREEN, cell.x_pos + player_cell.x_pos, cell.y_pos + player_cell.y_pos) 
    for bot in bots:
        if bot.x_pos >= map_size:
            bot.x_pos -= 5
        elif bot.x_pos <= -map_size:
            bot.x_pos += 5   
        if bot.y_pos >= map_size:
            bot.y_pos -= 5
        elif bot.y_pos <= -map_size:
            bot.y_pos += 5
        bot.wander()
        bot.draw(SCREEN, bot.x_pos + player_cell.x_pos, bot.y_pos + player_cell.y_pos)
    
    # CHECKING IF THE GAME IS OVER
    if game_over == True:
        text = BIGFONT.render("You lost!", False, text_color)
        SCREEN.blit(text, ((WIDTH / 2) - 150, (HEIGHT / 2) - 40))
    else:
        player_cell.draw(SCREEN, (WIDTH / 2), (HEIGHT / 2))
    
    # DRAWING THE MASS TO THE SCREEN
    text = FONT.render("Mass: " + str(round(player_cell.radius)), False, text_color)
    SCREEN.blit(text, (20, 20))
    
    # CALCULATING FPS
    counter += 1
    if frame_rate > 20:
        text = FONT.render("FPS: " + str(frame_rate), False, (55, 255, 55))
        SCREEN.blit(text, (20, 60))
    elif frame_rate <= 20 and frame_rate > 10:
        text = FONT.render("FPS: " + str(frame_rate), False, (255, 255, 55))
        SCREEN.blit(text, (20, 60))
    elif frame_rate <= 10 and frame_rate > 0:
        text = FONT.render("FPS: " + str(frame_rate), False, (255, 55, 55))
        SCREEN.blit(text, (20, 60))
        
    if (time.time() - start_time) > frame_rate_delay:
        frame_rate = round(counter / (time.time() - start_time))
        counter = 0
        start_time = time.time()
    
    # ENDING STUFF
    WIDTH, HEIGHT = pygame.display.get_surface().get_size()
    pygame.display.update()
    CLOCK.tick(FPS)
    SCREEN.fill(background_color)