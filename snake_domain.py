from tree_search import *
import math

class SnakeDomain(SearchDomain):
    def __init__(self, map, map_size, no_go, walls, traverse):
        self.map = map
        self.map_size = map_size
        self.no_go = no_go
        self.walls = walls
        self.traverse = traverse
    
    def actions(self, state):
        moves = []
        head = state[0]
        body = state[0:]

        if self.traverse:
            next_positions = {
                's': [head[0], (head[1] + 1) % self.map_size[1]],
                'w': [head[0], (head[1] - 1) % self.map_size[1]],
                'd': [(head[0] + 1) % self.map_size[0], head[1]],
                'a': [(head[0] - 1) % self.map_size[0], head[1]],
            }
        else:
            next_positions = {
                's': [head[0], head[1] + 1],
                'w': [head[0], head[1] - 1],
                'd': [head[0] + 1, head[1]],
                'a': [head[0] - 1, head[1],
                ]
            }
        
        for m in ['d', 'a', 's', 'w']:
            next = next_positions[m]

            if not self.traverse:
                if (next[0] < 0 or next[0] >= self.map_size[0] or 
                    next[1] < 0 or next[1] >= self.map_size[1] or 
                    next in self.walls or
                    next in body):
                    continue

            if  next not in body and next not in self.no_go:
                moves.append(m)

        return moves
            
        
    def result(self, state, action):
        new_state = state.copy()
        head = state[0]
        x = head[0]
        y = head[1]

        if action == 'd':
            new_state = [(x+1) % self.map_size[0], y]
        elif action == 'a':
            new_state = [(x-1) % self.map_size[0], y] 
        elif action == 's':
            new_state = [x, (y+1) % self.map_size[1]]
        elif action == 'w':
            new_state = [x, (y-1) % self.map_size[1]] 

        return [new_state]  + state[0:]

    def cost(self, state, action):
        new_state = self.result(state, action)
        head = new_state[0]

        # to avoid going against the body 
        if  head in new_state[1:]:
            return 100000
        
        if not self.traverse:
            if head[0] < 0 or head[0] >= self.map_size[0] or head[1] < 0 or head[1] >= self.map_size[1] or head in self.walls:
                return 100000
        return 1  

    def heuristic(self, state, goal_state):
        if not self.traverse:
            return math.dist(state[0], goal_state)
        return calc_Min_Distance(state, goal_state, self.map_size)       

    def satisfies(self, state, goal):
        return state == goal
    

#função auxiliar
def calc_Min_Distance(p1, p2, map_size):
    x1, y1 = p1[0]
    x2, y2 = p2
    width, height = map_size

    dx = min(abs(x1 - x2), width - abs(x1 - x2))
    dy = min(abs(y1 - y2), height - abs(y1 - y2))

    #return math.sqrt(dx**2 + dy**2) 
    return dx + dy 