from django.shortcuts import render
from core.services.api import obtener_facturas
from django.http import FileResponse
import requests

BACKEND_URL = "http://127.0.0.1:5000/api"
# Create your views here.

def listar_facturas(request):
    facturas = obtener_facturas()
    return render(request, "facturas/listar.html", {"facturas": facturas})

def descargar_xml(request):
    try:
        response = requests.get(f"{BACKEND_URL}/facturas/xml", stream=True)
        if response.status_code == 200:
            return FileResponse(response.raw, as_attachment=True, filename="facturas.xml")
    except Exception as e:
        print("Error descargando XML:", e)
    return render(request, "facturas/listar.html", {"error": "No se pudo descargar el archivo"})