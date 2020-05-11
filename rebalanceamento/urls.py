# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:37:37 2020

@author: icaromarley5
"""

from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path(
        'wallet/confirm/', 
        views.confirmWallet, name='confirmWallet'
    ),
    path(
        'stock-autocomplete/',
        views.StockAutocomplete.as_view(),
        name='stock-autocomplete',
    ),
    path(
        'wallet/confirm/', 
        views.confirmWallet, name='confirmWallet'
    ),
    path(
        'wallet/redo/', 
        views.redoWallet, name='redoWallet'
    ),
    re_path(
        '(.|//)+', views.redirect404, name='404'
    ),
]

