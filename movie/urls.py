from django.contrib import admin
from django.urls import path, include
from movie import views as movieViews

urlpatterns = [
    path('recommend/', movieViews.recommend, name='recommend'),
]
