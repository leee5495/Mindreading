import datetime

from django.shortcuts import render
from django.db import IntegrityError
from django.db.models import Count, Avg, Q, F
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.views.generic import View, FormView, ListView, TemplateView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from info.forms import LoginForm, SignupForm, SearchForm
from info.models import User_Book, User_Book_Like, Book, Book_Genre, Genre, Book_Author


User = get_user_model()

def get_user(request):
    if request.COOKIES.get('username') is not None:
        ID = request.COOKIES.get('username')
        pw = request.COOKIES.get('password')
    else:
        ID = None
        pw = None
    return ID, pw


# default page with login
class IndexView(TemplateView):
    template_name = 'info/user/index.html'
    
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['login_form'] = LoginForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST)     
        context=self.get_context_data()
        context['error_message'] = 'username or password is incorrect'
        if self.request.COOKIES.get('username') is not None:
            ID = self.request.COOKIES.get('username')
            pw = self.request.COOKIES.get('password')
            user = auth.authenticate(self.request, username=ID, password=pw)
            if user is not None:
                auth.login(self.request, user)
                return HttpResponseRedirect("/book/")
            else:
                return render(self.request, self.template_name, context=context)
        else:
            if form.is_valid():          
                ID = form.cleaned_data['user_id']
                pw = form.cleaned_data['password']
                user = auth.authenticate(self.request, username=ID, password=pw)
                if user is not None:
                    auth.login(self.request, user)
                    response = HttpResponseRedirect('/book/')
                    response.set_cookie('username', ID)
                    response.set_cookie('password', pw)
                    return response
                else:
                    return render(self.request, self.template_name, context=context)
            else:
                return render(self.request, self.template_name, context=context)


# Sign in page
class SignupView(TemplateView):
    template_name =  'info/user/signup.html'    
    
    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        context['signup_form'] = SignupForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = SignupForm(data=request.POST)
        context=self.get_context_data()
        if form.is_valid():     
            ID = form.cleaned_data['user_id']
            email = form.cleaned_data['email']
            pw = form.cleaned_data['password']
            pw2 = form.cleaned_data['password2']
            try:
                if pw == pw2:
                    User = get_user_model()
                    new_user = User.objects.create_user(username=ID, email=email, password=pw)
                    auth.login(self.request, new_user)
                    
                    response = HttpResponseRedirect('/rate/page="1"')
                    response.set_cookie('username', ID)
                    response.set_cookie('password', pw)
                    return response
                else:
                    context['error_message'] = 'The passwords do not match'
                    return render(self.request, self.template_name, context=context)
            except IntegrityError:
                context['error_message'] = 'User ID already exists'
                return render(self.request, self.template_name, context=context)
        else:
            context['error_message'] = 'Enter valid information'
            return render(self.request, self.template_name, context=context)


# logout
def logout(request):
    response = HttpResponseRedirect('/')
    response.delete_cookie('username')
    response.delete_cookie('password')
    auth.logout(request)
    return response


class MyPageView(TemplateView):
    template_name = 'info/user/mypage.html'
    
    def get_context_data(self, **kwargs):
        context = super(MyPageView, self).get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        user = self.request.user
        context['liked_books'] = User_Book_Like.objects.filter(user=user)
        context['rated_books'] = User_Book.objects.filter(user=user)
        context['user'] = user
        return context
    
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
        elif request.POST.get("delete"):
            book_id = request.POST.get("delete_id")
            book = Book.objects.get(pk=book_id)
            user = self.request.user
            temp_ = User_Book.objects.filter(user=user).filter(book=book)
            temp_.delete()
            context = self.get_context_data()
            context['rating_default'] = True
            return render(request, 'info/user/mypage.html', context)

        
class DelUserView(TemplateView):
    template_name = 'info/user/deleteUser.html'
    
    def get_context_data(self, **kwargs):
        context = super(DelUserView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        ID = request.POST.get("user")
        pw = request.POST.get("pw")
        user = auth.authenticate(request, username=ID, password=pw)
        if user is not None:
            user.delete()
            return HttpResponse('<script type="text/javascript">opener.location.href = "/"; self.close();</script>')
        else:
            context.update({'error':"password is incorrect"})
            return render(request, 'info/user/deleteUser.html', context)
        return  render(request, '/mypage/deleteUser/')

    
class ChangePWView(TemplateView):
    template_name = 'info/user/changepw.html'
    
    def get_context_data(self, **kwargs):
        context = super(ChangePWView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        current_password = request.POST.get("origin_pw")
        user = request.user
        if check_password(current_password,user.password):
            new_password = request.POST.get("pw1")
            password_confirm = request.POST.get("pw2")
            if new_password == password_confirm:
                user.set_password(new_password)
                user.save()
                auth.login(request,user)
                return HttpResponse('<script type="text/javascript">window.close();</script>')
            else:
                context.update({'error':"새로운 비밀번호를 다시 확인해주세요."})
        else:
            context.update({'error':"현재 비밀번호가 일치하지 않습니다."})
        return render(request, 'info/user/changepw.html', context)


class RateView(TemplateView):
    template_name = 'info/rate.html'
    
    def get_context_data(self, **kwargs):
        context = super(RateView, self).get_context_data(**kwargs)
        context['search_form'] = SearchForm()
        
        ID, PW = get_user(self.request)
        if ID is not None:
            context['user'] = ID
            page_id = self.kwargs.get('page_id')
            context['page_id'] = page_id
            genre_names = {1: '추리/미스테리 소설',
                           2: '판타지/환상문학',
                           3: '로맨스 소설',
                           4: '테마문학'}    
            
            user = self.request.user
 
            temp_ = []
            bestseller = {}
            
            if page_id == '1':
                bestseller['genre'] = '추리/미스테리 소설'
                genre = Genre.objects.get(pk=91)
                temp_ = []
                temp_list_ = Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                 num_reviews=Count('aladin_user_book')).order_by('-num_reviews')[:100]
                for i in temp_list_:
                        j = User_Book.objects.filter(user=user).filter(book=i).first()
                        k = Book_Author.objects.filter(book=i).first()
                        temp_.append({'book': i, 'user_rated': j, 'author': k})
                bestseller['books'] = temp_
            elif page_id == '2':
                bestseller['genre'] = '판타지/환상문학'
                genre = Genre.objects.get(pk=99)
                temp_ = []
                temp_list_ = Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                 num_reviews=Count('aladin_user_book')).order_by('-num_reviews')[:100]
                for i in temp_list_:
                        j = User_Book.objects.filter(user=user).filter(book=i).first()
                        k = Book_Author.objects.filter(book=i).first()
                        temp_.append({'book': i, 'user_rated': j, 'author': k})
                bestseller['books'] = temp_
            elif page_id == '3':  
                bestseller['genre'] = '로맨스 소설'
                genre = Genre.objects.get(pk=41)
                temp_ = []
                temp_list_ = Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                 num_reviews=Count('aladin_user_book')).order_by('-num_reviews')[:100]
                for i in temp_list_:
                        j = User_Book.objects.filter(user=user).filter(book=i).first()
                        k = Book_Author.objects.filter(book=i).first()
                        temp_.append({'book': i, 'user_rated': j, 'author': k})
                bestseller['books'] = temp_
            else:
                bestseller['genre'] = '테마문학'
                genre = Genre.objects.get(pk=95)
                temp_ = []
                temp_list_ = Book.objects.filter(pk__in=Book_Genre.objects.filter(genre=genre).values('book')).annotate(
                                                 num_reviews=Count('aladin_user_book')).order_by('-num_reviews')[:100]
                for i in temp_list_:
                        j = User_Book.objects.filter(user=user).filter(book=i).first()
                        k = Book_Author.objects.filter(book=i).first()
                        temp_.append({'book': i, 'user_rated': j, 'author': k})
                bestseller['books'] = temp_
            
            context['object_list'] = bestseller
            context['genre_names'] = genre_names    

        else: 
            context['user'] = False
        
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        book_id = request.POST.get("book_id")
        book = Book.objects.get(pk=book_id)
        rating = request.POST.get("rating")
        if rating == "null":
            User_Book.objects.filter(user=user).filter(book=book).delete()
        elif User_Book.objects.filter(user=user).filter(book=book):
            temp_ = User_Book.objects.filter(user=user).filter(book=book).first()
            temp_.rating = rating
            temp_.save()
        else:
            temp_review = User_Book(user=user, book=book, rating=rating, time=datetime.datetime.now())
            temp_review.save()
        return JsonResponse({'m': "success"})   