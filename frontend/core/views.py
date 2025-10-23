from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services import api
from django.contrib import messages
from core.services.api import enviar_xml_configuracion

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

        if "error" in resultado:
            messages.error(request, resultado["error"])
        elif "resumen" in resultado:
            resumen = resultado["resumen"]
            messages.success(
                request,
                f"Archivo procesado correctamente: "
                f"{resumen.get('recursos_cargados', 0)} recursos, "
                f"{resumen.get('categorias_cargadas', 0)} categorías, "
                f"{resumen.get('configuraciones_cargadas', 0)} configuraciones, "
                f"{resumen.get('clientes_cargados', 0)} clientes, "
                f"{resumen.get('instancias_cargadas', 0)} instancias."
            )
        else:
            messages.error(request, "Error desconocido al procesar el archivo.")
        return redirect("subir_configuracion")

    return render(request, "configuracion/cargar_configuracion.html")

#CARGA DE ARCHIVOS XML
def cargar_configuracion(request):
    if request.method == 'POST':
        archivo = request.FILES.get('archivo')
        if archivo:
            resultado = enviar_xml_configuracion(archivo)
            if 'error' in resultado:
                messages.error(request, resultado['error'])
            else:
                resumen = resultado.get("resumen", {})
                messages.success(
                    request,
                    f"Archivo procesado correctamente: "
                    f"{resumen.get('recursos_cargados', 0)} recursos, "
                    f"{resumen.get('categorias_cargadas', 0)} categorías, "
                    f"{resumen.get('configuraciones_cargadas', 0)} configuraciones, "
                    f"{resumen.get('clientes_cargados', 0)} clientes, "
                    f"{resumen.get('instancias_cargadas', 0)} instancias."
                )
        else:
            messages.error(request, "No se seleccionó ningún archivo.")
    return render(request, 'core/cargar_configuracion.html')