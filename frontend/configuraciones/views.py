from django.shortcuts import render, redirect
from core.services import api

# Create your views here.
def listar_configuraciones(request):
    configuraciones = api.obtener_configuraciones()
    recursos = api.obtener_recursos()

    # Construimos un diccionario para mostrar nombres de recursos
    recursos_dict = {r["id"]: r["nombre"] for r in recursos}
    for c in configuraciones:
        for r in c.get("recursos", []):
            r["nombre_recurso"] = recursos_dict.get(r.get("id_recurso"), "Desconocido")

    return render(request, "configuraciones/listar.html", {"configuraciones": configuraciones})

def nueva_configuracion(request):
    #Obtener categorías y recursos para llenar los selects del formulario
    categorias = api.obtener_categorias()
    recursos = api.obtener_recursos()

    if request.method == "POST":
        #Capturar datos del formulario
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        categoria_id = request.POST.get("categoria_id")

        #Capturar los recursos seleccionados y sus cantidades
        recursos_data = []
        for recurso in recursos:
            cantidad = request.POST.get(f"cantidad_{recurso['id']}")
            if cantidad and float(cantidad) > 0:
                recursos_data.append({
                    "id_recurso": recurso["id"],
                    "cantidad": float(cantidad)
                })

        #Crear el payload para enviar al backend Flask
        nueva_config = {
            "nombre": nombre,
            "descripcion": descripcion,
            "categoria_id": int(categoria_id),
            "recursos": recursos_data
        }

        #Enviar al backend Flask
        api.crear_configuracion(nueva_config)

        #Redirigir al listado de configuraciones
        return redirect("/configuraciones/")

    #Si es GET, mostrar el formulario vacío
    contexto = {
        "categorias": categorias,
        "recursos": recursos
    }
    return render(request, "configuraciones/nuevo.html", contexto)

def eliminar_configuracion(request, id):
    api.eliminar_configuracion(id)
    return redirect('/configuraciones/')
