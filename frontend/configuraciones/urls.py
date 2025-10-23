from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_configuraciones, name='listar_configuraciones'),
    path('nuevo/', views.nueva_configuracion, name='nueva_configuracion'),
    path('eliminar/<int:id>/', views.eliminar_configuracion, name='eliminar_configuracion'),
]
