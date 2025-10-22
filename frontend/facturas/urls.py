from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_facturas, name='listar_facturas'),
    path('descargar/', views.descargar_xml, name='descargar_facturas'),
]