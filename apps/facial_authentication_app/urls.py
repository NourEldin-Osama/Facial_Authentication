from django.urls import path

from apps.facial_authentication_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recognize_user', views.recognize_user, name='recognize_user'),
    path('add_user', views.add_user, name='add_user'),
]
