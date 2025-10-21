from django.shortcuts import render, redirect
from core.services import api
# Create your views here.

#Listar recursos

def listar_recursos(request):
    print("🟢 Entró a listar_recursos Django")
    recursos = api.obtener_recursos()
    print("📦 Recursos recibidos desde Flask:", recursos)
    return render(request, "recursos/listar.html", {"recursos": recursos})

#Crear recurso nuevo
def crear_recurso(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        abreviatura = request.POST.get("abreviatura")
        metrica = request.POST.get("metrica")
        tipo = request.POST.get("tipo")
        valor_x_hora = float(request.POST.get("valor_x_hora", 0))
        api.crear_recurso(nombre, abreviatura, metrica, tipo, valor_x_hora)
        return redirect("listar_recursos")
    return render(request, "recursos/nuevo.html")

#Eliminar un recurso
def eliminar_recurso(request, id):
    api.eliminar_recurso(id)
    return redirect("listar_recursos")
