# -*- coding: utf-8 -*-
"""
Module for prediction explanation

explain prediction vector with "explain_prediction" function:
    input:  output_vector - output of RBM
            input_vector - original vector for prediction
            top_n - show top n books from the output
            use_meta - whether to explain top n genres, authors, publishers from the output
    output: explanation of the output vector

Created on Sun Jul  7 18:05:55 2019
@author: 1615055
"""

import pickle
import pandas as pd

import os
import numpy as np
from gensim.test.utils import datapath as dp
from gensim.similarities import MatrixSimilarity

class Explanation:
    
    def __init__(self, picklepath):
        with open(os.path.join(picklepath, "book_id_to_int"), "rb") as fp:
            self.book_id_to_int = pickle.load(fp)
            self.int_to_book_id = {v:k for k,v in self.book_id_to_int.items()}
        with open(os.path.join(picklepath, "genre_to_int"), "rb") as fp:
            self.genre_to_int = pickle.load(fp)
            self.int_to_genre = {v:k for k,v in self.genre_to_int.items()}
        with open(os.path.join(picklepath, "author_to_int"), "rb") as fp:
            self.author_to_int = pickle.load(fp)
            self.int_to_author = {v:k for k,v in self.author_to_int.items()}
        with open(os.path.join(picklepath, "publisher_to_int"), "rb") as fp:
            self.publisher_to_int = pickle.load(fp)
            self.int_to_publisher = {v:k for k,v in self.publisher_to_int.items()}
        with open(os.path.join(picklepath, "meta"), "rb") as fp:
            self.meta= pickle.load(fp)
        with open(os.path.join(picklepath, "lda_index_to_title"), "rb") as fp:
            self.lda_index_to_title= pickle.load(fp)
        
        index_file = dp(os.path.join(picklepath, "lda_similarity.index"))
        self.index = MatrixSimilarity.load(index_file)
            
        self.num_books = len(self.book_id_to_int)
        self.num_genre = len(self.genre_to_int)
        self.num_author = len(self.author_to_int)
        self.num_publisher = len(self.publisher_to_int)
        
            
    def explain_prediction(self, output_vector, input_vector, top_n=5, use_meta=False, use_lda=False):
        print("debug:", output_vector)
        np.array(output_vector)
        np.array(input_vector)
        rating_output = output_vector[:self.num_books]
        rating_input = input_vector[:self.num_books]
        
        # explain input
        print("Explain input")
        in_rating_ind = np.reshape(np.argwhere(rating_input>0), (-1,))
        for i in in_rating_ind:
            book_meta = self.meta[self.meta.book_id == i].iloc[0]
            print(" title:     ", book_meta.title)
            print(" author:    ", self.int_to_author[book_meta.author])
            print(" genre:     ", [self.int_to_genre[j] for j in book_meta.genre])
            print(" publisher: ", self.int_to_publisher[book_meta.publisher])
            print(" rating:    ", rating_input[i]*5)
            print()
        
        # explain output
        print("\n\nExplain output")
        rating_output[in_rating_ind] = 0
        top_n_ind = (-rating_output).argsort()[:top_n]
        for i in top_n_ind:
            book_meta = self.meta[self.meta.book_id == i].iloc[0]
            print(" title:     ", book_meta.title)
            print(" author:    ", self.int_to_author[book_meta.author])
            print(" genre:     ", [self.int_to_genre[j] for j in book_meta.genre])
            print(" publisher: ", self.int_to_publisher[book_meta.publisher])
            print(" score:     ", output_vector[i])
            print()
            
        if use_meta:
            print("\n\nExplain output meta")
            genre_output = output_vector[self.num_books:self.num_books+self.num_genre]
            author_output = output_vector[self.num_books+self.num_genre:self.num_books+self.num_genre+self.num_author]
            publisher_output = output_vector[self.num_books+self.num_genre+self.num_author:self.num_books+self.num_genre+self.num_author+self.num_publisher]
            
            print(" Genre: ")
            top_n_ind = (-genre_output).argsort()[:top_n]
            for i in top_n_ind:
                print("   -", self.int_to_genre[i])
                
            print(" Author: ")
            top_n_ind = (-author_output).argsort()[:top_n]
            for i in top_n_ind:
                print("   -", self.int_to_author[i])
                
            print(" Publisher: ")
            top_n_ind = (-publisher_output).argsort()[:top_n]
            for i in top_n_ind:
                print("   -", self.int_to_publisher[i])
                
        if use_lda:
            print("\n\nExplain output LDA")
            lda_output = output_vector[self.num_books+self.num_genre+self.num_author+self.num_publisher:]
            sims = self.index[lda_output]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])[:top_n]
            
            print(" books that are similar by LDA: ")
            for sim in sims :
                book_id = sim[0]
                try:
                    book_title = self.lda_index_to_title[book_id]
                    print("   -", book_title)
                except:
                    pass

            
    def explain_prediction_batch(self, output_vectors, input_vectors, top_n=5, use_meta=False):
        batch_size = np.shape(output_vectors)[0]
        for i in range(batch_size):
            self.explain_prediction(output_vectors[i], input_vectors[i], top_n=top_n, use_meta=use_meta)
            
    def hit_rate(self, test_output, rl_test_next_books, k):
        rating_vect = test_output[:,:self.num_books]
        top_k = (-rating_vect).argsort()[:,:k]
        hit = 0
        total = len(rating_vect)
        
        for i in range(len(rating_vect)):
            if rl_test_next_books[i][0] in top_k[i]:
                hit += 1
        
        return hit/total
    
    
            
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        