from django.shortcuts import render, redirect
from core.services import api

# Create your views here.

def listar_instancias(request):
    instancias = api.obtener_instancias()
    clientes = api.obtener_clientes()
    recursos = api.obtener_recursos()

    # Crear diccionarios para traducir IDs a nombres
    clientes_dict = {c["id"]: c["nombre"] for c in clientes}
    recursos_dict = {r["id"]: r["nombre"] for r in recursos}

    #Mostramos quien usa cada instancia con nombre
    for i in instancias:
        i["cliente_nombre"] = clientes_dict.get(i.get("cliente_id"), "Desconocido")
        i["recurso_nombre"] = recursos_dict.get(i.get("recurso_id"), "Desconocido")

    return render(request, 'instancias/listar.html', {
        'instancias': instancias
    })

def nueva_instancia(request):
    if request.method == 'POST':
        cliente_id = int(request.POST.get('cliente_id'))
        recurso_id = int(request.POST.get('recurso_id'))
        horas = float(request.POST.get('horas'))
        api.crear_instancia(cliente_id, recurso_id, horas)
        return redirect('/instancias/')
    clientes = api.obtener_clientes()
    recursos = api.obtener_recursos()
    return render(request, 'instancias/nuevo.html', {
        'clientes': clientes,
        'recursos': recursos
    })

def cancelar_instancia(request, id):
    api.cancelar_instancia(id)
    return redirect('/instancias/')