from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('galeria/', views.gallery, name='gallery'),
    path('contacto/', views.contact, name='contact'),
]