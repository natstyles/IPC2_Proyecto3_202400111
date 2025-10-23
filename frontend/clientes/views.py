from django.shortcuts import render, redirect
import requests
from core.services import api

BACKEND_URL = "http://127.0.0.1:5000/api"

# Create your views here.
def listar_clientes(request):
    clientes = api.obtener_clientes()
    return render(request, "clientes/listar.html", {"clientes": clientes})

def crear_cliente(request):
    if request.method == "POST":
        data = {
            "nombre": request.POST.get("nombre"),
            "nit": request.POST.get("nit"),
            "direccion": request.POST.get("direccion"),
            "correo": request.POST.get("correo"),
        }

        response = requests.post(f"{BACKEND_URL}/clientes", json=data)

        if response.status_code == 201:
            # Cliente creado exitosamente
            return redirect("/clientes/")
        else:
            # Si el backend devolvió un error, lo mostramos
            error_msg = response.json().get("error", "Error desconocido al crear cliente.")
            return render(request, "clientes/nuevo.html", {"error": error_msg})

    return render(request, "clientes/nuevo.html")

def eliminar_cliente(request, id):
    try:
        api.eliminar_cliente(id)
    except Exception as e:
        print("Error al eliminar cliente:", e)
    return redirect("listar_clientes")
