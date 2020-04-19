# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:37:37 2020

@author: icaromarley5
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('wallet/confirm/', views.confirmWallet, name='confirmWallet'),
]

