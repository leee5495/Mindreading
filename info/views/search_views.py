from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, FormView, View
from django.urls import reverse

from info.models import Aladin_User, Book, Aladin_User_Book, Author, Genre, Publisher, Book_Author, Book_Genre, Book_Publisher
from info.forms import SearchForm, SortOrderForm, DetailSearchForm, FilterForm

from django.db.models import Count
from django.db.models import Avg

import re
import datetime


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
        queryset = queryset.annotate(avg_reviews=Avg('aladin_user_book__rating'), num_reviews=Count('aladin_user_book')).order_by('-avg_reviews', '-num_reviews')
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
                
    if 'min_rating' in kwargs and kwargs.get('min_rating')!='None':
        min_rating = float(kwargs.get('min_rating'))
        queryset = queryset.annotate(avg_reviews=Avg('aladin_user_book__rating')).filter(avg_reviews__gte=min_rating)
            
    if 'min_num_rating' in kwargs and kwargs.get('min_num_rating')!='None':
        min_num_rating = int(kwargs.get('min_num_rating'))
        queryset = queryset.annotate(num_reviews=Count('aladin_user_book')).filter(num_reviews__gte=min_num_rating)
        
    if 'filter_keyword' in kwargs and kwargs.get('filter_keyword')!='None':
        keyword = kwargs.get('filter_keyword')           
        for i in re.split('[,|;][ ]*|[ ]+',keyword):
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
    min_rating = float(kwargs.get('min_rating')) if kwargs.get('min_rating')!='None' and kwargs.get('min_rating')!=None else None
    min_num_rating = int(kwargs.get('min_num_rating')) if kwargs.get('min_num_rating')!='None' and kwargs.get('min_num_rating')!=None else None
    filter_keyword = kwargs.get('filter_keyword') if kwargs.get('filter_keyword')!='None' and kwargs.get('filter_keyword')!=None else None
    
    return FilterForm(data={'min_price':min_price, 'max_price':max_price,
                            'from_date':from_date, 'to_date':to_date,
                            'min_rating':min_rating, 'min_num_rating':min_num_rating,
                            'filter_keyword': filter_keyword})

    

# search view (POST)
class SearchView(FormView):
    def post(self, request, *args, **kwargs):
        form = SearchForm(data=request.POST)
        if form.is_valid():
            search_type = form.cleaned_data['search_type']
            search_term = form.cleaned_data['search_term']
            return HttpResponseRedirect(reverse('info:search_result', args=(search_type,search_term)))

# search result view    
class SearchResultView(TemplateView):
    template_name = 'info/search_result.html'
    
    def get_context_data(self, **kwargs):
        search_type = self.kwargs.get('search_type')
        search_term = self.kwargs.get('search_term')
        
        context = super(SearchResultView, self).get_context_data(**kwargs)
        
        if search_type == '1' or search_type == '2':
            sort_by='1'
            books = Book.objects.filter(title__icontains=search_term)
            if 'sort_order' in self.kwargs:
                sort_by = self.kwargs.get('sort_order')
                books = sort_queryset(sort_by, books)
                
            books = filter_queryset(self.kwargs, books)
                    
            context['object_list'] = {'book': books}
            
            if search_type == '1':
                authors = Author.objects.filter(name__icontains=search_term)
                genres = Genre.objects.filter(name__icontains=search_term)
                publishers = Publisher.objects.filter(name__icontains=search_term)
                context['object_list']['author'] = authors
                context['object_list']['genre'] = genres
                context['object_list']['publisher'] = publishers
                
            context['sort_order'] = SortOrderForm(data={'sort_order': sort_by, 'view_by': '30'})
            context['filter'] = get_filter(self.kwargs)
        elif search_type == '3':
            authors = Author.objects.filter(name__icontains=search_term)
            context['object_list'] = {'author': authors}
        elif search_type == '4':
            genres = Genre.objects.filter(name__icontains=search_term)
            context['object_list'] = {'genre': genres}
        elif search_type == '5':
            publishers = Publisher.objects.filter(name__icontains=search_term)
            context['object_list'] = {'publisher': publishers}
            
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
        else: 
            context['user'] = False
        
        context['search_type'] = search_type
        context['search_term'] = search_term
        context['search_form'] = SearchForm(data={'search_type': search_type, 'search_term': search_term})
        
        return context  

    def post(self, request, *args, **kwargs):
        sort_order_form = SortOrderForm(request.POST or None)
        filter_form = FilterForm(request.POST or None)
        
        search_type = self.kwargs.get('search_type')
        search_term = self.kwargs.get('search_term')
        
        sort_by = self.kwargs.get('sort_order')
        if not sort_by:
            sort_by = '1'
        
        min_price = self.kwargs.get('min_price')
        max_price = self.kwargs.get('max_price')
        from_date = self.kwargs.get('from_date')
        to_date = self.kwargs.get('to_date')
        min_rating = self.kwargs.get('min_rating')
        min_num_rating = self.kwargs.get('min_num_rating')
        filter_keyword = self.kwargs.get('filter_keyword')
        
        if sort_order_form.is_valid():    
            sort_by = sort_order_form.cleaned_data['sort_order']            
            return HttpResponseRedirect(reverse('info:search_result_sorted', args=(search_type, search_term, sort_by, min_price, max_price, from_date, to_date, min_rating, min_num_rating, filter_keyword)))
            
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
                min_rating = filter_form.cleaned_data.get('min_rating')
                min_num_rating = filter_form.cleaned_data.get('min_num_rating')
                filter_keyword = filter_form.cleaned_data.get('filter_keyword')

                return HttpResponseRedirect(reverse('info:search_result_sorted', args=(search_type, search_term, sort_by, min_price, max_price, from_date, to_date, min_rating, min_num_rating, filter_keyword)))
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        elif 'reset' in request.POST:
            return HttpResponseRedirect(reverse('info:search_result_sorted', args=(search_type, search_term, sort_by, 'None', 'None', 'None', 'None', 'None', 'None', 'None')))
    
    
    
# detail search view (POST)
class DetailSearchView(TemplateView):
    template_name = 'info/detail_search.html'
    
    def get_context_data(self, **kwargs):
        context = super(DetailSearchView, self).get_context_data(**kwargs)
        context['detail_search_form'] = DetailSearchForm()
        context['search_form'] = SearchForm()
        
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
        else: 
            context['user'] = False
            
        return context
    
    def post(self, request, *args, **kwargs):
        form = DetailSearchForm(data=request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            author = form.cleaned_data['author']
            keyword = form.cleaned_data['keyword']
            publisher = form.cleaned_data['publisher']
            ISBN = form.cleaned_data['ISBN']
            return HttpResponseRedirect(reverse('info:detail_search_result', args=(title,author,keyword,publisher,ISBN)))
        else:
            context = self.get_context_data(**kwargs)
            context['detail_search_form'] = form
            return render(request, self.template_name, context)    
        
        
class DetailSearchResultView(ListView):
    template_name = 'info/detail_search_result.html'
    paginate_by = 30
    
    def get_queryset(self, **kwargs):
        title = self.kwargs.get('title')
        author = self.kwargs.get('author')
        publisher = self.kwargs.get('publisher')
        keyword = self.kwargs.get('keyword')
        ISBN = self.kwargs.get('ISBN')
        
        queryset = Book.objects.all()
        
        if title != '':
            for i in re.split('[,|;][ ]*|[ ]+',title):
                queryset = queryset.filter(title__icontains=i)
        if keyword != '':            
            for i in re.split('[,|;][ ]*|[ ]+',keyword):
                genres = Genre.objects.filter(name__icontains=i)
                book_genre = Book_Genre.objects.filter(book__in=queryset)
                
                queryset = (queryset.filter(title__icontains=i)|
                            queryset.filter(description__icontains=i)|
                            queryset.filter(publisher_description__icontains=i)|
                            queryset.filter(pk__in=book_genre.filter(genre__in=genres).values('book')))
        if ISBN != '':
            isbns = re.split('[,|;][ ]*|[ ]+',ISBN)
            queryset = queryset.filter(ISBN__in=isbns)
        if author != '':
            authors = []
            for i in re.split('[,|;][ ]*',author):
                authors.extend(list(Author.objects.filter(name__icontains=i)))
            book_author = Book_Author.objects.filter(book__in=queryset)
            queryset = queryset.filter(pk__in=book_author.filter(author__in=authors).values('book'))
        if publisher != '':
            publishers = []
            for i in re.split('[,|;][ ]*',publisher):
                publishers.extend(list(Publisher.objects.filter(name__icontains=i)))
            book_publisher = Book_Publisher.objects.filter(book__in=queryset)
            queryset = queryset.filter(pk__in=book_publisher.filter(publisher__in=publishers).values('book'))
            
        if 'sort_order' in self.kwargs:
            sort_by = self.kwargs.get('sort_order')
            queryset = sort_queryset(sort_by, queryset)
        
        if 'view_by' in self.kwargs:
            view_by = self.kwargs.get('view_by')
            self.paginate_by = int(view_by)
            
        queryset = filter_queryset(self.kwargs, queryset)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DetailSearchResultView, self).get_context_data(**kwargs)
        
        context['sort_order'] = get_sort_order(self.kwargs)
        context['filter'] = get_filter(self.kwargs)
        context['search_form'] = SearchForm()
        context['is_listview'] = True
        
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
        else: 
            context['user'] = False
        
        return context
    
    def post(self, request, *args, **kwargs):        
        sort_order_form = SortOrderForm(request.POST or None)
        filter_form = FilterForm(request.POST or None)

        title = self.kwargs.get('title')
        author = self.kwargs.get('author')
        publisher = self.kwargs.get('publisher')
        keyword = self.kwargs.get('keyword')
        ISBN = self.kwargs.get('ISBN')
        
        sort_by = self.kwargs.get('sort_order')
        if not sort_by:
            sort_by = '1'
        view_by = self.kwargs.get('view_by')
        if not view_by:
            view_by = '30'
        
        min_price = self.kwargs.get('min_price')
        max_price = self.kwargs.get('max_price')
        from_date = self.kwargs.get('from_date')
        to_date = self.kwargs.get('to_date')
        min_rating = self.kwargs.get('min_rating')
        min_num_rating = self.kwargs.get('min_num_rating')
        filter_keyword = self.kwargs.get('filter_keyword')
        
        if sort_order_form.is_valid():    
            sort_by = sort_order_form.cleaned_data['sort_order']  
            view_by = sort_order_form.cleaned_data['view_by']
            return HttpResponseRedirect(reverse('info:detail_search_result_sorted', args=(title, author, keyword, publisher, ISBN, sort_by, view_by, min_price, max_price, from_date, to_date, min_rating, min_num_rating, filter_keyword)))
            
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
                min_rating = filter_form.cleaned_data.get('min_rating')
                min_num_rating = filter_form.cleaned_data.get('min_num_rating')
                filter_keyword = filter_form.cleaned_data.get('filter_keyword')

                return HttpResponseRedirect(reverse('info:detail_search_result_sorted', args=(title, author, keyword, publisher, ISBN, sort_by, view_by, min_price, max_price, from_date, to_date, min_rating, min_num_rating, filter_keyword)))
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
        elif 'reset' in request.POST:
            return HttpResponseRedirect(reverse('info:detail_search_result_sorted', args=(title, author, keyword, publisher, ISBN, sort_by, view_by, 'None', 'None', 'None', 'None', 'None', 'None', 'None')))
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        