from django.urls import path
from . import views

urlpatterns = [
    path('', views.dirhome),
    path('locked', views.registration, name="login"),
    path('home', views.login, name="home"),
    path('logout', views.logout, name="logout"),
    path('about', views.about, name="about"),
    path('team', views.team, name="team"),
    path('product', views.product, name="product"),
    path('product/<str:category>/', views.product_redirect, name="product_dynamic"),
    path('save_image/', views.save_image, name='save_image'),
    path('upload_video/', views.upload_video, name='upload_video'),
    path('process_video/', views.process_video, name='process_video'),
    path("start-webcam/", views.start_webcam, name="start-webcam"),
]