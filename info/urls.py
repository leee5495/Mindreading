# -*- coding: utf-8 -*-
"""info URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from info.views import info_views, search_views, user_views

app_name = 'info'

urlpatterns= [
                # user-related: login, logout, signup, initial rating, my page
                url(r'^$', user_views.IndexView.as_view(), name='index'),
                url(r'^signup/$', user_views.SignupView.as_view(), name='signup'),
                url(r'^mypage/$', user_views.MyPageView.as_view(), name='mypage'),
                url(r'^mypage/changepw/$', user_views.ChangePWView.as_view(), name='mypage'),
                url(r'^mypage/deleteUser/$', user_views.DelUserView.as_view(), name='mypage'),
                url(r'^logout/$', user_views.logout, name='logout'),
                
                url(r'^rate/page="(?P<page_id>\d+)"/$', user_views.RateView.as_view(), name='rate'),
                
                # book list
                url(r'^book/$', info_views.BookListView.as_view(), name='book_list'),
                url(r'^book/sort_order="(?P<sort_order>\w+)"/view_by="(?P<view_by>\w+)"/filter_by=price(?P<min_price>\w+)~(?P<max_price>\w+)&pub_date(?P<from_date>\d+\/\d+\/\d+|\w+)~(?P<to_date>\d+\/\d+\/\d+|\w+)&keyword="(?P<filter_keyword>[\w+, ]*)"/$', info_views.BookListView.as_view(), name='book_list_sorted'), #min_rating(?P<min_rating>[\w|.]+)&min_num_rating(?P<min_num_rating>\w+)&
                url(r'^book/genre="(?P<genre_id>\w+)"/sort_order="(?P<sort_order>\w+)"/view_by="(?P<view_by>\w+)"/filter_by=price(?P<min_price>\w+)~(?P<max_price>\w+)&pub_date(?P<from_date>\d+\/\d+\/\d+|\w+)~(?P<to_date>\d+\/\d+\/\d+|\w+)&keyword="(?P<filter_keyword>[\w+, ]*)"/$', info_views.BookListView.as_view(), name='book_list_genre'), #min_rating(?P<min_rating>[\w|.]+)&min_num_rating(?P<min_num_rating>\w+)&
                
                # book detail page
                url(r'^book/detail/id="(?P<pk>\d+)"/$', info_views.BookDetailView.as_view(), name='book_detail'),
              
                # author/publisher/genre detail page
                url(r'^(?P<detail_type>author|publisher|genre|aladin_user|user)/detail/id="(?P<pk>\d+)"/$', info_views.GridDetailView.as_view(), name='grid_detail'),
                url(r'^(?P<detail_type>author|publisher|genre|aladin_user|user)/detail/id="(?P<pk>\d+)"/sort_order="(?P<sort_order>\w+)"/view_by="(?P<view_by>\w+)"/$', info_views.GridDetailView.as_view(), name='grid_detail_sorted'),
              
                # search
                url(r'^search/$', search_views.SearchView.as_view(), name='search'),
                # search result
                url(r'^search/type="(?P<search_type>\d)"/term="(?P<search_term>[\w+, ]*)"/$', search_views.SearchResultView.as_view(), name='search_result'),
                url(r'^search/type="(?P<search_type>\d)"/term="(?P<search_term>[\w+, ]*)"/sort_order="(?P<sort_order>\w+)/filter_by=price(?P<min_price>\w+)~(?P<max_price>\w+)&pub_date(?P<from_date>\d+\/\d+\/\d+|\w+)~(?P<to_date>\d+\/\d+\/\d+|\w+)&min_rating(?P<min_rating>[\w|.]+)&min_num_rating(?P<min_num_rating>\w+)&keyword="(?P<filter_keyword>[\w+, ]*)"/$', search_views.SearchResultView.as_view(), name='search_result_sorted'),
                
                # detail search
                url(r'^detail_search/$', search_views.DetailSearchView.as_view(), name='detail_search'),
                # detail search result
                url(r'^detail_search/title="(?P<title>[\w+, ]*)"/author="(?P<author>[\w+, ]*)"/keyword="(?P<keyword>[\w+, ]*)"/pub="(?P<publisher>[\w+, ]*)"/ISBN="(?P<ISBN>[\w+, ]*)"$', search_views.DetailSearchResultView.as_view(), name='detail_search_result'),
                url(r'^detail_search/title="(?P<title>[\w+, ]*)"/author="(?P<author>[\w+, ]*)"/keyword="(?P<keyword>[\w+, ]*)"/pub="(?P<publisher>[\w+, ]*)"/ISBN="(?P<ISBN>[\w+, ]*)"/sort_order="(?P<sort_order>\w+)/view_by="(?P<view_by>\w+)"/filter_by=price(?P<min_price>\w+)~(?P<max_price>\w+)&pub_date(?P<from_date>\d+\/\d+\/\d+|\w+)~(?P<to_date>\d+\/\d+\/\d+|\w+)&min_rating(?P<min_rating>[\w|.]+)&min_num_rating(?P<min_num_rating>\w+)&keyword="(?P<filter_keyword>[\w+, ]*)"/$', search_views.DetailSearchResultView.as_view(), name='detail_search_result_sorted'),
              
                # recommenation page
                url(r'^recommend/page="(?P<page_id>\d+)"/$', info_views.RecommendationView.as_view(), name='recommend'),
              ]