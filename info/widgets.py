# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 13:32:47 2019

@author: 1615055
"""

from django.forms import DateInput

class FengyuanChenDatePickerInput(DateInput):
    template_name = 'widgets/fengyuanchen_datepicker.html'
   