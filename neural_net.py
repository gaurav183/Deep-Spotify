import numpy as np
import random
import math


# num hidden layers is 1
class NeuralNet:
  def __init__(self, structure, learning_rate):
    """
    Initialize the Neural Network.

    - structure is a dictionary with the following keys defined:
        num_inputs
        num_outputs
        num_hidden
    - learning rate is a float that should be used as the learning
        rate coefficient in training

    When building your net, make sure to initialize your weights
    to random values in the range [-0.05, 0.05]. Specifically, you
    should use some transformation of 'np.random.rand(n,m).'
    """

    self.num_inputs = structure['num_inputs']
    self.num_outputs = structure['num_outputs']
    self.num_hidden = structure['num_hidden']
    self.learning_rate = learning_rate

    self.x = []

    self.w1 =(np.random.rand(self.num_inputs + 1, self.num_hidden) - 0.5)/10.0

    self.w2 = (np.random.rand(self.num_hidden, self.num_outputs) - 0.5)/10.0



  def apply_sigmoid(self, x):
    return float(1.0/float((1.0+math.e**(float(-1*x)))))

  def get_weights(self):
    """
    Returns (w1, w2) where w1 is a matrix representing the current
    weights from the input to the hidden layer and w2 is a similar
    matrix for the hidden to output layers. Specifically, w1[i,j]
    should be the weight from input node i to hidden unit j.
    """

    return (self.w1, self.w2)

  def forward_propagate(self, x):
    """
    Push the input 'x' through the network and returns the activations
    on the output nodes.

    - x is a numpy array representing an input to the NN

    Return a numpy array representing the activations of the output nodes.

    Hint: you may want to update state here, since you should call this
    method followed by back_propagate in your train method.
    """

    # add 1 for "bias"
    x = np.append(x, [1])
    self.x = x
    (w1, w2) = (self.w1, self.w2)
    product = np.dot([x], w1)
    for i in xrange(self.num_hidden):
        product[0][i] = self.apply_sigmoid(product[0][i])
    self.sigmoid_product = product 
    predicted=np.dot(product, w2)
    for i in xrange(self.num_outputs):
        predicted[0][i] = self.apply_sigmoid(predicted[0][i])
    self.predicted = predicted
    return predicted[0]


  def back_propagate(self, target):
    """
    Updates the weights of the NN for the last forward_propagate call.

    - target is the label of the last forward_propogate input
    """

    (w1, w2) = (self.w1, self.w2)
    predicted = self.predicted
    sigmoid_product = self.sigmoid_product
    delt2 = [float(0) for i in range(self.num_outputs)]
    for i in xrange(self.num_outputs):
        delt2[i] = float(predicted[0][i]*(1-predicted[0][i])*(target[i]-predicted[0][i]))
    temp  = np.multiply(w2, delt2)
    sum_temp= np.sum(temp, axis=1)
    delth=[[float(0)] for i in range(self.num_hidden)]
    for i in xrange(self.num_hidden):
        delth[i][0]=float(sigmoid_product[0][i]*(float(1)-sigmoid_product[0][i])*sum_temp[i])

    delt2_scaled = np.multiply(delt2, self.learning_rate)
    deriv_w2 = np.multiply(np.transpose(sigmoid_product), delt2_scaled) 
    delt1 = np.transpose(np.dot(delth, [self.x]))
    deriv_w1 = np.multiply(delt1, self.learning_rate)
    self.w2 =  np.add(w2, deriv_w2)
    self.w1 = np.add(w1, deriv_w1)


  def train(self, X, Y, iterations=100):
    """
    Trains the NN on observations X with labels Y.

    - X is a numpy matrix (array of arrays) corresponding to a series of
        observations. Each row is a new observation.
    - Y is a numpy matrix (array of arrays) corresponding to the labels
        of the observations.
    - iterations is how many passes over X should be completed.
    """
    for i in xrange(iterations):
        for j in xrange((X.shape)[0]):
            self.forward_propagate(X[j])
            #label = np.zeros(shape=(12,), dtype=np.float32)
            #label[Y[j]] = float(1)
            self.back_propagate(Y[j])

        err = self.test(X, Y)
        print "Epoch ", i, " Error = ", err

  def test(self, X, Y):
    """
    Tests the NN on observations X with labels Y.

    - X is a numpy matrix (array of arrays) corresponding to a series of
        observations. Each row is a new observation.
    - Y is a numpy matrix (array of arrays) corresponding to the labels
        of the observations.

    Returns the mean squared error.
    """

    wrong = float(0)
    for i in xrange((X.shape)[0]):
        self.forward_propagate(X[i])
        #prob = np.argmax(self.predicted[0])
        num_ones = (Y[i]==1).sum()
        num_ones = 1
        temp = (self.predicted[0]).argsort()[-num_ones:][::-1]
        indices = [i for i, x in enumerate(Y[i]) if x==1]
        #print "temp", temp
        #print "indices", indices
        #print "predicted", self.predicted
        for i in xrange(num_ones):
            if temp[i] not in indices:
                #print self.predicted
                #print "indices", indices
                wrong+=1
                break
        # correct = False
        # for i in xrange(num_ones):
        #     if temp[i] in indices:
        #         correct = True
        #         break
        # if correct==False:
        #     wrong+=1

            
    return float(wrong)/float((Y.shape)[0])
   


