from django.shortcuts import render
from django.http import JsonResponse
from .services import api

# Create your views here.
def home(request):
    return render(request, "core/home.html")

def listar_recursos(request):
    recursos = api.obtener_recursos()
    return JsonResponse(recursos, safe=False)

def reiniciar_sistema(request):
    resultado = api.inicializar_sistema()
    return JsonResponse(resultado)

def subir_configuracion(request):
    if request.method == "POST" and request.FILES.get("archivo"):
        archivo = request.FILES["archivo"]
        resultado = api.enviar_xml_configuracion(archivo)
        return JsonResponse(resultado)
    return JsonResponse({"error": "No se envió un archivo XML"}, status=400)