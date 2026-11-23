from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('galeria/', views.gallery, name='gallery'),
    path('contacto/', views.contact, name='contact'),
    path('contacto/formulario/', views.contact_form_view, name='contact_form'),
    path('aviso-legal/', views.legal_notice, name='legal_notice'),
    path('politica-de-privacidad/', views.privacy_policy, name='privacy_policy'),
    path('politica-de-cookies/', views.cookie_policy, name='cookie_policy'),
]