# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 20:07:54 2019

@author: 1615055
"""

import numpy as np
from keras.models import Model
from keras.layers import Input
from keras.layers import Dense

class RBM:
    
    def __init__(self, num_visible, num_hidden, import_model=None):
        self.num_visible = num_visible
        self.num_hidden = num_hidden
        
        visible = Input(shape=(num_visible,))
        hidden = Dense(num_hidden, activation="sigmoid")(visible)
        #output = Dense(num_visible, activation="sigmoid")(hidden)
        #self.model = Model(inputs=visible, outputs=output)
        self.hidden_model = Model(inputs=visible, outputs=hidden)
        
        if import_model:
            self.weights = import_model['W']
            self.visible_bias = import_model['b_v']
            self.hidden_bias = import_model['b_h']
            """
            self.model.layers[1].set_weights([self.weights, self.hidden_bias])
            self.model.layers[2].set_weights([self.weights.T, self.visible_bias])
            """
            self.hidden_model.layers[1].set_weights([self.weights, self.hidden_bias])
            self.hidden_model._make_predict_function()
            
            
    """
    def predict(self,input_data) :
        input_data = np.reshape(input_data, (1,-1))
        prediction = self.model.predict(input_data)
        return prediction
    """
    
    def sample_hidden(self,input_data) :
        input_data = np.reshape(input_data, (1,-1))
        hidden = self.hidden_model.predict(input_data)
        return hidden