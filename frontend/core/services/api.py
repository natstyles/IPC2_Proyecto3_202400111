import requests

#URL base de Flask
BACKEND_URL = "http://localhost:5000/api"

#RECURSOS
def obtener_recursos():
    try:
        r = requests.get(f"{BACKEND_URL}/recursos")
        r.raise_for_status()  # lanza excepción si hay error 4xx/5xx
        return r.json()
    except Exception as e:
        print(f"Error al obtener recursos: {e}")
        return []

def crear_recurso(nombre, abreviatura, metrica, tipo, valor_x_hora):
    data = {
        "nombre": nombre,
        "abreviatura": abreviatura,
        "metrica": metrica,
        "tipo": tipo,
        "valor_x_hora": valor_x_hora
    }

    try:
        response = requests.post(f"{BACKEND_URL}/recursos", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            # Devuelve el mensaje de error del backend
            return response.json()
    except Exception as e:
        return {"error": f"Error al conectar con el backend: {e}"}

def eliminar_recurso(id_recurso):
    r = requests.delete(f"{BACKEND_URL}/recursos/{id_recurso}")
    return r.json()

#CLIENTES
def obtener_clientes():
    r = requests.get(f"{BACKEND_URL}/clientes")
    return r.json()

def crear_cliente(nombre, nit, direccion, correo):
    payload = {
        "nombre": nombre,
        "nit": nit,
        "direccion": direccion,
        "correo": correo
    }
    r = requests.post(f"{BACKEND_URL}/clientes", json=payload)
    try:
        return r.json()
    except ValueError:
        print("Error decodificando JSON:", r.text)
        return {"error": "Respuesta inválida del servidor Flask"}
    
def eliminar_cliente(cliente_id):
    url = f"{BACKEND_URL}/clientes/{cliente_id}"
    r = requests.delete(url)
    
    # Si Flask devuelve JSON, lo retornamos, si no, devolvemos un mensaje genérico
    try:
        return r.json()
    except ValueError:
        return {"message": f"Cliente {cliente_id} eliminado"}

#INSTANCIAS
def obtener_instancias():
    r = requests.get(f"{BACKEND_URL}/instancias")
    return r.json()

def crear_instancia(cliente_id, recurso_id, horas):
    payload = {
        "cliente_id": cliente_id,
        "recurso_id": recurso_id,
        "horas": horas
    }

    try:
        r = requests.post(f"{BACKEND_URL}/instancias", json=payload)

        # Si Flask devuelve un error, lo devolvemos a Django
        if r.status_code == 201:
            return r.json()
        else:
            try:
                return r.json()
            except Exception:
                return {"error": f"Error desconocido (código {r.status_code})"}

    except requests.exceptions.RequestException as e:
        #Error de conexión o backend caído
        return {"error": f"No se pudo conectar con el backend: {e}"}


def cancelar_instancia(id):
    r = requests.put(f"{BACKEND_URL}/instancias/{id}/cancelar")
    return r.json()

#SISTEMA
def inicializar_sistema():
    r = requests.post(f"{BACKEND_URL}/sistema/inicializar")
    return r.json()

#XMLS
def enviar_xml_configuracion(archivo):
    files = {'archivo': archivo}
    r = requests.post(f"{BACKEND_URL}/configuracion/cargar-xml", files=files)
    return r.json()

def enviar_xml_consumos(archivo):
    files = {'archivo': archivo}
    r = requests.post(f"{BACKEND_URL}/consumos/cargar-xml", files=files)
    return r.json()

#FACTURAS
def obtener_facturas():
    try:
        response = requests.get(f"{BACKEND_URL}/facturas")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener facturas: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión con el backend: {e}")
        return []
