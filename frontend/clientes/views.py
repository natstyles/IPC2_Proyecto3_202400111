from django.shortcuts import render, redirect
from core.services import api

# Create your views here.
def listar_clientes(request):
    clientes = api.obtener_clientes()
    return render(request, "clientes/listar.html", {"clientes": clientes})

def crear_cliente(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        nit = request.POST.get("nit")
        direccion = request.POST.get("direccion")
        correo = request.POST.get("correo")

        api.crear_cliente(nombre, nit, direccion, correo)
        return redirect("listar_clientes")

    return render(request, "clientes/nuevo.html")

def eliminar_cliente(request, id):
    api.eliminar_cliente(id)
    return redirect("listar_clientes")