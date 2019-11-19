#cloud_sql_proxy_x64.exe -instances="mindreading:asia-northeast2:mindreadingdb-2019"=tcp:3307

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.urls import reverse

from info.models import Aladin_User, Book, Aladin_User_Book, Author, Genre, Publisher, Book_Author, Book_Genre, Book_Publisher, User_Book, User_Book_Like
from django.contrib.auth import get_user_model
from info.forms import SearchForm, ReviewForm, SortOrderForm, FilterForm

from django.db.models import Q, Count
from django.db.models import Avg
from django.db.models import Case, When

import datetime
import re
import os
import pickle
import numpy as np

User = get_user_model()

modelpath = "info/views/models"

len_rating = 5992
num_author = 2850
num_genre = 164
num_publisher = 751

def get_user(request):
    if request.COOKIES.get('username') is not None:
        ID = request.COOKIES.get('username')
        pw = request.COOKIES.get('password')
    else:
        ID = None
        pw = None
    return ID, pw

def sort_queryset(sort_by, queryset):
    if sort_by == '1':
        queryset = queryset.order_by('pk')
    elif sort_by == '2':
        queryset = queryset.order_by('title')
    elif sort_by == '3':
        queryset = queryset.annotate(num_reviews=Count('aladin_user_book'), avg_reviews=Avg('aladin_user_book__rating')).order_by('-num_reviews', '-avg_reviews')
    elif sort_by == '4':
        queryset = queryset.annotate(num_reviews=Count('aladin_user_book'), avg_reviews=Avg('aladin_user_book__rating')).order_by('-avg_reviews', '-num_reviews')
    elif sort_by == '5':
        queryset = queryset.order_by('-pub_date')
    elif sort_by == '6':
        queryset = queryset.order_by('sale_price')
    elif sort_by == '7':
        queryset = queryset.order_by('-sale_price')
    return queryset

def filter_queryset(kwargs, queryset):
    if 'min_price' in kwargs and kwargs.get('min_price')!='None':
        min_price = int(kwargs.get('min_price'))
        queryset = queryset.filter(sale_price__gte=min_price)
                
    if 'max_price' in kwargs and kwargs.get('max_price')!='None':
        max_price = int(kwargs.get('max_price'))
        queryset = queryset.filter(sale_price__lte=max_price)
            
    if 'from_date' in kwargs and kwargs.get('from_date')!='None':
        from_date = datetime.datetime.strptime(kwargs.get('from_date'), '%Y/%m/%d')
        queryset = queryset.filter(pub_date__gte=from_date)
                
    if 'to_date' in kwargs and kwargs.get('to_date')!='None':
        to_date = datetime.datetime.strptime(kwargs.get('to_date'), '%Y/%m/%d')
        queryset = queryset.filter(pub_date__lte=to_date)
    
    """
    if 'min_rating' in kwargs and kwargs.get('min_rating')!='None':
        min_rating = float(kwargs.get('min_rating'))
        queryset = queryset.filter(avg_reviews__gte=min_rating)
        
    if 'min_num_rating' in kwargs and kwargs.get('min_num_rating')!='None': 
        min_num_rating = int(kwargs.get('min_num_rating'))
        queryset = queryset.filter(num_reviews__gte=min_num_rating)
    """
    
    if 'filter_keyword' in kwargs and kwargs.get('filter_keyword')!='None':
        filter_keyword = kwargs.get('filter_keyword')
        for i in re.split('[,|;][ ]*|[ ]+',filter_keyword):
            genres = Genre.objects.filter(name__icontains=i)
            book_genre = Book_Genre.objects.filter(book__in=queryset)
                
            queryset = (queryset.filter(title__icontains=i)|
                        queryset.filter(description__icontains=i)|
                        queryset.filter(publisher_description__icontains=i)|
                        queryset.filter(pk__in=book_genre.filter(genre__in=genres).values('book')))
    return queryset
    
def get_sort_order(kwargs):
    if 'sort_order' in kwargs:
        return SortOrderForm(data={'sort_order': kwargs.get('sort_order'), 'view_by': kwargs.get('view_by')})
    else:
        return SortOrderForm(data={'sort_order': '1', 'view_by': '30'})

def get_filter(kwargs):
    min_price = int(kwargs.get('min_price')) if kwargs.get('min_price')!='None' and kwargs.get('min_price')!=None  else None
    max_price = int(kwargs.get('max_price')) if kwargs.get('max_price')!='None' and kwargs.get('max_price')!=None else None
    from_date = kwargs.get('from_date') if kwargs.get('from_date')!='None' and kwargs.get('from_date')!=None else None
    to_date = kwargs.get('to_date') if kwargs.get('to_date')!='None' and kwargs.get('to_date')!=None else None
    #min_rating = float(kwargs.get('min_rating')) if kwargs.get('min_rating')!='None' and kwargs.get('min_rating')!=None else None
    #min_num_rating = int(kwargs.get('min_num_rating')) if kwargs.get('min_num_rating')!='None' and kwargs.get('min_num_rating')!=None else None
    filter_keyword = kwargs.get('filter_keyword') if kwargs.get('filter_keyword')!='None' and kwargs.get('filter_keyword')!=None else None
    
    return FilterForm(data={'min_price':min_price, 'max_price':max_price,
                            'from_date':from_date, 'to_date':to_date,
                            #'min_rating':min_rating, 'min_num_rating':min_num_rating,
                            'filter_keyword': filter_keyword})
    
    
# book list
class BookListView(ListView):
    model = Book
    template_name = 'info/book_list.html'
    paginate_by = 30
    
    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        
        context['genre_menu'] = {'장르': Genre.objects.filter(parent__isnull=True).annotate(num_books=Count('book_genre')).order_by('-num_books')}
        if 'genre_id' in self.kwargs:
            genre_id = self.kwargs.get('genre_id')
            cur_genre = Genre.objects.get(pk=genre_id)
            path = [cur_genre]
            while True:
                if cur_genre.parent is None:
                    break
                parent = cur_genre.parent
                path.insert(0,parent)
                cur_genre = parent
            for i in range(len(path)):
                context['genre_menu'][path[i].name] = Genre.objects.filter(parent=path[i]).annotate(num_books=Count('book_genre')).order_by('-num_books')
                
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
        else: 
            context['user'] = False
            
        context['sort_order'] = get_sort_order(self.kwargs)
        context['filter'] = get_filter(self.kwargs)
        context['search_form'] = SearchForm()
        context['is_listview'] = True
        
        return context
    
    def get_queryset(self, **kwargs):
        queryset = Book.objects.all()
        
        if 'genre_id' in self.kwargs:
            genre_id = self.kwargs.get('genre_id')
            genre = Genre.objects.get(pk=genre_id)
            book_genre = Book_Genre.objects.filter(book__in=queryset)
            queryset = queryset.filter(pk__in=book_genre.filter(genre=genre).values('book'))
        
        if 'sort_order' in self.kwargs:
            sort_by = self.kwargs.get('sort_order')
            queryset = sort_queryset(sort_by, queryset)
        
        if 'view_by' in self.kwargs:
            view_by = self.kwargs.get('view_by')
            self.paginate_by = int(view_by)
            
        queryset = filter_queryset(self.kwargs, queryset)
            
        return queryset
    
    def post(self, request, *args, **kwargs):
        sort_order_form = SortOrderForm(request.POST or None)
        filter_form = FilterForm(request.POST or None)
        
        genre_id = self.kwargs.get('genre_id')
        
        sort_by = self.kwargs.get('sort_order')
        view_by = self.kwargs.get('view_by')
        if not sort_by:
            sort_by = '1'
        if not view_by:
            view_by = '30'
        
        min_price = self.kwargs.get('min_price')
        max_price = self.kwargs.get('max_price')
        from_date = self.kwargs.get('from_date')
        to_date = self.kwargs.get('to_date')
        #min_rating = self.kwargs.get('min_rating')
        #min_num_rating = self.kwargs.get('min_num_rating')
        filter_keyword = self.kwargs.get('filter_keyword')
        
        if sort_order_form.is_valid():    
            sort_by = sort_order_form.cleaned_data['sort_order']
            view_by = sort_order_form.cleaned_data['view_by']
            
            if genre_id:
                return HttpResponseRedirect(reverse('info:book_list_genre', args=(genre_id, sort_by, view_by, min_price, max_price, from_date, to_date, filter_keyword))) #min_rating, min_num_rating, 
            else:
                return HttpResponseRedirect(reverse('info:book_list_sorted', args=(sort_by, view_by, min_price, max_price, from_date, to_date, filter_keyword))) #min_rating, min_num_rating, 
            
        elif 'filter' in request.POST:
            if filter_form.is_valid():
                min_price = filter_form.cleaned_data['min_price']
                max_price = filter_form.cleaned_data['max_price']
                if filter_form.cleaned_data.get('from_date'):
                    from_date = filter_form.cleaned_data.get('from_date').strftime("%Y/%m/%d")
                else:
                    from_date = None
                if filter_form.cleaned_data.get('to_date'):
                    to_date = filter_form.cleaned_data.get('to_date').strftime("%Y/%m/%d")
                else:
                    to_date = None
                #min_rating = filter_form.cleaned_data.get('min_rating')
                #min_num_rating = filter_form.cleaned_data.get('min_num_rating')
                filter_keyword = filter_form.cleaned_data.get('filter_keyword')

                if genre_id:
                    return HttpResponseRedirect(reverse('info:book_list_genre', args=(genre_id, sort_by, view_by, min_price, max_price, from_date, to_date, filter_keyword))) #min_rating, min_num_rating, 
                else:
                    return HttpResponseRedirect(reverse('info:book_list_sorted', args=(sort_by, view_by, min_price, max_price, from_date, to_date, filter_keyword))) #min_rating, min_num_rating, 
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        elif 'reset' in request.POST:
            if genre_id:
                return HttpResponseRedirect(reverse('info:book_list_genre', args=(genre_id, sort_by, view_by, 'None', 'None', 'None', 'None', 'None'))) #'None', 'None', 
            else:
                return HttpResponseRedirect(reverse('info:book_list_sorted', args=(sort_by, view_by, 'None', 'None', 'None', 'None', 'None'))) #'None', 'None', 
                
    
# book detail
class BookDetailView(TemplateView):
    template_name = 'info/book_detail.html'
    
    def get_context_data(self, **kwargs):        
        book_id = self.kwargs.get('pk')
        book = Book.objects.get(pk=book_id)
        
        book_author = Book_Author.objects.filter(book=book)
        author = [book_author[i].author for i in range(len(book_author))]
        
        book_genre = Book_Genre.objects.filter(book=book).values('genre')
        genre = Genre.objects.filter(pk__in=book_genre)
        
        leaf_genres = []
        for i in list(genre):
            leaf = True
            for j in list(genre):
                if j.parent == i:
                    leaf=False
            if leaf:
                leaf_genres.append(i)
        
        genre_list = []
        for i in leaf_genres:
            node = i
            temp = []
            while True:
                temp.insert(0, node)
                node = node.parent
                if node is None:
                    break
            genre_list.append(temp)
        
        
        book_publisher = Book_Publisher.objects.filter(book=book)[0]
        publisher = book_publisher.publisher
        
        aladin_user_book = Aladin_User_Book.objects.filter(book=book).order_by('-time')
        user_book = User_Book.objects.filter(book=book).order_by('-time')
        review_form = ReviewForm()
        
        similar_books = book.lda_sims
        similar_books = similar_books.split(" ")[:-1]
        similar_books = [Book.objects.get(pk=int(i)+1) for i in similar_books]
        
        context = super(BookDetailView, self).get_context_data(**kwargs)
        
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
            user = self.request.user
            
            if User_Book.objects.filter(user=user).filter(book=book):
                context['reviewed'] = True
                review_form.fields["review"].initial = "You have already left a review"
            if User_Book_Like.objects.filter(user=user).filter(book=book):
                context['user_liked'] = True
        else: 
            context['user'] = False

        context['object'] = book
        context['object_author'] = author
        context['object_genre'] = genre_list
        context['object_publisher'] = publisher
        context['object_review_aladin'] = aladin_user_book
        context['object_review'] = user_book
        context['review_form'] = review_form
        context['search_form'] = SearchForm()
        context['similar_books'] = similar_books
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = ReviewForm(data=request.POST)
        ID, PW = get_user(self.request)
        book_id = self.kwargs.get('pk')
        
        if request.POST.get("delete"):
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            
            temp_ = User_Book.objects.filter(user=user).filter(book=book)
            temp_.delete()
            
            return HttpResponseRedirect(request.path_info)
        elif request.POST.get("name")=="like":
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            temp_ = User_Book_Like(user=user, book=book, time=datetime.datetime.now())
            temp_.save()
            return JsonResponse({'m': "success"})
        elif request.POST.get("name")=="unlike":
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            temp_ = User_Book_Like.objects.filter(user=user).filter(book=book)
            temp_.delete()
            return JsonResponse({'m': "success"})
        else:
            if form.is_valid():
                rating = int(form.cleaned_data['rating'])
                comment = form.cleaned_data['review']                
                user = self.request.user
                book = Book.objects.get(pk=self.kwargs.get('pk'))
                time = datetime.datetime.now()
                
                temp_review = User_Book(user=user, book=book, rating=rating, comment=comment, time=time)
                temp_review.save()
                
                return HttpResponseRedirect(request.path_info)
            else:
                context = self.get_context_data()
                context['message'] = "Please give more than one star"
                return render(request, 'info/book_detail.html', context)
  
    
    
# for author, genre, publisher detail view
class GridDetailView(ListView):
    template_name = 'info/grid_detail_list.html'
    context_object_name = 'object_book'
    paginate_by = 30
    
    def get_queryset(self, **kwargs):
        detail_type = self.kwargs.get('detail_type')
        search_id = self.kwargs.get('pk')
        
        queryset = []
        
        if detail_type == "author":
            objects = Author.objects.get(pk=search_id)
            author_book = Book_Author.objects.filter(author=objects).values('book')
            queryset = Book.objects.filter(pk__in=author_book)
        elif detail_type == "publisher":
            objects = Publisher.objects.get(pk=search_id)
            publisher_book = Book_Publisher.objects.filter(publisher=objects).values('book')
            queryset = Book.objects.filter(pk__in=publisher_book)
        elif detail_type == "aladin_user":
            objects = Aladin_User.objects.get(pk=search_id)
            queryset = Aladin_User_Book.objects.filter(user=objects)
        else:
            objects = User.objects.get(pk=search_id)
            queryset = User_Book.objects.filter(user=objects)
        
        if 'sort_order' in self.kwargs:
            sort_by = self.kwargs.get('sort_order')
            queryset = sort_queryset(sort_by, queryset)
        
        if 'view_by' in self.kwargs:
            view_by = self.kwargs.get('view_by')
            self.paginate_by = int(view_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super(GridDetailView, self).get_context_data(**kwargs)
        
        detail_type = self.kwargs.get('detail_type')
        search_id = self.kwargs.get('pk')
        
        objects, subname, is_user = '','', False
        
        if detail_type == "author":
            objects = Author.objects.get(pk=search_id)
            subname = "이 작가의 책"
        elif detail_type == "publisher":
            objects = Publisher.objects.get(pk=search_id)
            subname = "이 출판사의 책"
        elif detail_type == "aladin_user" :
            objects = Aladin_User.objects.get(pk=search_id)
            is_user = True
        else:
            objects = {'name': User.objects.get(pk=search_id).username}
            is_user = True
        
        if is_user:
            context['sort_order'] = None
        elif 'sort_order' in self.kwargs:
            context['sort_order'] = SortOrderForm(data={'sort_order': self.kwargs.get('sort_order'), 'view_by': self.kwargs.get('view_by')})
        else:
            context['sort_order'] = SortOrderForm(data={'sort_order': '1', 'view_by': '30'})
        
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
        else: 
            context['user'] = False
            
        context['object'] = objects
        context['search_form'] = SearchForm()
        context['subname'] = subname
        context['is_user'] = is_user
        context['is_listview'] = True
        return context
    
    def post(self, request, *args, **kwargs):
        sort_order_form = SortOrderForm(data=request.POST)
        
        detail_type = self.kwargs.get('detail_type')
        search_id = self.kwargs.get('pk')
        
        if sort_order_form.is_valid():
            sort_order = sort_order_form.cleaned_data['sort_order']
            view_by = sort_order_form.cleaned_data['view_by']
            
            return HttpResponseRedirect(reverse('info:grid_detail_sorted', args=(detail_type, search_id, sort_order, view_by)))  


#### RECOMMENDATION VIEW
class RecommendationView(TemplateView):
    template_name = 'info/recommendation.html'
    
    def get_context_data(self, **kwargs): 
        context = super(RecommendationView, self).get_context_data(**kwargs)
        
        ID, PW = get_user(self.request)
        page_id = self.kwargs.get('page_id')
        rec_types = ["per_rec", "cur_best", "best"]
        
        if ID is not None:
            rec_type = rec_types[int(page_id)-1]
            rec_pages = {1: "Personal Recommendation",
                         2: "Recent Bestseller",
                         3: "Bestseller"}
        
        else: 
            rec_type = rec_types[int(page_id)]
            rec_pages = {1: "Recent Bestseller",
                         2: "Bestseller"}
            context['user'] = False
          
        context['search_form'] = SearchForm() 
        context['rec_type'] = rec_type
        context['rec_pages'] = rec_pages
        
        if rec_type == "per_rec":
            user = self.request.user
            context['user'] = ID
            rec_list, scores = self.get_recommendation_set()
            temp_ = []
            for i, j in zip(list(rec_list), scores*1000):
                k = User_Book_Like.objects.filter(user=user).filter(book=i)
                temp_.append({'rec': i, 'score': j, 'user_liked': k})
            context['rec_list'] = temp_
            
        elif rec_type == "cur_best":
            temp_trending = {}
            genre = Genre.objects.get(pk=91)
            temp_trending['추리/미스테리 소설'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book', filter=Q(aladin_user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))
                                                    +Count('user_book', filter=Q(user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))).order_by('-num_reviews')[:50],
                                                  'id': 91}
            genre = Genre.objects.get(pk=99)
            temp_trending['판타지/환상문학'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book', filter=Q(aladin_user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))
                                                    +Count('user_book', filter=Q(user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))).order_by('-num_reviews')[:50],
                                               'id': 99}
            genre = Genre.objects.get(pk=41)
            temp_trending['로맨스 소설'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book', filter=Q(aladin_user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))
                                                    +Count('user_book', filter=Q(user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))).order_by('-num_reviews')[:50],
                                            'id': 41}
            genre = Genre.objects.get(pk=95)
            temp_trending['테마문학'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book', filter=Q(aladin_user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))
                                                    +Count('user_book', filter=Q(user_book__time__gt=datetime.datetime.today()-datetime.timedelta(days=365)))).order_by('-num_reviews')[:50],
                                        'id': 95}
            context['rec_list'] = temp_trending
        
        elif rec_type == "best":
            temp_bestseller = {}
            genre = Genre.objects.get(pk=91)
            temp_bestseller['추리/미스테리 소설'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book')+Count('user_book')).order_by('-num_reviews')[:50],
                                                    'id': 91}
            genre = Genre.objects.get(pk=99)
            temp_bestseller['판타지/환상문학'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book')+Count('user_book')).order_by('-num_reviews')[:50],
                                                  'id': 99}
            genre = Genre.objects.get(pk=41)
            temp_bestseller['로맨스 소설'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book')+Count('user_book')).order_by('-num_reviews')[:50],
                                              'id': 41}
            genre = Genre.objects.get(pk=95)
            temp_bestseller['테마문학'] = {'objects': Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                    num_reviews=Count('aladin_user_book')+Count('user_book')).order_by('-num_reviews')[:50],
                                            'id': 95}
            context['rec_list'] = temp_bestseller
           
        return context
    
    
    def sample_hidden(self, input_data, weights):
        input_data = np.reshape(input_data, (1,-1))
        hidden = np.matmul(input_data, weights['W']) + weights['b_h']
        hidden = 1/(1 + np.exp(-hidden)) 
        return hidden
    
    def prediction(self, input_data, weights):
        hidden = np.matmul(input_data, weights[0]) + weights[1]
        hidden = np.maximum(hidden, 0)
        hidden = np.matmul(hidden, weights[2]) + weights[3]
        pred = 1/(1 + np.exp(-hidden)) 
        return pred

    def get_recommendation_set(self):
        with open(os.path.join(modelpath, "ensemble_cluster_rbm_keras"), "rb") as fp:
            ensemble_cluster_rbm_model = pickle.load(fp)
        
        with open(os.path.join(modelpath, "ensemble_rbm1_keras"), "rb") as fp:
            ensemble_rbm1_model = pickle.load(fp)
        
        with open(os.path.join(modelpath, "ensemble_rbm2_keras"), "rb") as fp:
            ensemble_rbm2_model = pickle.load(fp)
        
        with open(os.path.join(modelpath, "ensemble_rbm3_keras"), "rb") as fp:
            ensemble_rbm3_model = pickle.load(fp)
        
        with open(os.path.join(modelpath, "ensemble_model_weights"), "rb") as fp:
            ensemble_model_weights = pickle.load(fp)
            
        with open(os.path.join(modelpath, "ensemble_kmeans"), "rb") as fp:
            ensemble_kmeans = pickle.load(fp)
          
        # get user_book interactions
        user = self.request.user
        user_book = list(User_Book.objects.filter(user=user))
        
        temp_rating = np.zeros((len_rating,))
        temp_author = np.zeros((num_author,))
        temp_genre = np.zeros((num_genre,))
        temp_publisher = np.zeros((num_publisher))
        
        for i in user_book:
            # update temp rating vect
            book = i.book
            if book.rec_id:
                book_rec_id = book.rec_id
                rating = i.rating/5  
                temp_rating[book_rec_id] = rating
            else:
                rating = i.rating/5
               
            # update meta vect
            authors = [j.author for j in list(Book_Author.objects.filter(book=book))]
            for j in authors:
                if j.rec_id:
                    temp_author[j.rec_id] = max(temp_author[j.rec_id], rating)
            genres = [j.genre for j in list(Book_Genre.objects.filter(book=book))]
            for j in genres:
                if j.rec_id:
                    temp_genre[j.rec_id] = max(temp_genre[j.rec_id], rating)
            publishers = [j.publisher for j in list(Book_Publisher.objects.filter(book=book))]
            for j in publishers:
                if j.rec_id:
                    temp_publisher[j.rec_id] = max(temp_publisher[j.rec_id], rating)
                    
        user_rbm_input = [np.concatenate([temp_rating, temp_author, temp_genre, temp_publisher], axis=0)]
        
        ensemble_rbm1_hidden = self.sample_hidden(user_rbm_input, ensemble_rbm1_model)
        ensemble_rbm2_hidden = self.sample_hidden(user_rbm_input, ensemble_rbm2_model)
        ensemble_rbm3_hidden = self.sample_hidden(user_rbm_input, ensemble_rbm3_model)
        ensemble_cluster_rbm_hidden = self.sample_hidden(user_rbm_input, ensemble_cluster_rbm_model)
        
        ensemble_test_input = np.concatenate([ensemble_rbm1_hidden, ensemble_rbm2_hidden, ensemble_rbm3_hidden, ensemble_kmeans.transform(ensemble_cluster_rbm_hidden)], axis=1)
        
        ensemble_prediction = self.prediction(ensemble_test_input, ensemble_model_weights)[0,:len_rating]
        ensemble_prediction = ensemble_prediction*np.where(temp_rating!=0,0,1)   
           
        ranks = np.argsort(-ensemble_prediction)[:200]
        preserved = Case(*[When(rec_id=rec_id, then=pos) for pos, rec_id in enumerate(ranks)])
        queryset = Book.objects.filter(rec_id__in=ranks).order_by(preserved)
        
        return queryset, ensemble_prediction[ranks]
        
    def post(self, request, *args, **kwargs):
        if request.POST.get("name")=="like":
            book_id = request.POST.get("val")
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            temp_ = User_Book_Like(user=user, book=book, time=datetime.datetime.now())
            temp_.save()
            return JsonResponse({'m': "success"})
        
        elif request.POST.get("name")=="unlike":
            book_id = request.POST.get("val")
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            temp_ = User_Book_Like.objects.filter(user=user).filter(book=book)
            temp_.delete()
            return JsonResponse({'m': "success"})
        