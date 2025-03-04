from django.urls import path
from . import views

urlpatterns = [
    path('', views.dirhome),
    path('locked', views.registration, name="login"),
    path('home', views.login, name="home"),
    path('logout', views.logout, name="logout")
]
