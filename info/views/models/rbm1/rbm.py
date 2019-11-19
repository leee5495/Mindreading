# -*- coding: utf-8 -*-
"""
RBM for book recommendation
with Python Torch


"""

"""BUILD MODEL"""
#import torch.utils.data
import numpy as np
import torch
import torch.nn as nn #for neural networks
import matplotlib.pyplot as plt




class RBM(nn.Module):

    def __init__(self, num_visible, num_hidden, k, learning_rate=1e-2, momentum_coefficient=0.5, weight_decay=1e-4, import_model=None):
        super(RBM, self).__init__()
        self.num_visible = num_visible
        self.num_hidden = num_hidden
        self.k = k
        self.learning_rate = learning_rate
        self.momentum_coefficient = momentum_coefficient
        self.weight_decay = weight_decay

        self.weights = torch.randn(num_visible, num_hidden) * 0.1
        self.visible_bias = torch.ones(num_visible) * 0.5
        self.hidden_bias = torch.zeros(num_hidden)

        self.weights_momentum = torch.zeros(num_visible, num_hidden)
        self.visible_bias_momentum = torch.zeros(num_visible)
        self.hidden_bias_momentum = torch.zeros(num_hidden)
        
        if import_model:
            self.weights = import_model['W']
            self.visible_bias = import_model['b_h']
            self.hidden_bias = import_model['b_h']
            

    def sample_hidden(self, visible_probabilities):
        hidden_activations = torch.matmul(visible_probabilities, self.weights) + self.hidden_bias
        hidden_probabilities = self._sigmoid(hidden_activations)
        return hidden_probabilities

    def sample_visible(self, hidden_probabilities):
        visible_activations = torch.matmul(hidden_probabilities, self.weights.t()) + self.visible_bias
        visible_probabilities = self._sigmoid(visible_activations)
        return visible_probabilities

    def contrastive_divergence(self, input_data):
        # Positive phase
        positive_hidden_probabilities = self.sample_hidden(input_data)
        positive_hidden_activations = (positive_hidden_probabilities >= self._random_probabilities(self.num_hidden)).float()
        positive_associations = torch.matmul(input_data.t(), positive_hidden_activations)

        # Negative phase
        hidden_activations = positive_hidden_activations

        for step in range(self.k):
            visible_probabilities = self.sample_visible(hidden_activations)
            hidden_probabilities = self.sample_hidden(visible_probabilities)
            hidden_activations = (hidden_probabilities >= self._random_probabilities(self.num_hidden)).float()

        negative_visible_probabilities = visible_probabilities
        negative_hidden_probabilities = hidden_probabilities

        negative_associations = torch.matmul(negative_visible_probabilities.t(), negative_hidden_probabilities)

        # Update parameters
        self.weights_momentum *= self.momentum_coefficient
        self.weights_momentum += (positive_associations - negative_associations)

        self.visible_bias_momentum *= self.momentum_coefficient
        self.visible_bias_momentum += torch.sum(input_data - negative_visible_probabilities, dim=0)

        self.hidden_bias_momentum *= self.momentum_coefficient
        self.hidden_bias_momentum += torch.sum(positive_hidden_probabilities - negative_hidden_probabilities, dim=0)

        batch_size = input_data.size(0)

        self.weights += self.weights_momentum * self.learning_rate / batch_size
        self.visible_bias += self.visible_bias_momentum * self.learning_rate / batch_size
        self.hidden_bias += self.hidden_bias_momentum * self.learning_rate / batch_size

        self.weights -= self.weights * self.weight_decay  # L2 weight decay

        # Compute reconstruction error
        error = torch.mean((input_data - negative_visible_probabilities)**2)

        return error

    def _sigmoid(self, x):
        return 1 / (1 + torch.exp(-x))

    def _random_probabilities(self, num):
        random_probabilities = torch.rand(num)

        return random_probabilities

    def predict(self,input_data) :
        q_h0 = self._sigmoid(torch.matmul(input_data, self.weights) + self.hidden_bias)
        prediction = self._sigmoid(torch.matmul(q_h0, self.weights.t()) + self.visible_bias)
  
        return prediction


def test_rbm(sfile,inputs,vis, hidden, cd_k) :
    # .. to load your previously training model:
    rbm = RBM2(vis, hidden, cd_k)
    rbm.load_state_dict(torch.load(sfile))
    
    prediction = rbm.predict(inputs)
      
    return prediction  

def run_rbm(train_data, vis, hidden, cd_k,n_epoch,batch_size,sfile) :
    rbm = RBM(num_visible=vis, num_hidden=hidden, k = cd_k )

    for epoch in range(n_epoch):
        epoch_error = 0.0
        for i in range(0, vis - batch_size, batch_size): 
            vk = train_data[i:i+batch_size]
            batch_error = rbm.contrastive_divergence(vk)
      

            epoch_error += batch_error

        print('Epoch Error (epoch=%d): %.4f' % (epoch, epoch_error))

    torch.save(rbm.state_dict(), sfile)
   
    return rbm

if __name__ == "__main__":
    # manage data : data를 올려줌.
    
    from manage_data import DATA
    
    """OPEN DATA"""
    picklepath = "C:\\RBM\\rbm_v3.1\\pickle\\"
    data = DATA(picklepath)
        
    """ MAKE MODELS """
    # hyperparameters setting
    len_rating_vect = len(data.rating_vect_train[0])
    num_data = len(data.rating_vect_train)
    
    latent_dim = 50
    epochs = 15
    batchsize = 20
    cd_k = 5
    print("test : ", len(data.rating_vect_train))    
   
    training_set = torch.FloatTensor(data.rating_vect_train)   
    len_rating_vect = len(training_set[0])
    num_data = len(training_set)
    rating_rbm = RBM(num_visible=len_rating_vect, num_hidden=latent_dim, k = cd_k )

    errors = []
    for epoch in range(epochs):
        epoch_error = 0.0
        for i in range(0, num_data - batchsize, batchsize): 
            vk = training_set[i:i+batchsize]
            batch_error = rating_rbm.contrastive_divergence(vk)
            epoch_error += batch_error

        print('Epoch Error (epoch=%d): %.4f' % (epoch, epoch_error/num_data))
        errors.append(epoch_error)
       
    plt.plot(errors)
    plt.ylabel('Error')
    plt.xlabel('Epoch')
    plt.show()
    
    training_set2 = torch.FloatTensor(np.concatenate([data.rating_vect_train, data.meta_vect_train, data.lda_vect_train], axis=1))
    len_rating_vect = len(training_set2[0])
    num_data = len(training_set2)
    lda_rbm = RBM(num_visible=len_rating_vect, num_hidden=latent_dim, k = cd_k )
    
    errors = []

    for epoch in range(epochs):
        epoch_error = 0.0
        for i in range(0, num_data - batchsize, batchsize): 
            vk = training_set2[i:i+batchsize]
            batch_error = lda_rbm.contrastive_divergence(vk)
            epoch_error += batch_error

        print('Epoch Error (epoch=%d): %.4f' % (epoch, epoch_error/num_data))
        errors.append(epoch_error)
    plt.plot(errors)
    plt.ylabel('Error')
    plt.xlabel('Epoch')
    plt.show()
  
    """PREDICT WITH MODELS"""
    from explain_prediction import Explanation
    
    testUser = training_set2[100]
  
    
    explain_module = Explanation(picklepath)

    rec = lda_rbm.predict(testUser).cpu().data.numpy()
    print(rec)
    #print(np.array(rec)[0])
    explain_module.explain_prediction(rec, np.array(testUser))
    