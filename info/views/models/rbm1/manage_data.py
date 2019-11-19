# -*- coding: utf-8 -*-
"""
define class for opening data for training and validation

Created on Fri Jul  5 21:31:33 2019
@author: 1615055
"""

import pickle
import os
import numpy as np

class DATA:
    def __init__(self, picklepath, use_valid=True, valid_rate=0.2):        
        self.picklepath = picklepath
        self.use_valid = use_valid
        if use_valid:
            self.valid_rate=0.2
        
        self.open_datasets()
        
    
    def open_pickle(self, filename):
        with open(os.path.join(self.picklepath, filename), "rb") as fp:
            data = pickle.load(fp)
        return data
        
    def open_datasets(self):
        self.rating_vect_train = np.array(self.open_pickle("rating_vect_train"))
        self.meta_vect_train = np.array(self.open_pickle("meta_vect_train"))
        self.lda_vect_train = np.array(self.open_pickle("lda_vect_train"))
        
        if self.use_valid:
            data_array = np.concatenate([self.rating_vect_train, self.meta_vect_train, self.lda_vect_train], axis=1)
            np.random.seed(0)
            np.random.shuffle(data_array)

            rating_vect_shape = self.rating_vect_train.shape
            self.rating_vect_train = data_array[int(rating_vect_shape[0]*self.valid_rate):,:rating_vect_shape[1]]
            self.rating_vect_valid = data_array[:int(rating_vect_shape[0]*self.valid_rate),:rating_vect_shape[1]]

            meta_vect_shape = self.meta_vect_train.shape
            self.meta_vect_train = data_array[int(meta_vect_shape[0]*self.valid_rate):,rating_vect_shape[1]:rating_vect_shape[1]+meta_vect_shape[1]]
            self.meta_vect_valid = data_array[:int(meta_vect_shape[0]*self.valid_rate),rating_vect_shape[1]:rating_vect_shape[1]+meta_vect_shape[1]]

            lda_vect_shape = self.lda_vect_train.shape
            self.lda_vect_train = data_array[int(lda_vect_shape[0]*self.valid_rate):,rating_vect_shape[1]+meta_vect_shape[1]:]
            self.lda_vect_valid = data_array[:int(lda_vect_shape[0]*self.valid_rate),rating_vect_shape[1]+meta_vect_shape[1]:]
        
        self.rating_vect_test = self.open_pickle("rating_vect_test")
        self.meta_vect_test = self.open_pickle("meta_vect_test")
        self.lda_vect_test = self.open_pickle("lda_vect_test")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    