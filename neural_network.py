import numpy as np
import random

#X is in the form of:
""" Number of rows: The number batches
    Number of colums: The number of inputs
"""
#X = 0.1 * np.random.randn(5,4) #(batches, inputs)

class Layer:
    def __init__(self, input_number, neuron_number, activation_choice, weight, bias):
        self.weight = weight
        self.bias = bias
        self.activation_choice = activation_choice
    
    def forward(self, inputs):
        if self.activation_choice == 1:
            self.output = self.activation_relu(np.dot(inputs, self.weight) + self.bias)
        elif self.activation_choice == 2:
            self.output = self.activation_tanh(np.dot(inputs, self.weight) + self.bias)
        elif self.activation_choice == 3:
            self.output = self.activation_sigmoid(np.dot(inputs, self.weight) + self.bias)
        elif self.activation_choice == 4:
            self.output = self.activation_softmax(np.dot(inputs, self.weight) + self.bias)

    def activation_sigmoid(self, inputs):
        return 1/(1 + np.exp(-inputs))

    def activation_relu(self, inputs):
        return np.maximum(0, inputs)

    def activation_tanh(self, inputs):
        return np.tanh(inputs) 

    def activation_softmax(self, inputs):
        return np.exp(inputs) / np.sum(np.exp(inputs), axis=0)

#DEBUG
# hidden_layer1 = Layer(4,3,1)
# hidden_layer1.forward(X)

# hidden_layer2 = Layer(3,4,1)
# hidden_layer2.forward(hidden_layer1.output)

# print(X)
# print(hidden_layer1.output)
# print(hidden_layer2.output)
