import requests

#URL base de Flask
BACKEND_URL = "http://localhost:5000/api"

#RECURSOS
def obtener_recursos():
    r = requests.get(f"{BACKEND_URL}/recursos")
    return r.json()

def crear_recurso(nombre, abreviatura, metrica, tipo, valor_x_hora):
    data = {
        "nombre": nombre,
        "abreviatura": abreviatura,
        "metrica": metrica,
        "tipo": tipo,
        "valor_x_hora": valor_x_hora
    }
    r = requests.post(f"{BACKEND_URL}/recursos", json=data)
    return r.json()

def eliminar_recurso(id_recurso):
    r = requests.delete(f"{BACKEND_URL}/recursos/{id_recurso}")
    return r.json()


#CLIENTES
def obtener_clientes():
    r = requests.get(f"{BACKEND_URL}/clientes")
    return r.json()

def crear_cliente(nit, nombre, usuario, clave, direccion, correo):
    data = {
        "nit": nit,
        "nombre": nombre,
        "usuario": usuario,
        "clave": clave,
        "direccion": direccion,
        "correo": correo
    }
    r = requests.post(f"{BACKEND_URL}/clientes", json=data)
    return r.json()

#INSTANCIAS
def obtener_instancias():
    r = requests.get(f"{BACKEND_URL}/instancias")
    return r.json()

def crear_instancia(id_config, nombre):
    data = {
        "id_configuracion": id_config,
        "nombre": nombre
    }
    r = requests.post(f"{BACKEND_URL}/instancias", json=data)
    return r.json()

def cancelar_instancia(id_instancia):
    r = requests.put(f"{BACKEND_URL}/instancias/{id_instancia}/cancelar")
    return r.json()

#SISTEMA
def inicializar_sistema():
    r = requests.post(f"{BACKEND_URL}/sistema/inicializar")
    return r.json()

#XMLS
def enviar_xml_configuracion(archivo):
    """Envía un archivo XML de configuración al backend."""
    files = {'archivo': archivo}
    r = requests.post(f"{BACKEND_URL}/configuracion/cargar-xml", files=files)
    return r.json()

def enviar_xml_consumos(archivo):
    """Envía un archivo XML de consumos al backend."""
    files = {'archivo': archivo}
    r = requests.post(f"{BACKEND_URL}/consumos/cargar-xml", files=files)
    return r.json()
