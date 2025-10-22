from django.shortcuts import render, redirect
from core.services import api
# Create your views here.

#Listar recursos

def listar_recursos(request):
    print("Entró a listar_recursos Django")
    recursos = api.obtener_recursos()
    print("Recursos recibidos desde Flask:", recursos)
    return render(request, "recursos/listar.html", {"recursos": recursos})

#Crear recurso nuevo
def crear_recurso(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        abreviatura = request.POST.get("abreviatura")
        metrica = request.POST.get("metrica")
        tipo = request.POST.get("tipo")
        valor_x_hora = request.POST.get("valor_x_hora")

        #Enviar datos al backend Flask
        response = api.crear_recurso(nombre, abreviatura, metrica, tipo, valor_x_hora)

        #Si Flask devuelve un error, mostrarlo en el formulario
        if isinstance(response, dict) and response.get("error"):
            return render(request, "recursos/nuevo.html", {"error": response["error"]})

        #Si todo va bien, redirigir al listado
        return redirect("listar_recursos")

    return render(request, "recursos/nuevo.html")


#Eliminar un recurso
def eliminar_recurso(request, id):
    api.eliminar_recurso(id)
    return redirect("listar_recursos")
