from django.urls import path
from . import views

urlpatterns = [
    path('locked', views.registration, name="login"),
    path('check', views.login, name="home")
]
