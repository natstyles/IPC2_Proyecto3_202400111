from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clientes, name='listar_clientes'),
    path('nuevo/', views.crear_cliente, name='crear_cliente'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
]
