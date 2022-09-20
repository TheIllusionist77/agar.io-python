# IMPORTING AND INITIALIZING NECCESARY MODULES
import pygame, sys, random, math, time, socket
from pygame.locals import *
pygame.init()

# SETTING UP THE SCREEN
SCREEN = pygame.display.set_mode((1280, 720))
FPS = 15
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Agar.io")

# VARIABLES THAT CAN BE CHANGED
HOST = "IP"
PORT = 65432
text_color = (255, 255, 255)
background_color = (0, 0, 0)

# SYSTEM VARIABLES
TINYFONT = pygame.font.Font("freesansbold.ttf", 16)
FONT = pygame.font.Font("freesansbold.ttf", 32)
BIGFONT = pygame.font.Font("freesansbold.ttf", 72)
game_over = False
counter = 0
frame_rate = 30
start_time = 0
frame_rate_delay = 0.5
droppedFrames = 0
playerRadius = 25
username = ""
            
# PARSER FUNCTION
def parser(cell_strings, surface):
    global username, playerRadius
    temp_string = ""
    master_strings = []
    for character in cell_strings:
        if character != "/":
            temp_string += str(character)
        else:
            master_strings.append(temp_string)
            temp_string = ""
    temp_string = ""
    for cell_string in master_strings:
        string_list = []
        for character in cell_string:
            if character != ":":
                temp_string += str(character)
            else:
                string_list.append(temp_string)
                temp_string = ""
        temp_radius = float(string_list[0])
        temp_r = int(string_list[1])
        temp_g = int(string_list[2])
        temp_b = int(string_list[3])
        temp_x = int(string_list[4])
        temp_y = int(string_list[5])
        temp_username = string_list[6]
        if temp_username == username:
            playerRadius = temp_radius
        if temp_username != "None":
            pygame.draw.circle(surface, (temp_r, temp_g, temp_b), (temp_x, temp_y), int(temp_radius / 5))
            text = TINYFONT.render(str(temp_username), False, text_color)
            SCREEN.blit(text, (temp_x - 27.5, temp_y - 7.5))
        else:
            pygame.draw.circle(surface, (temp_r, temp_g, temp_b), (temp_x, temp_y), int(temp_radius / 5))

# FUNCTION THAT SENDS DATA TO THE SERVER
def send_to_server(message):
    data = ""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            b = message.encode("utf-8")
            s.sendall(b)
            while not data:
                data = s.recv(65536)
        except:
            return False
    if data.decode() == "GAME_OVER:" + str(username):
        return "GAME_OVER"
    return str(data.decode())

while len(username) < 4 or len(username) > 8:
    username = input("Enter your username: ")
    if len(username) < 4 or len(username) > 8:
        print("Your username must be at least 4 and at most 8 letters long!")
        
send_to_server(str(username) + ":" + str(random.randint(0, 255)) + ":" + str(random.randint(0, 255)) + ":" + str(random.randint(0, 255)) + ":" + str(random.randint(0, 1280)) + ":" + str(random.randint(0, 720)) + ":")
  
# MAIN GAME LOOP
while True:
    # CHECKING FOR INPUT
    for event in pygame.event.get():
        if event.type == QUIT:
            if game_over == False:
                send_to_server("END_CONNECTION:" + str(username) + ":")
            pygame.quit()
            sys.exit()
        if event.type == MOUSEMOTION and game_over == False:
            mouse_x, mouse_y = event.pos
        else:
            mouse_x = 640
            mouse_y = 360
    
    # COMMUNICATING WITH SERVER IF GAME IS RUNNING
    if not game_over:       
        player_data = send_to_server(str(mouse_x) + ":" + str(mouse_y) + ":" + str(username) + ":")
    
        if player_data != False:
            parser(player_data, SCREEN)
        else:
            droppedFrames += 1
    
        if player_data == "GAME_OVER":
            game_over = True
    
    # CHECKING IF THE GAME IS OVER
    if game_over == True:
        text = BIGFONT.render("You lost!", False, text_color)
        SCREEN.blit(text, (490, 320))
    
    # DRAWING THE MASS TO THE SCREEN
    text = FONT.render("Mass: " + str(round(playerRadius, 1)), False, text_color)
    SCREEN.blit(text, (20, 20))
    
    # PUTTING THE AMOUNT OF DROPPED FRAMES ON THE SCREEN
    text = TINYFONT.render("Dropped Frames: " + str(droppedFrames), False, text_color)
    SCREEN.blit(text, (20, 100))
    
    # CALCULATING FPS
    counter += 1
    if frame_rate > 10:
        text = FONT.render("FPS: " + str(frame_rate), False, (55, 255, 55))
        SCREEN.blit(text, (20, 60))
    elif frame_rate <= 10 and frame_rate > 5:
        text = FONT.render("FPS: " + str(frame_rate), False, (255, 255, 55))
        SCREEN.blit(text, (20, 60))
    elif frame_rate <= 5 and frame_rate > 0:
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