from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_instancias, name='listar_instancias'),
    path('nuevo/', views.nueva_instancia, name='nueva_instancia'),
    path('cancelar/<int:id>/', views.cancelar_instancia, name='cancelar_instancia'),
]
