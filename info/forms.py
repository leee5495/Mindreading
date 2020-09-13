# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 01:29:53 2019

@author: 1615055
"""

from django import forms

from .widgets import FengyuanChenDatePickerInput

class LoginForm(forms.Form):
    user_id = forms.CharField(label='ID', max_length=100)
    password = forms.CharField(label='PW', max_length=100, widget=forms.PasswordInput())
    
class SignupForm(forms.Form):
    user_id = forms.CharField(label='Input ID', max_length=100)
    email = forms.EmailField(label='Input Email', max_length=100)
    password = forms.CharField(min_length=6, label='Input PW', max_length=100, widget=forms.PasswordInput(attrs={"type":"password"}))
    password2 = forms.CharField(min_length=6, label='Verify PW', max_length=100, widget=forms.PasswordInput(attrs={"type":"password"}))

class SearchForm(forms.Form):
    search_type = forms.ChoiceField(choices=[(1,'전체'), (2,'책'), (3,'작가'), (4,'장르'), (5, '출판사')])
    search_term = forms.CharField(label='Search ', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Search..'}))
    search_type.widget.attrs.update({'class' : 'option_in'})
    search_term.widget.attrs.update({'class' : 'text_in'})       
    
class DetailSearchForm(forms.Form):
    title = forms.CharField(label='title', max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'text_in', 'placeholder': '제목'}))
    author = forms.CharField(label='author', max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'text_in', 'placeholder': '작가'}))
    keyword = forms.CharField(label='keyword', max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'text_in', 'placeholder': '키워드(콤마와 띄어쓰기로 분리)'}))
    publisher = forms.CharField(label='publisher', max_length=300, required=False, widget=forms.TextInput(attrs={'class': 'text_in', 'placeholder': '출판사'}))
    ISBN = forms.CharField(label='ISBN', max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'text_in', 'placeholder': 'ISBN 번호'}))

    def clean(self):
        title = self.cleaned_data.get('title')
        author = self.cleaned_data.get('author')
        keyword = self.cleaned_data.get('keyword')
        publisher = self.cleaned_data.get('publisher')
        ISBN = self.cleaned_data.get('ISBN')
        if not title and not author and not keyword and not publisher and not ISBN:
            raise forms.ValidationError('적어도 하나의 값을 입력하세요')
        return self.cleaned_data
    
class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(x,x) for x in range(1,6)], widget=forms.HiddenInput())
    rating.widget.attrs.update({'id' : 'rating_val'})
    review = forms.CharField(widget=forms.Textarea)

class SortOrderForm(forms.Form):
    sort_order = forms.ChoiceField(choices=[(1, '등록일순'), (2,'가나다순'), (3,'리뷰순'), (4,'평점순'), (5,'최신순'), (6, '저가격순'), (7, '고가격순')])
    view_by = forms.ChoiceField(choices=[(100,'100'), (75,'75'), (50,'50'), (30,'30')], required=False)
    
class FilterForm(forms.Form):
    min_price = forms.IntegerField(required=False)   
    max_price = forms.IntegerField(required=False) 
    from_date = forms.DateTimeField(input_formats=['%Y/%m/%d'], required=False,
                                    widget=FengyuanChenDatePickerInput())
    to_date = forms.DateTimeField(input_formats=['%Y/%m/%d'], required=False,
                                  widget=FengyuanChenDatePickerInput())
    #min_rating = forms.FloatField(required=False)
    #min_num_rating = forms.IntegerField(required=False)
    filter_keyword = forms.CharField(max_length=300, required=False)
    
    def clean(self):
        min_price = self.cleaned_data.get('min_price')
        max_price = self.cleaned_data.get('max_price')
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        #min_rating = self.cleaned_data.get('min_rating')
        #min_num_rating = self.cleaned_data.get('min_num_rating')
        filter_keyword = self.cleaned_data.get('filter_keyword')
        if not min_price and not max_price and not from_date and not to_date and not filter_keyword: # and not min_rating and not min_num_rating
            raise forms.ValidationError('적어도 하나의 값을 입력하세요')
        return self.cleaned_data