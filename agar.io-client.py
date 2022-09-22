# IMPORTING AND INITIALIZING NECCESARY MODULES
import pygame, sys, random, time, socket
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
server_uptime = 0
ping = 0
playerRadius = 25
username = ""
player_data = ""
            
# PARSER FUNCTION
def parser(cell_strings, surface):
    if player_data == "":
        text = FONT.render("Something went wrong, please reconnect.", False, (255, 55, 55))
        SCREEN.blit(text, (320, 320))
    else:
        global username, playerRadius, server_uptime
        temp_string = ""
        master_strings = []
        for character in cell_strings:
            if character != "/":
                if character == "-":
                    try:
                        seconds = int(temp_string)
                        minutes = divmod(seconds, 60)[0]
                        seconds = divmod(seconds, 60)[1]
                        hours = divmod(minutes, 60)[0]
                        minutes = divmod(minutes, 60)[1]
                        server_uptime = str(int(hours)) + "h:" + str(int(minutes)) + "m:" + str(int(seconds)) + "s"
                    except ValueError:
                        pass
                    temp_string = ""
                else:
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
            try:
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
            except ValueError:
                pass

# FUNCTION THAT SENDS DATA TO THE SERVER
def send_to_server(message):
    global ping
    data = ""
    start_time = time.perf_counter()
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
    ping = round((time.perf_counter() - start_time) * 1000, 1)
    return str(data.decode())

# GETTING READY TO CONNECT TO THE SERVER AND START THE GAME
while len(username) < 4 or len(username) > 8:
    username = input("Enter your username: ")
    if len(username) < 4 or len(username) > 8:
        print("Your username must be at least 4 and at most 8 letters long!")
        
parser(player_data, SCREEN)
pygame.display.update()
        
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
        server_data = send_to_server(str(mouse_x) + ":" + str(mouse_y) + ":" + str(username) + ":")
    
        if server_data != False:
            player_data = server_data
            parser(player_data, SCREEN)
            disconnected = False
        else:
            parser(player_data, SCREEN)
            droppedFrames += 1
            disconnected = True
    
        if player_data == "GAME_OVER":
            game_over = True
    
    # CHECKING IF THE GAME IS OVER
    if game_over == True:
        text = BIGFONT.render("You lost!", False, text_color)
        SCREEN.blit(text, (490, 320))
    
    # DRAWING THE MASS TO THE SCREEN
    text = FONT.render("Mass: " + str(round(playerRadius, 1)), False, text_color)
    SCREEN.blit(text, (20, 20))
    
    # PUTTING THE PING ON THE SCREEN
    text = TINYFONT.render("Ping: " + str(ping) + "ms", False, text_color)
    SCREEN.blit(text, (20, 580))
    
    # PUTTING THE SERVER UPTIME ON THE SCREEN
    text = TINYFONT.render("Server Uptime: " + str(server_uptime), False, text_color)
    SCREEN.blit(text, (20, 600))
    
    # PUTTING THE SERVER ADDRESS ON THE SCREEN
    text = TINYFONT.render("Server Address: " + str(HOST), False, text_color)
    SCREEN.blit(text, (20, 620))
    
    # PUTTING THE AMOUNT OF DROPPED FRAMES ON THE SCREEN
    text = TINYFONT.render("Dropped Frames: " + str(droppedFrames), False, text_color)
    SCREEN.blit(text, (20, 640))
    if droppedFrames <= 50:
        text = TINYFONT.render("Your connection is stable", False, (55, 255, 55))
        SCREEN.blit(text, (20, 660))
    elif droppedFrames <= 100:
        text = TINYFONT.render("Your connection is slightly unstable", False, (155, 255, 55))
        SCREEN.blit(text, (20, 660))
    elif droppedFrames <= 300:
        text = TINYFONT.render("Your connection is unstable, dropped framerate", False, (255, 155, 55))
        SCREEN.blit(text, (20, 660))
        FPS = 12
    else:
        text = TINYFONT.render("Your connection is very unstable, dropped framerate further", False, (255, 55, 55))
        SCREEN.blit(text, (20, 660))
        FPS = 8
    
    # PUTTING THE CONNECTION STATUS ON THE SCREEN
    if disconnected == False:
        text = TINYFONT.render("Connected to server", False, (55, 255, 55))
        SCREEN.blit(text, (20, 680))
    else:
        text = TINYFONT.render("Failed to connect to server", False, (255, 55, 55))
        SCREEN.blit(text, (20, 680))
    
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
