from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_recursos, name='listar_recursos'),
    path('nuevo/', views.crear_recurso, name='crear_recurso'),
    path('eliminar/<int:id>/', views.eliminar_recurso, name='eliminar_recurso'),
]