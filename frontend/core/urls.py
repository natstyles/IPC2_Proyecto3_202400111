from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('recursos/', views.listar_recursos, name='listar_recursos'),
    path('sistema/inicializar/', views.reiniciar_sistema, name='reiniciar_sistema'),
    path('configuracion/subir/', views.subir_configuracion, name='subir_configuracion'),
]
