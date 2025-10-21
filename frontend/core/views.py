from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services import api
import requests
from django.contrib import messages

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

#CARGA DE ARCHIVOS XML
def cargar_configuracion(request):
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        archivo = request.FILES.get('archivo')

        if not archivo:
            messages.error(request, "Debes seleccionar un archivo XML.")
            return redirect('cargar_configuracion')

        try:
            response = requests.post(
                "http://127.0.0.1:5000/api/cargar_xml",
                files={'archivo': archivo},
                data={'tipo': tipo}
            )

            if response.status_code == 201:
                data = response.json()
                messages.success(request, data.get('message', 'Carga exitosa'))
            else:
                try:
                    data = response.json()
                    messages.error(request, data.get('error', 'Error al procesar el archivo.'))
                except:
                    messages.error(request, "Error inesperado en la respuesta del servidor Flask.")

        except requests.exceptions.ConnectionError:
            messages.error(request, "No se pudo conectar con el servidor Flask. Verifica que esté corriendo.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")

        return redirect('cargar_configuracion')

    return render(request, 'core/cargar_configuracion.html')