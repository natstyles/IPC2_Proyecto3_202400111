from django.shortcuts import render, redirect
from core.services import api

# Create your views here.

def listar_instancias(request):
    try:
        instancias = api.obtener_instancias()
        clientes = {c["id"]: c["nombre"] for c in api.obtener_clientes()}
        configuraciones = {cfg["id"]: cfg["nombre"] for cfg in api.obtener_configuraciones()}

        # Normalizar para evitar errores por campos faltantes
        for i in instancias:
            i["cliente_nombre"] = clientes.get(i.get("cliente_id"), "Desconocido")
            i["configuracion_nombre"] = configuraciones.get(i.get("configuracion_id"), "Sin configuración")
            i["fecha_inicio"] = i.get("fecha_inicio") or "--"
            i["fecha_final"] = i.get("fecha_final") or "--"
            i["horas"] = i.get("horas", 0.0)
            i["costo_total"] = i.get("costo_total", 0.0)
            i["estado"] = i.get("estado", "VIGENTE")

        return render(request, "instancias/listar.html", {"instancias": instancias})

    except Exception as e:
        print(f"Error al obtener instancias: {e}")
        return render(request, "instancias/listar.html", {"error": "Error al conectar con el backend"})
    
def nueva_instancia(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        configuracion_id = request.POST.get('configuracion_id')
        horas = request.POST.get('horas')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_final = request.POST.get('fecha_final')

        # Enviar todos los datos al backend Flask
        response = api.crear_instancia(
            cliente_id=cliente_id,
            configuracion_id=configuracion_id,
            horas=horas,
            fecha_inicio=fecha_inicio,
            fecha_final=fecha_final
        )

        if isinstance(response, dict) and response.get("error"):
            clientes = api.obtener_clientes()
            configuraciones = api.obtener_configuraciones()
            return render(request, 'instancias/nuevo.html', {
                'clientes': clientes,
                'configuraciones': configuraciones,
                'error': response["error"]
            })

        return redirect('/instancias/')

    clientes = api.obtener_clientes()
    configuraciones = api.obtener_configuraciones()
    return render(request, 'instancias/nuevo.html', {
        'clientes': clientes,
        'configuraciones': configuraciones
    })


def cancelar_instancia(request, id):
    api.cancelar_instancia(id)
    return redirect('/instancias/')