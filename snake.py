import pygame
import sys
import random
import csv
from genetic_algorithm import *
from neural_network import *

pygame.init()
pygame.display.set_caption('SnakeAI')

#Screen setup
cell_size = 40
cell_numbers = 10
screen = pygame.display.set_mode((cell_size*cell_numbers+10,cell_size*cell_numbers+35))
surface1 = pygame.Surface((cell_size*cell_numbers,cell_size*cell_numbers)) #playing arena

#Clock setup
clock = pygame.time.Clock()

#Colors
COLOR_RED = (168,50,50)
COLOR_BLACK = (0,0,0)
COLOR_LIGHT = (247,247,247)
COLOR_DARK = (219,219,219)

#Font
font = pygame.font.Font('freesansbold.ttf', 20)

#Additional global variables
#Directions - [RIGHT, LEFT, UP, DOWN]
directions = [(0,1), (0,-1), (-1,0), (1,0)]
#Vision direction:
""" 012
    3H4
    567
"""
vision_direction = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]


#Apple
class Apple:
    def __init__(self):
        self.x = random.randint(0,cell_numbers-1)
        self.y = random.randint(0,cell_numbers-1)
        self.coordinate = (self.x, self.y)

    def draw_apple(self):
        apple_rect = pygame.Rect(cell_size*self.y, cell_size*self.x, cell_size, cell_size)
        pygame.draw.rect(surface1, COLOR_RED, apple_rect)

#Snake
class Snake:
    def __init__(self, ID):
        self.ID = ID
        self.x = (cell_numbers-1)//2
        self.y = (cell_numbers-1)//2
        self.length = 3
        self.body_positions = [(self.x, self.y), (self.x, self.y-1),  (self.x, self.y-2)]
        self.head = self.body_positions[0]
        self.direction = directions[0]
        self.is_eating = False
        self.is_alive = True
        self.apples_eaten = 0
        self.steps_taken = 0
        self.steps_remaining = 100
        self.fitness = 0

    def move(self):
        if (self.is_eating):
            body_positions_temp = self.body_positions
            body_positions_temp.insert(0, (body_positions_temp[0][0] + self.direction[0],\
                 body_positions_temp[0][1] + self.direction[1]))
            self.body_positions = body_positions_temp
            self.is_eating = False
        else:
            body_positions_temp = self.body_positions[:-1]
            body_positions_temp.insert(0, (body_positions_temp[0][0] + self.direction[0],\
                 body_positions_temp[0][1] + self.direction[1]))
            self.body_positions = body_positions_temp
        self.head = self.body_positions[0]
        self.steps_taken += 1
        self.steps_remaining -= 1

    def distance_vision(self, direction_number, apple_coordinate):
        self.dist_to_wall = 1
        self.dist_to_apple = 1
        self.dist_to_self = 1
        current_pos_x = self.head[0]
        current_pos_y = self.head[1]
        current_pos_x += vision_direction[direction_number][0]
        current_pos_y += vision_direction[direction_number][1]

        self.wall_found = False
        self.apple_found = False
        self.self_found = False

        while (not self.wall_found):
            #Check for apple
            if (not self.apple_found):
                if ((current_pos_x, current_pos_y) == apple_coordinate):
                    self.apple_found = True
                else:
                    self.dist_to_apple += 1

            #Check for self
            if (not self.self_found):
                if ((current_pos_x, current_pos_y) in self.body_positions):
                    self.self_found = True
                else:
                    self.dist_to_self += 1
            
            #Check for wall
            if (current_pos_x <= 0 or current_pos_x >= cell_numbers-1 \
                or current_pos_y <= 0 or current_pos_y >= cell_numbers-1):
                self.wall_found = True
            else:
                self.dist_to_wall += 1
                current_pos_x += vision_direction[direction_number][0]
                current_pos_y += vision_direction[direction_number][1]
        
        if (not self.apple_found):
            self.dist_to_apple = -99
        if (not self.self_found):
            self.dist_to_self = -99
        return [0.01*self.dist_to_wall, 0.01*self.dist_to_apple, 0.01*self.dist_to_self]

    def binary_vision(self, direction_number, apple_coordinate):
        self.is_wall = 0
        self.is_apple = 0
        self.is_self = 0

        current_pos_x = self.head[0] + vision_direction[direction_number][0]
        current_pos_y = self.head[1] + vision_direction[direction_number][1]

        if ((current_pos_x, current_pos_y) in self.body_positions):
            self.is_self = 1
        if ((current_pos_x, current_pos_y) == apple_coordinate):
            self.is_apple = 1
        if (current_pos_x <= 0 or current_pos_x >= cell_numbers-1 \
            or current_pos_y <= 0 or current_pos_y >= cell_numbers-1):
            self.is_wall = 1

        return [self.is_wall, self.is_apple, self.is_self]

    def comb_vision(self, direction_number, apple_coordinate):

        self.wall_found = False
        
        self.is_wall = 0
        self.is_apple = 0
        self.is_self = 0

        current_pos_x = self.head[0] + vision_direction[direction_number][0]
        current_pos_y = self.head[1] + vision_direction[direction_number][1]

        #Check for wall
        if (current_pos_x < 0 or current_pos_x > cell_numbers-1 \
                or current_pos_y < 0 or current_pos_y > cell_numbers-1):
                self.is_wall = 1

        while (not(self.wall_found)):
            #Check for apple
            if (self.is_apple == 0):
                if ((current_pos_x, current_pos_y) == apple_coordinate):
                    self.is_apple = 1

            #Check for self
            if (self.is_self):
                if ((current_pos_x, current_pos_y) in self.body_positions):
                    self.is_self = 1
            
            #Check for wall
            if (current_pos_x < 0 or current_pos_x > cell_numbers-1 \
                or current_pos_y < 0 or current_pos_y > cell_numbers-1):
                self.wall_found = True
            else:
                current_pos_x += vision_direction[direction_number][0]
                current_pos_y += vision_direction[direction_number][1]

        return [self.is_wall, self.is_apple, self.is_self]

    def eat_apple(self):
        self.length += 1
        self.apples_eaten += 1
        self.is_eating = True
        self.steps_remaining = 100

    def  draw_snake(self):
        for body in self.body_positions:
            snake_body_rect = pygame.Rect(cell_size*body[1], cell_size*body[0], cell_size, cell_size)
            pygame.draw.rect(surface1, COLOR_BLACK, snake_body_rect)

    def calculate_fitness(self):
        self.fitness = self.steps_taken + (2**(self.apples_eaten) + ((self.apples_eaten**2.1)*500)) \
            - ((self.apples_eaten**1.2)*((0.25*self.steps_taken)**1.3))


#Main Game
class Game():
    def __init__(self, snake_ID):
        self.new_game(snake_ID)

    def update_screen(self):
        self.check_eating()
        self.check_life()
        self.snake.move()
        self.draw_board()
        self.get_input()

    def update_score(self):
        self.text = font.render(f'Score: {self.snake.length}', True, COLOR_BLACK)
        text_rect = self.text.get_rect()
        text_rect.center = (cell_size*cell_numbers // 2, 17)
        screen.blit(self.text, text_rect)

    def draw_board(self):
        screen.fill(COLOR_DARK)
        surface1.fill(COLOR_LIGHT)
        self.apple.draw_apple()
        self.snake.draw_snake()
        self.update_score()
        screen.blit(surface1,(5,30))
        
    def check_eating(self):
        if self.snake.head == self.apple.coordinate:
            self.snake.eat_apple()
            self.apple = Apple()
            while (self.apple.coordinate in self.snake.body_positions):
                self.apple = Apple()

    def check_life(self):
        self.check_hit_self()
        self.check_hit_wall()
        self.check_steps_available()
        if (not(self.snake.is_alive)):
            self.snake.calculate_fitness()
            #print(self.snake.ID, self.snake.fitness)

    def check_hit_self(self):
        if (self.snake.head in self.snake.body_positions[1:]):
            self.snake.is_alive = False
        
    def check_hit_wall(self):
        if ((self.snake.head[0] < 0) or (self.snake.head[0] > cell_numbers-1) or \
            (self.snake.head[1] < 0) or (self.snake.head[1] > cell_numbers-1)):
            self.snake.is_alive = False
    
    def check_steps_available(self):
        if (self.snake.steps_remaining == 0):
            self.snake.is_alive = False

    def get_input(self):
        #Saving the vision result as inputs for neural network
        self.nn_inputs = []
        for i in range(8):
            self.nn_inputs += self.snake.comb_vision(i, self.apple.coordinate)
        direction_array = [0,0,0,0]
        idx = directions.index(self.snake.direction)
        direction_array[idx] = 1
        self.nn_inputs += direction_array
        #DEBUG
        #print(self.nn_inputs)

    def run_game(self, snake_ID, array_of_weights, array_of_biases, show_display):
        
        self.show_display = show_display

        current_weights = array_of_weights[snake_ID]
        current_biases = array_of_biases[snake_ID]

        hidden_layer1 = Layer(28, 8, 1, current_weights[0], current_biases[0])
        hidden_layer2 = Layer(8, 8, 1, current_weights[1], current_biases[1])
        output_layer = Layer(8, 4, 4, current_weights[2], current_biases[2])

        while (self.snake.is_alive):
            self.update_screen()
            hidden_layer1.forward(self.nn_inputs)
            hidden_layer2.forward(hidden_layer1.output)
            output_layer.forward(hidden_layer2.output)

            #Gerakin snakenya berdasarkan hasil output layer
            next_dir = np.argmax(output_layer.output)
            if (next_dir == 0):
                if (self.snake.direction != directions[1]):
                    self.snake.direction = directions[next_dir]
            elif (next_dir == 1):
                if (self.snake.direction != directions[0]):
                    self.snake.direction = directions[next_dir]
            elif (next_dir == 2):
                if (self.snake.direction != directions[3]):
                    self.snake.direction = directions[next_dir]
            elif (next_dir == 3):
                if (self.snake.direction != directions[2]):
                    self.snake.direction = directions[next_dir]

            #clock.tick(500)

            if (self.show_display):
                pygame.display.update()
                clock.tick(25)
        

    def new_game(self, snake_ID):
        self.snake = Snake(snake_ID)
        self.apple = Apple()
        self.text = font.render(f'Score: {self.snake.length}', True, COLOR_BLACK)

class Generation:
    def __init__(self, total_population):
        #First iteration Initialization
        array_of_weights = []
        array_of_biases = []

        #Initialize weights - for first iteration only
        for _ in range(total_population):
            W1 = 0.01 * np.random.randn(28,8)
            W2 = 0.01 * np.random.randn(8,8)
            W3 = 0.01 * np.random.randn(8,4)

            B1 = np.zeros(8)
            B2 = np.zeros(8)
            B3 = np.zeros(4)

            array_of_weights.append((W1, W2, W3))
            array_of_biases.append((B1, B2, B3))

        self.new_generation(1, total_population, array_of_weights, array_of_biases)

    def new_generation(self, generation_no, total_population, weights_input, biases_input):
        self.best_score = 0
        current_indiv = 0
        array_of_scores = []
        self.game = Game(0)
        self.game.show_display = False
        print("Generation " + str(generation_no))
        for i in range(total_population):
            
            #Controls
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.game.show_display = True
                    elif event.key == pygame.K_LEFT:
                        self.game.show_display = False

            self.game.new_game(i)
            self.game.run_game(i, weights_input, biases_input, self.game.show_display)
            current_indiv += 1
            
            array_of_scores.append((i, self.game.snake.fitness))
            if (self.game.snake.length - 3 > self.best_score):
                self.best_score = self.game.snake.length - 3

        #Snake is dead
        array_of_scores.sort(key=lambda tup: tup[1]) #Sort fitness scores
        array_of_scores.reverse() #Descending order

        self.weights_output, self.biases_output = generate_next_gen(array_of_scores, weights_input, biases_input)
        self.best_weight = weights_input[array_of_scores[0][0]]
        self.best_bias = biases_input[array_of_scores[0][0]]

        #DEBUG
        for i in range(5):
            print(self.weights_output[300+i][2])
        
        
class Main:
    def __init__(self, total_generation, total_population):
        self.new_main(total_generation, total_population)

    def load(self, filename):
        pass

    def save(self, filename, array):
        writer = csv.writer(open(filename,"w"))
        for data in array:
            writer.writerow(data)
        #Use this twice, once to save the weights and another for the biases

    def new_main(self, total_generation, total_population):
        self.best_weights = []
        self.best_biases = []
        self.best_overall_score = 0

        self.generation = Generation(total_population)

        for n in range(2, total_generation+1):
            self.generation.new_generation(n, total_population, self.generation.weights_output, self.generation.biases_output)
            
            #Add the best weight and bias of the run
            self.best_weights.append(self.generation.best_weight)
            self.best_biases.append(self.generation.best_bias)

            #Update best score
            if (self.generation.best_score > self.best_overall_score):
                self.best_overall_score = self.generation.best_score

            #Stat print
            print("Best current generation score: " + str(self.generation.best_score))
            print("Best overall score: "+ str(self.best_overall_score))
            print()

            #Save best weights and biases
            self.save("weights.csv", self.best_weights)
            self.save("biases.csv", self.best_biases)

#New game initialization
start = Main(2500, 1000)
