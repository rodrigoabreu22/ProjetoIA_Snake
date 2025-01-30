# Module: tree_search
# 
# This module provides a set o classes for automated
# problem solving through tree search:
#    SearchDomain  - problem domains
#    SearchProblem - concrete problems to be solved
#    SearchNode    - search tree nodes
#    SearchTree    - search tree with the necessary methods for searhing
#
#  (c) Luis Seabra Lopes
#  Introducao a Inteligencia Artificial, 2012-2020,
#  Inteligência Artificial, 2014-2023

from abc import ABC, abstractmethod
import time

# Dominios de pesquisa
# Permitem calcular
# as accoes possiveis em cada estado, etc
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass


# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal
    def goal_test(self, state):
        return self.domain.satisfies(state.state[0],self.goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self,state: str,parent, cost, heuristic=None, action=None): 
        self.state = state
        self.parent = parent
        self.depth = self.calc_depth()
        self.cost = cost
        self.heuristic = heuristic
        self.action = action

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"
    def __repr__(self):
        return str(self)
    def in_parent(self, state):
        if self.parent == None:
            return False
        
        if self.parent.state[0] == state[0]:
            return True
        
        if self.parent.state[0] == state[1]:
            return True
        
        return self.parent.in_parent(state)
    
    def calc_depth(self):
        if self.parent == None:
            return 0
        return self.parent.calc_depth() + 1

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self,problem, strategy='breadth', fps=10): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0)
        self.open_nodes = [root]
        self.strategy = strategy
        self.solution = None
        self.non_terminals = 0
        self.highest_cost_nodes = [root]
        self.total_depth = 0
        self.average_depth = 0
        self.time = time.time()
        self.fps = fps

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self,node):
        if node.parent == None:
            return [node.state[0]]
        path = self.get_path(node.parent)
        path.append(node.state[0])
        return(path)
    
    @property
    def length(self):
        if self.solution:
            return self.solution.depth
        return 0
    
    @property
    def terminals(self):
        return len(self.open_nodes) + 1
    
    @property
    def avg_branching(self):
        return (self.terminals + self.non_terminals - 1) / self.non_terminals
    
    @property
    def cost(self):
        return self.solution.cost if self.solution else 0
    
    @property
    def plan(self):
        return self.get_plan(self.solution)
    
    def get_plan(self, node):
        if node.parent == None:
            return []
        plan = self.get_plan(node.parent)
        plan += [node.action]
        return plan

    # procurar a solucao
    def search(self, limit=None):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)
            if self.problem.goal_test(node):
                self.solution = node
                return self.get_path(node)
            lnewnodes = []

            self.non_terminals +=1

            if limit != None and node.depth >= limit:
                continue

            for a in self.problem.domain.actions(node.state):
                if time.time() - self.time > (1/self.fps) - 0.008:
                    return self.get_path(node)

                newstate = self.problem.domain.result(node.state,a)

                if not node.in_parent(newstate) and self.problem.domain.cost(node.state, a) <= 50000:

                    cost = self.problem.domain.cost(node.state, a)

                    heuristic = self.problem.domain.heuristic(newstate, self.problem.goal)

                    newnode = SearchNode(newstate,node, node.cost + cost, heuristic, a)

                    lnewnodes.append(newnode)

                    # calcular os nós com maior custo acumulado
                    if self.highest_cost_nodes[0].cost < newnode.cost:
                        self.highest_cost_nodes = [newnode]
                    elif self.highest_cost_nodes[0].cost == newnode.cost:
                        self.highest_cost_nodes.append(newnode)

                    self.total_depth += newnode.depth

            self.add_to_open(lnewnodes)
            self.average_depth = self.total_depth / (self.non_terminals + self.terminals - 1)
        return None

    # juntar novos nos a lista de nos abertos de acordo com a estrategia
    def add_to_open(self,lnewnodes):
        if self.strategy == 'breadth':
            self.open_nodes.extend(lnewnodes)
        elif self.strategy == 'depth':
            self.open_nodes[:0] = lnewnodes
        elif self.strategy == 'uniform':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda x: x.cost)
        elif self.strategy == 'greedy':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda x: x.heuristic)
        elif self.strategy == 'a*':
            self.open_nodes.extend(lnewnodes)
            self.open_nodes.sort(key = lambda x: x.heuristic + x.cost)