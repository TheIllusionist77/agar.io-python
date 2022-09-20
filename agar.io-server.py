# IMPORTING NECCESARY MODULES
import socket, random, math, threading

# GETTING HOST IP
n = socket.gethostname()
ip = socket.gethostbyname(n)
print("Connect to IP " + str(ip) + " to play!")

# VARIABLES THAT CAN BE CHANGED
PORT = 65432
cell_count = 2000
respawn_cells = True

# SYSTEM VARIABLES
spawn_size = 25
HOST = str(ip)
cells = []
keys = []
player_dict = {}

# PARSER FUNCTION
def parser(cell_string):
    temp_string = ""
    string_list = []
    for character in cell_string:
        if character != ":":
            temp_string += str(character)
        else:
            string_list.append(temp_string)
            temp_string = ""
    return string_list

# CLASS FOR ALL CELLS IN THE GAME
class Cell():
    def __init__(self, x, y, color, radius, name, username = None):
        self.username = username
        self.name = name
        self.radius = radius
        self.color = color
        self.x_pos = x
        self.y_pos = y
        self.eaten = False
    
    # CHECKS IF AN CELL IS COLLIDING WITH SOMETHING
    def collide_check(self):
        global cells
        for cell in cells:
            if cell.name == "Cell" and math.sqrt((self.x_pos - cell.x_pos) ** 2 + (self.y_pos - cell.y_pos) ** 2) <= cell.radius / 5 + self.radius / 5 and cell.radius / 5 <= self.radius / 5:
                cells.remove(cell)
                self.radius += 0.25
                if respawn_cells:
                    new_cell = Cell(random.randint(0, 1280), random.randint(0, 720), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5, "Cell")
                    cells.append(new_cell)
        for player in player_dict:
            player = player_dict[player]
            if player.name == "Player" and player.username != self.username and math.sqrt((self.x_pos - player.x_pos) ** 2 + (self.y_pos - player.y_pos) ** 2) <= player.radius / 5 + self.radius / 5 and player.radius / 5 >= self.radius / 5 * 1.1:
                self.eaten = True
            
# SPAWNING EVERY CELL
for i in range(cell_count):
    new_cell = Cell(random.randint(0, 1280), random.randint(0, 720), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), 5, "Cell")
    cells.append(new_cell)

# SERVER CONNECTION FUNCTION
def Server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                send_info = ""
                data = conn.recv(65536)
                if not data:
                    break
                else:
                    data = parser(data.decode())

                # CHECKING IF PLAYER IS NEW OR EXISTING
                if len(data) == 6:
                    cell = Cell(int(data[4]), int(data[5]), (int(data[1]), int(data[2]), int(data[3])), spawn_size, "Player", data[0])
                    keys.append(data[0])
                    player_dict[str(data[0])] = cell
                elif "END_CONNECTION" in str(data[0]):
                    player_dict.pop(str(data[1]))
                else:
                    cell = player_dict[data[2]]
                    if cell.name == "Player":
                        if cell.eaten == True:
                            player_dict.pop(cell.username)
                            response = str("GAME_OVER:" + cell.username)
                            transmit = response.encode("utf-8")
                            conn.sendall(transmit)
                        else:
                            cell.collide_check()
                            # MAKING BORDERS FOR THE MAP
                            if cell.x_pos >= 1280:
                                cell.x_pos -= 5
                            elif cell.x_pos <= 0:
                                cell.x_pos += 5
                            else:
                                cell.x_pos += round(-((-int(data[0]) + 640) / cell.radius / 10))
                            if cell.y_pos >= 720:
                                cell.y_pos -= 5
                            elif cell.y_pos <= 0:
                                cell.y_pos += 5
                            else:
                                cell.y_pos += round(-((-int(data[1]) + 360) / cell.radius / 5))
                
                # ADDING EVERY PLAYER TO THE SEND LIST
                for key in keys:
                    try:
                        cell = player_dict[key]
                        if cell.radius > 25:
                            cell.radius -= 0.0025
                        temp_string = str(str(cell.radius) + ":" + str(cell.color[0]) + ":" + str(cell.color[1]) + ":" + str(cell.color[2]) + ":" + str(cell.x_pos) + ":" + str(cell.y_pos) + ":" + str(cell.username) + ":")
                        send_info += temp_string
                        send_info += "/"
                    except:
                        pass
                
                # ADDING EVERY CELL TO THE SEND LIST
                for cell in cells:
                    temp_string = str(str(cell.radius) + ":" + str(cell.color[0]) + ":" + str(cell.color[1]) + ":" + str(cell.color[2]) + ":" + str(cell.x_pos) + ":" + str(cell.y_pos) + ":None:")
                    send_info += temp_string
                    send_info += "/"
                
                # SENDING DATA
                response = str(send_info)
                transmit = response.encode("utf-8")
                conn.sendall(transmit)
            
# MAIN CONNECTION HANDLER LOOP
while True:
    try:
        threading.Thread(target = Server()).start()
    except:
        pass