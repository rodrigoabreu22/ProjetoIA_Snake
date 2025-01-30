#Rodrigo Abreu, 113626
#Eduardo Lopes, 103070
#João Neto, 113482


from snake_domain import *
import math

class Agent():
    def __init__(self):
        self.state = None
        self.key = ""
        self.map = None
        self.map_size = None
        self.my_position = None
        self.traverse = True
        self.last_direction = None      
        self.body = []  
        self.savedfoods=[]     
        self.savedSfoods=[]     
        self.path = []         
        self.walls = []
        self.checkpoints = []  
        self.sight_range = 1
        self.trying = None
        self.pathTocheckpoint = []
        self.visible_fruit_list = []
        self.path_food = None
        self.fps = 10
        self.enemy_snake = []
        self.enemy_snake_seen = False
        self.map_borders = []

    def wrap_position(self, pos):
        map_width, map_height = self.map_size
        return [(pos[0] + map_width) % map_width, (pos[1] + map_height) % map_height]

    def update_state(self, state):
        if 'map' in state:
            self.map = state['map']
            self.map_size = state['size']
            self.fps = state['fps']

            for i in range(self.map_size[0]):
                for j in range(self.map_size[1]):
                    if self.map[i][j] == 1:
                        self.walls.append([i, j])
            
            self.map_borders.extend([[i, -1] for i in range(self.map_size[0])])  
            self.map_borders.extend([[i, self.map_size[1]] for i in range(self.map_size[0])])  
            self.map_borders.extend([[-1, i] for i in range(self.map_size[1])])  
            self.map_borders.extend([[self.map_size[0], i] for i in range(self.map_size[1])])  

        elif 'body' in state:
            self.state = state
            self.body = state['body']
            self.my_position = state['body'][0]

            food, superfood, enemy_snake = self.get_sight_info()

            if enemy_snake or self.traverse != state['traverse']:
                self.traverse = state['traverse']
                self.enemy_snake = enemy_snake
                self.path=[]
                self.pathTocheckpoint=[]
                self.checkpoints = []
                self.enemy_snake_seen = True

            elif self.enemy_snake_seen:
                self.enemy_snake_seen = False
                self.path=[]
                self.pathTocheckpoint=[]
                self.checkpoints = []
                self.enemy_snake=[]


            if self.sight_range != 1:
                if self.sight_range != len(self.state['sight']) if 'sight' in self.state else 1:
                    self.sight_range = len(self.state['sight']) if 'sight' in self.state else 1
                    self.checkpoints = self.generate_checkpoints()
            else:
                self.sight_range = len(self.state['sight']) if 'sight' in self.state else 1
                self.checkpoints = self.generate_checkpoints()

            if not self.checkpoints:
                self.checkpoints = self.generate_checkpoints()


            if food or superfood:
                self.pathTocheckpoint=[]
                food_found = False
                if food:
                    self.visible_fruit_list.extend(food)
                    food_found=True
                    
                if superfood :
                    if self.sight_range < 8 or not self.traverse:
                        self.visible_fruit_list.extend(superfood)
                    else: 
                        if not food_found and not self.path:

                            if not self.pathTocheckpoint:
                                return self.whats_next()
                            else:
                                return self.go_to(self.pathTocheckpoint.pop(0))



                closest_food = self.find_closest_food(self.visible_fruit_list)

                if closest_food != self.path_food and closest_food!=None:
                    self.path_food = closest_food
                    tree = self.tree_search(self.path_food)
                    self.path = tree.search()


                    if self.path:
                        self.path.pop(0)


            if self.path:
                next_position = self.path.pop(0)

                if next_position == self.path_food:
                    self.visible_fruit_list = [item for item in self.visible_fruit_list if item != self.path_food]
                    self.path_food = None

                return self.go_to(next_position)

            else:
                if self.visible_fruit_list != []:
                    self.path_food = self.find_closest_food(self.visible_fruit_list)
                    tree = self.tree_search(self.path_food)
                    path = tree.search()

                    if path and len(path)>1:
                        self.path=path
                        self.path.pop(0)
                        next_position = self.path.pop(0)
                        return self.go_to(next_position)

                else:
                    if not self.pathTocheckpoint:
                        return self.whats_next()
                    else:
                        return self.go_to(self.pathTocheckpoint.pop(0))
                    
                    
        if self.key == "":
            return self.key
    
    def go_to(self, next):
        count = 0
        for checkpoint in self.checkpoints:
            distance = abs(next[0] - checkpoint[0]) + abs(next[1] - checkpoint[1])
            if distance < self.state["range"]-1:
                self.checkpoints.pop(count)
                break
            count+=1

        map_width, map_height = self.map_size  
        
        current_x, current_y = self.my_position
        next_x, next_y = next

        delta_x = (next_x - current_x) % map_width
        if delta_x > map_width / 2:
            delta_x -= map_width  

        delta_y = (next_y - current_y) % map_height
        if delta_y > map_height / 2:
            delta_y -= map_height 

        if abs(delta_x) > 0 and delta_y == 0:
            if delta_x > 0:
                self.key = "d"
                self.last_direction = 1
            else:
                self.key = "a"
                self.last_direction = 3
        elif abs(delta_y) > 0 and delta_x == 0:
            if delta_y > 0:
                self.key = "s"
                self.last_direction = 2
            else:
                self.key = "w"
                self.last_direction = 0
        else:
            if self.last_direction ==0:
                self.key = "w"
            elif self.last_direction ==2:
                self.key="s"
            elif self.last_direction ==3:
                self.key="a"
            elif self.last_direction==1:
                self.key="d"

        return self.key
        
    
    def tree_search(self, goal): 

        domain = SnakeDomain(map, self.map_size, self.enemy_snake, self.walls, self.traverse)
        problem = SearchProblem(domain, self.body, goal)
            
        if not self.traverse:
            return SearchTree(problem, 'greedy', self.fps)
        return SearchTree(problem, 'a*', self.fps)
        
    def whats_next(self):
        
        next_checkpoint = None
        while self.checkpoints:
            if not next_checkpoint:
                next_checkpoint = self.checkpoints[0]  
                if next_checkpoint in self.body[1:] or next_checkpoint in self.walls:
                    self.checkpoints.pop(0)
                    next_checkpoint = None
                    self.pathTocheckpoint=[]
                    if not self.checkpoints:
                        self.checkpoints = self.generate_checkpoints()
                    continue

                tree = self.tree_search(next_checkpoint)
                self.pathTocheckpoint = tree.search()

            if not self.pathTocheckpoint:
                self.checkpoints.pop(0)
                if not self.checkpoints:
                    self.checkpoints = self.generate_checkpoints()
                next_checkpoint = None
                continue

            else:
                head = self.pathTocheckpoint.pop(0)

                next_position = self.pathTocheckpoint.pop(0)
                
                if next_position == next_checkpoint:
                    next_checkpoint=None
                    
                    if self.checkpoints:
                        self.checkpoints.pop(0)

                position_to_go = next_position
                next_position = None
                return self.go_to(position_to_go)
                

    def generate_no_traverse_checkpoints(self):
        checkpoints = []
        reverse = False
        snake_direction = self.last_direction
        first_row=True

        if snake_direction==1 or (snake_direction!=3 and self.my_position[0]>=self.map_size[0]//2):
            first_row_checkpoints = [[col, self.my_position[1]] for col in range(self.my_position[0]+self.sight_range//2-1, self.map_size[0], self.sight_range-1)]
            reverse=True
        else:
            first_row_checkpoints = [[col, self.my_position[1]] for col in range(self.my_position[0]-(self.sight_range//2-1), -1, -(self.sight_range-1))]

        for row in range(self.my_position[1], self.map_size[1], self.sight_range-1):
            if first_row:
                if first_row_checkpoints!=[]:
                    checkpoints.extend(first_row_checkpoints)
                first_row = False
                continue

            if reverse:
                row_checkpoints = [[col, row] for col in range(self.map_size[0]-(self.sight_range//2-1), 0, -(self.sight_range - 1))]
            else:
                row_checkpoints = [[col, row] for col in range(self.sight_range // 2 -1, self.map_size[0], self.sight_range - 1)]

            reverse = not reverse

            checkpoints.extend(row_checkpoints)

        if checkpoints:
            starting_row = self.map_size[1]%checkpoints[-1][1]
        else:
            starting_row = self.sight_range//2-1
        
        for row in range(starting_row, self.my_position[1], self.sight_range-1):
            if reverse:
                row_checkpoints = [[col, row] for col in range(self.map_size[0] - (self.sight_range // 2 -1), -1, -(self.sight_range - 1))]
            else:
                row_checkpoints = [[col, row] for col in range(self.sight_range // 2 -1, self.map_size[0], self.sight_range - 1)]

            reverse = not reverse
            checkpoints.extend(row_checkpoints)

        return checkpoints

    def generate_checkpoints(self):
        checkpoints = []

        if not self.traverse:
            return self.generate_no_traverse_checkpoints()

        snake_direction = self.last_direction
        first_row=True

        if snake_direction == None or snake_direction==1 or (snake_direction!=3 and self.my_position[0]>=self.map_size[0]//2):
                first_row_checkpoints = [[col, self.my_position[1]] for col in range(self.my_position[0]+self.sight_range//2-1, self.map_size[0], self.sight_range-1)]
        else:
            first_row_checkpoints = [[col, self.my_position[1]] for col in range(self.my_position[0]-(self.sight_range//2-1), 0, -(self.sight_range-1))]

        for row in range(self.my_position[1], self.map_size[1], self.sight_range-1):
            if first_row:
                if first_row_checkpoints!=[]:
                    checkpoints.extend(first_row_checkpoints)
                first_row = False
                continue

            row_checkpoints = [[col, row] for col in range(self.sight_range // 2 -1, self.map_size[0], self.sight_range - 1)]

            checkpoints.extend(row_checkpoints)

        for row in range(self.sight_range//2-1, self.my_position[1], self.sight_range-1):
            row_checkpoints = [[col, row] for col in range(self.sight_range // 2 -1, self.map_size[0], self.sight_range - 1)]

            checkpoints.extend(row_checkpoints)

        return checkpoints
    
    
    def get_sight_info(self):
        food = []
        superfood = []
        enemy_snake = []
        for key in self.state['sight']:
            for key2 in self.state['sight'][key]:
                if self.state['sight'][key][key2] == 2:
                    food.append([int(key), int(key2)])
                elif self.state['sight'][key][key2] == 3:
                    superfood.append([int(key), int(key2)])
                elif self.state['sight'][key][key2] == 4:
                    if self.body and [int(key), int(key2)] not in self.body:
                        enemy_snake.append([int(key), int(key2)])

        return food, superfood, enemy_snake
    
    def find_closest_food(self, food_list):
        min_distance = float('inf')
        closest_food = None

        for food in food_list:
            distance = math.dist(self.my_position, food)
            if distance < min_distance:
                min_distance = distance
                closest_food = food[:2]

        return closest_food


    def calc_Min_Distance(self, p1, p2, map_size):
        x1, y1 = p1
        x2, y2 = p2
        width, height = map_size

        dx = min(abs(x1 - x2), width - abs(x1 - x2))
        dy = min(abs(y1 - y2), height - abs(y1 - y2))

        return dx + dy  
    
    def error(self):
        if self.key == "":
            return self.key
        snake_head = self.body[0]
        left = [snake_head[0]-1, snake_head[1]] if snake_head[0]-1 != -1 else [47,snake_head[1]]
        right = [snake_head[0]+1, snake_head[1]] if snake_head[0]+1 != 48 else [0,snake_head[1]]
        up = [snake_head[0], snake_head[1]-1] if snake_head[1]-1 != -1 else [snake_head[0],23]
        down = [snake_head[0], snake_head[1]+1] if snake_head[1]+1 != 23 else [snake_head[0],0]
        directions = {
            "left": left,
            "right": right,
            "up": up,
            "down": down,
        }
        valid_moves = []
        for direction, position in directions.items():
            if position not in self.walls and position not in self.body:
                # Check for boundaries only if self.traverse is False
                if self.traverse or (0 <= position[0] < self.map_size[0] and 0 <= position[1] < self.map_size[1]):
                    valid_moves.append(direction)

        if "up" in valid_moves:
            self.key ="w"
            self.last_direction =0
        elif "down" in valid_moves:
            self.key ="s"
            self.last_direction =2
        elif "right" in valid_moves:
            self.key="d"
            self.last_direction =1
        elif "left" in valid_moves:
            self.key="a"
            self.last_direction =3
        else:
            if self.last_direction ==0:
                self.key = "w"
            elif self.last_direction ==2:
                self.key="s"
            elif self.last_direction ==3:
                self.key="a"
            elif self.last_direction==1:
                self.key="d"

        return self.key
