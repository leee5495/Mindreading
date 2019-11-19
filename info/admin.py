from django.contrib import admin
from info.models import Aladin_User, Book, Aladin_User_Book, Author, Genre, Publisher, Book_Author, Book_Genre, Book_Publisher

# Register your models here.
admin.site.register(Aladin_User)
admin.site.register(Book)
admin.site.register(Aladin_User_Book)
admin.site.register(Author)
admin.site.register(Genre)
admin.site.register(Publisher)
admin.site.register(Book_Author)
admin.site.register(Book_Genre)
admin.site.register(Book_Publisher)
