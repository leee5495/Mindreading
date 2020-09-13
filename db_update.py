# -*- coding: utf-8 -*-
import os
import pickle
import datetime

import numpy as np
import pandas as pd
from konlpy.tag import Okt
from gensim.models import TfidfModel
from gensim.models.ldamodel import LdaModel
from gensim.similarities import MatrixSimilarity

from info.models import Aladin_User, Book, Aladin_User_Book, Author, Genre, Publisher, Book_Author, Book_Genre, Book_Publisher

datapath = "./data"
modelpath = "./models"

book = pd.read_csv(os.path.join(datapath, "Book.csv"))
aladin_user = pd.read_csv(os.path.join(datapath, "Aladin_User.csv"))
aladin_user_book = pd.read_csv(os.path.join(datapath, "Aladin_User_Book.csv"))
author = pd.read_csv(os.path.join(datapath, "Author.csv"))
book_author = pd.read_csv(os.path.join(datapath, "Book_Author.csv"))
genre = pd.read_csv(os.path.join(datapath, "Genre.csv"))
book_genre = pd.read_csv(os.path.join(datapath, "Book_Genre.csv"))
publisher = pd.read_csv(os.path.join(datapath, "Publisher.csv"))
book_publisher = pd.read_csv(os.path.join(datapath, "Book_Publisher.csv"))

# update Book
for line in book.values:
    temp = Book(id=line[1]+1,
                aladin_id=line[2],
                ISBN=line[3],
                title=line[4],
                page=line[5],
                price=line[6],
                sale_price=line[7],
                pub_date=datetime.datetime.strptime(line[8], "%Y-%m-%d %H:%M:%S"),
                image_src=line[9],
                description=line[10],
                publisher_description=line[11])
    try:
        temp.save()
    except:
        print("there was a problem with book_id {} in book".format(line[1]))

# update Aladin_User
for line in aladin_user.values:
    temp = Aladin_User(id=line[1]+1,
                       aladin_id=line[2],
                       name=line[3])
    try:
        temp.save()
    except:
        print("there was a problem with user_id {} in user".format(line[1]))        

# update Aladin_User_Book
for line in aladin_user_book.values:
    temp_time = None
    if type(line[5]) is str:
        temp_time = datetime.datetime.strptime(line[5], "%Y-%m-%d")
    temp = Aladin_User_Book(user=Aladin_User.objects.get(pk=line[1]+1),
                            book=Book.objects.get(pk=line[2]+1),
                            rating = line[3],
                            comment = line[4],
                            time = temp_time)
    try:
        temp.save()
    except:
        print("there was a problem with user_id {}, book_id {} in user_book".format(line[1], line[2]))  
        
# update Author
for line in author.values:
    temp = Author(id=line[1]+1,
                  name=line[2])
    try:
         temp.save()
    except:
         print("there was a problem with author_id {} in author".format(line[1]))

# update Book_Author
for line in book_author.values:
    temp = Book_Author(book=Book.objects.get(pk=line[1]+1),
                       author=Author.objects.get(pk=line[2]+1))
    try:
         temp.save()
    except:
         print("there was a problem with book_id {} author_id {} in book_author".format(line[1], line[2]))
         
# update Genre
for line in genre.values:
    if np.isnan(line[2]):
        temp_parent = None
    else:
        temp_parent = Genre.objects.get(pk=line[2]+1)
    temp = Genre(id=line[1]+1,
                 parent=temp_parent,
                 name=line[3])
    try:
         temp.save()
    except:
         print("there was a problem with genre_id {} in genre".format(line[1]))
    
# update Book_Genre
for line in book_genre.values:
    temp = Book_Genre(book=Book.objects.get(pk=line[1]+1),
                      genre=Genre.objects.get(pk=line[2]+1))
    try:
         temp.save()
    except:
         print("there was a problem with book_id {} genre_id {} in book_genre".format(line[1], line[2]))
         
# update Publisher
for line in publisher.values:
    temp = Publisher(id=line[1]+1,
                     name=line[2])
    try:
         temp.save()
    except:
         print("there was a problem publisher_id {} in publisher".format(line[1]))
         
# update Book_Publisher
for line in book_publisher.values:
    temp = Book_Publisher(book=Book.objects.get(pk=line[1]+1),
                          publisher=Publisher.objects.get(pk=line[2]+1))
    try:
         temp.save()
    except:
         print("there was a problem with book_id {} publisher_id {} in book_publisher".format(line[1], line[2]))        
    

# ADD RECOMMENDATION IDs
with open(os.path.join(datapath, "book_id"), "r", encoding='utf-8') as fin:
	book_id = [line.strip() for line in fin]
for idx, bid in enumerate(book_id):
    try:
        book = Book.objects.filter(aladin_id=str(bid))[0]
        setattr(book, 'rec_id', idx)
        book.save()
    except:
        print(i)
        print(j)
    
with open(os.path.join(datapath, "author_id"), "r", encoding='utf-8') as fin:
	author_id = [line.strip() for line in fin] 
for idx, aid in enumerate(author_id):
    try:
        author = list(Author.objects.filter(name=aid))
        for k in author:
            setattr(k, 'rec_id', idx)
            k.save()
    except:
        print(i)
        print(j)    
    
with open(os.path.join(datapath, "genre_id"), "r", encoding='utf-8') as fin:
	genre_id = [line.strip() for line in fin]   
for idx, gid in enumerate(genre_id):
    try:
        genre = list(Genre.objects.filter(name=gid))
        for k in genre:
            setattr(k, 'rec_id', idx)
            k.save()
    except:
        print(i)
        print(j)   
        
with open(os.path.join(datapath, "publisher_id"), "r", encoding='utf-8') as fin:
	publisher_id = [line.strip() for line in fin]
for idx, pid in enumerate(publisher_id):
    try:
        publisher = list(Publisher.objects.filter(name=pid))
        for k in publisher:
            setattr(k, 'rec_id', idx)
            k.save()
    except:
        print(i)
        print(j) 

   
# PRE_SAVE LDA SIMILAR BOOKS
okt = Okt()
lda_similarity = MatrixSimilarity.load(os.path.join(modelpath, "lda_similarity.index"))
lda_model = LdaModel.load(os.path.join(modelpath, "lda_model"))
tfidf_model = TfidfModel.load(os.path.join(modelpath, "tfidf_model"))

for book in list(Book.objects.all()):
    print(book.id)
    doc = okt.pos(book.description + book.publisher_description, norm=True, stem=True)
    used_tags = ['Adjective', 'Adverb', 'Alpha', 'Foreign', 'Hashtag', 'Noun', 'Number']
    doc = [j[0] for j in doc if j[1] in used_tags]
    doc = lda_model.id2word.doc2bow(doc)
    doc = tfidf_model[doc]
    doc = lda_model.get_document_topics(doc, minimum_probability=0)
    similar_books = np.argsort(-lda_similarity[doc])[:5]
    sims = ""
    for i in similar_books:
        sims = sims + str(i) + " "
    print(sims)
    setattr(book, 'lda_sims', sims)
    book.save()