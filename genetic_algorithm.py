import numpy as np
import random

"""
One array for weights, one array for biases, one array for tuple of ID and score
    weights: [[weight set 1, weight set 2, weight set 3] for i in range (pop_size)]
    biases: [[bias set 1, bias set 2, bias set 3] for i in range (pop_size)]
    ID and score: [(ID, score) for i in range (pop_size)] SORTED from highest to lowest
        ID corresponds to the index of the respective snake in the weights and biases array
"""
def generate_next_gen(array_of_scores, array_of_weights, array_of_biases):
    #Input:  Array of scores, array of weights, array of biases, number of individuals in population
    #        Note: The number of individuals in old and new population is the same = FIXED = 400
    #Output: Array of weights and array of biases for next generation

    new_weights = []
    new_biases = []
    print(array_of_scores[0:10])
    print(array_of_weights[0:10][2])

    #Recombination
    for _ in range(400):
        parents = roulette_selection_double(array_of_scores)
        offspring_weight, offspring_bias = discrete_recombination(parents[0], parents[1], array_of_weights, array_of_biases)
        new_weights.append(offspring_weight)
        new_biases.append(offspring_bias)

    print("After recomb")
    print(array_of_scores[0:10])
    print(array_of_weights[0:10][2])

    #Mutation
    for i in range(300):
        mutated_weight, mutated_bias = mutation(array_of_scores[i][0], 0.05, array_of_weights, array_of_biases)
        new_weights.append(mutated_weight)
        new_biases.append(mutated_bias)

    #Duplication
    for i in range(100):
        new_weights.append(array_of_weights[array_of_scores[i][0]])
        new_biases.append(array_of_biases[array_of_scores[i][0]])

    #Random
    for i in range(200):
        W1 = 0.01 * np.random.randn(28,8)
        W2 = 0.01 * np.random.randn(8,4)
        W3 = 0.01 * np.random.randn(4,4)

        B1 = np.zeros(8)
        B2 = np.zeros(4)
        B3 = np.zeros(4)

        new_weights.append((W1, W2, W3))
        new_biases.append((B1, B2, B3))
    
    return new_weights, new_biases

def roulette_selection_double(array_of_scores):
    #Input:  Array of scores
    #Output: tuple of IDs of two chromosomes that will be parents for crossover
    
    parent1 = roulette_selection_single(array_of_scores)
    parent2 = roulette_selection_single(array_of_scores)

    return ((parent1, parent2))

def roulette_selection_single(array_of_scores):
    total_scores = 0
    for i in range(400):
        total_scores += array_of_scores[i][1]

    probability_array = []
    for i in range(400):
        probability_array.append((array_of_scores[i][0], array_of_scores[i][1]/total_scores))

    rolled = random.uniform(0,1)

    current_sum = probability_array[0][1]
    idx = 0
    while (current_sum < rolled):
        idx += 1
        current_sum += probability_array[idx][1]

    return (probability_array[idx][0])

def discrete_recombination(ID1, ID2, array_of_weights, array_of_biases):
    W1, B1 = discrete_recombination_single(ID1, ID2, array_of_weights, array_of_biases, 8, 28, 0)
    W2, B2 = discrete_recombination_single(ID1, ID2, array_of_weights, array_of_biases, 4, 8, 1)
    W3, B3 = discrete_recombination_single(ID1, ID2, array_of_weights, array_of_biases, 4, 4, 2)

    weights_tuple = (W1, W2, W3)
    bias_tuple = (B1, B2, B3)

    return weights_tuple, bias_tuple

def discrete_recombination_single(ID1, ID2, array_of_weights, array_of_biases, weight_col, weight_row, weight_index):
    #Input:  IDs of parents, array of weights, array of biases
    #Output: offspring weights and biases to be added to new weights and new biases respectively
    """
        Intinya, for each weight, each parent has an equal chance of passing down their weight, di gacha aja
        Weight row = bias row
    """

    offspring_weight = np.zeros((weight_row, weight_col)) 
    offspring_bias = np.zeros((weight_col))

    #Assigning new weight values
    for i in range(weight_row):
        for j in range(weight_col):
            rolled = random.uniform(0,1)
            if (rolled > 0.5):
                offspring_weight[i][j] = (array_of_weights[ID2][weight_index].copy())[i][j]
            else:
                offspring_weight[i][j] = (array_of_weights[ID1][weight_index].copy())[i][j]

    #Assigning new bias values
    for i in range(weight_col):
        rolled = random.uniform(0,1)
        if (rolled > 0.5):
            offspring_bias[i] = (array_of_biases[ID2][weight_index].copy())[i]
        else:
            offspring_bias[i] = (array_of_biases[ID1][weight_index].copy())[i]

    return offspring_weight, offspring_bias

def mutation(ID, mutation_rate, array_of_weights, array_of_biases):
    W1, B1 = mutation_single(ID, mutation_rate, array_of_weights, array_of_biases, 8, 28, 0)
    W2, B2 = mutation_single(ID, mutation_rate, array_of_weights, array_of_biases, 4, 8, 1)
    W3, B3 = mutation_single(ID, mutation_rate, array_of_weights, array_of_biases, 4, 4, 2)

    weights_tuple = (W1, W2, W3)
    bias_tuple = (B1, B2, B3)

    return weights_tuple, bias_tuple

def mutation_single(ID, mutation_rate, array_of_weights, array_of_biases, weight_col, weight_row, weight_index):
    #Input:  ID of chromosome, mutation rate, mutation size, array of weights, array of biases
    #Output: new weights and biases to be added to new weights and new biases respectively
    
    mutated_weight = array_of_weights[ID][weight_index].copy()
    mutated_bias = array_of_biases[ID][weight_index].copy()

     #Assigning new weight values
    for i in range(weight_row):
        for j in range(weight_col):
            mutation_size = np.random.normal(0, 0.1)
            rolled = random.uniform(0,1)
            if (rolled <= mutation_rate):
                mutated_weight[i][j] += mutation_size
            
            # if (mutated_weight[i][j] > 1):
            #     mutated_weight[i][j] -= 2*mutation_size

    #Assigning new bias values
    for i in range(weight_col):
        mutation_size = np.random.normal(0, 0.1)
        rolled = random.uniform(0,1)
        if (rolled <= mutation_rate):
            mutated_bias[i] += mutation_size
        
        # if (mutated_bias[i] > 1):
        #         mutated_bias[i] -= 2*mutation_size
    
    return mutated_weight, mutated_bias
