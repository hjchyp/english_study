"""engs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,re_path,include
from recite.views import *

urlpatterns = [
    re_path('^login/$', LoginView.as_view(), name='login'),
    re_path('^$', Index.as_view(), name='Index'),
    re_path('^logout/$', LogoutView.as_view(), name='logout'),
    re_path('^learning/$', Learning.as_view(), name='learning'),
    re_path('^yybycycy_menu/$', yybycycyMenu.as_view(), name='yybycycy_menu'),
    re_path('^reviewing/$', Reviewing.as_view(), name='reviewing'),
    re_path('^index/$', Index.as_view(), name='index')
]
