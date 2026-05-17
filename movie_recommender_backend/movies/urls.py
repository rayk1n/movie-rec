from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend,      name='recommend'),
    path('search/',    views.search_movies,  name='search'),
]