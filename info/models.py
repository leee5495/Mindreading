from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
    
class Aladin_User(models.Model):
    aladin_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

class Book(models.Model):
    aladin_id = models.CharField(max_length=100)
    rec_id = models.IntegerField(null=True)
    ISBN = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    image_src = models.CharField(max_length=500, null=True)
    price = models.IntegerField()
    sale_price = models.IntegerField()
    pub_date = models.DateTimeField()
    page = models.IntegerField()
    description = models.TextField(null=True)
    publisher_description = models.TextField(null=True)
    lda_sims = models.CharField(max_length=100, null=True)

class Aladin_User_Book(models.Model):
    user = models.ForeignKey(Aladin_User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True)
    time = models.DateTimeField(null=True)
    
class User_Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(null=True)
    time = models.DateTimeField(null=True)
    
class User_Book_Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    time = models.DateTimeField(null=True)
    
class Author(models.Model):
    rec_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    
class Genre(models.Model):
    rec_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    
class Publisher(models.Model):
    rec_id = models.IntegerField(null=True)
    name = models.CharField(max_length=100)
    
class Book_Author(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, null=True, on_delete=models.SET_NULL)
    
class Book_Genre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    
class Book_Publisher(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publisher, null=True, on_delete=models.SET_NULL)  