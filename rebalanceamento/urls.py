# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 17:37:37 2020

@author: icaromarley5
"""

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('wallet/checkResults/<str:cpf>/', views.checkResults, name='checkResults'),
    path('wallet/plotPlan/<str:cpf>/', views.plotPlan, name='plotPlan'),
    path('wallet/confirm/<str:cpf>/', views.confirmWallet, name='confirmWallet'),
]

