from flask import Flask, jsonify, request
from flask_cors import CORS
import secrets
import string

app = Flask(__name__)
CORS(app) #Peticiones del frontend

#base de datos simulada
recursos = []
clientes = []
instancias = []

#----------------------------------------------FUNCIONES AUXILIARES
#buscar por id
def buscar_por_id(lista, id):
    for item in lista:
        if item["id"] == id:
            return item
    return None

#generar claves aleatorias
def generar_clave(longitud: int = 12) -> str:
    #expresion regular
    alfabeto = string.ascii_letters + string.digits # [a-zA-Z0-9]
    while True:
        clave = ''.join(secrets.choice(alfabeto) for _ in range(longitud))
        if (any(c.islower() for c in clave)
            and any(c.isupper() for c in clave)
            and any(c.isdigit() for c in clave)):
            return clave

def sugerir_usuario_desde_correo(correo: str, clientes_existentes: list) -> str:
    base = (correo or "").split('@')[0] or "user"
    existentes = {c.get("usuario") for c in clientes_existentes if c.get("usuario")}
    usuario = base
    sufijo = 1
    while usuario in existentes:
        sufijo += 1
        usuario = f"{base}{sufijo}"
    return usuario

#----------------------------------------------ENDPOINTS RECURSOS
@app.route('/api/recursos', methods=['GET'])
def obtener_recursos():
    return jsonify(recursos)

@app.route('/api/recursos/<int:id>', methods=['GET'])
def obtener_recurso(id):
    recurso = buscar_por_id(recursos, id)
    if recurso:
        return jsonify(recurso)
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.route('/api/recursos', methods=['POST'])
def crear_recurso():
    nuevo = request.json
    nuevo["id"] = len(recursos) + 1
    recursos.append(nuevo)
    return jsonify(nuevo), 201

@app.route('/api/recursos/<int:id>', methods=['PUT'])
def actualizar_recurso(id):
    recurso = buscar_por_id(recursos, id)
    if recurso:
        recurso.update(request.json)
        return jsonify(recurso)
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.route('/api/recursos/<int:id>', methods=['DELETE'])
def eliminar_recurso(id):
    global recursos
    recursos = [r for r in recursos if r["id"] != id]
    return jsonify({"message": "Recurso eliminado"}), 200

#----------------------------------------------ENDPOINTS CLIENTES
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    return jsonify(clientes)

@app.route('/api/clientes/<string:nit>', methods=['GET'])
def obtener_cliente(nit):
    cliente = next((c for c in clientes if c["nit"] == nit), None)
    if cliente:
        return jsonify(cliente)
    return jsonify({"error": "Cliente no encontrado"}), 404

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    data = request.get_json() or {}
    nombre = data.get("nombre")
    nit = data.get("nit")
    direccion = data.get("direccion")
    correo = data.get("correo")

    if not all([nombre, nit, direccion, correo]):
        return jsonify({"error": "Faltan campos requeridos"}), 400

    usuario = sugerir_usuario_desde_correo(correo, clientes)
    clave = generar_clave()

    nuevo_cliente = {
        "id": len(clientes) + 1,
        "nombre": nombre,
        "nit": nit,
        "direccion": direccion,
        "correo": correo,
        "usuario": usuario,
        "clave": clave
    }

    clientes.append(nuevo_cliente)
    print("Cliente registrado:", nuevo_cliente)
    return jsonify(nuevo_cliente), 201

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    global clientes
    clientes = [c for c in clientes if c.get("id") != id]
    return jsonify({"message": "Cliente eliminado"}), 200

#----------------------------------------------ENDPOINTS INSTANCIAS
@app.route('/api/instancias', methods=['GET'])
def obtener_instancias():
    return jsonify(instancias)

@app.route('/api/instancias', methods=['POST'])
def crear_instancia():
    nueva = request.json
    nueva["id"] = len(instancias) + 1
    nueva["estado"] = "Vigente"
    instancias.append(nueva)
    return jsonify(nueva), 201

@app.route('/api/instancias/<int:id>/cancelar', methods=['PUT'])
def cancelar_instancia(id):
    instancia = buscar_por_id(instancias, id)
    if instancia:
        instancia["estado"] = "Cancelada"
        return jsonify(instancia)
    return jsonify({"error": "Instancia no encontrada"}), 404

#SISTEMA
@app.route('/api/sistema/inicializar', methods=['POST'])
def inicializar():
    global recursos, clientes, instancias
    recursos = []
    clientes = []
    instancias = []
    return jsonify({"ok": True, "mensaje": "Sistema inicializado correctamente."})

@app.route('/')
def home():
    return jsonify({"message": "Backend activo - Flask"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)