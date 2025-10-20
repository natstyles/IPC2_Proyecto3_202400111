from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app) #Peticiones del frontend

#base de datos simulada
recursos = []
clientes = []
instancias = []

#funcion aux
def buscar_por_id(lista, id):
    for item in lista:
        if item["id"] == id:
            return item
    return None

#endpoints para recursos
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

#endpoints de clientes
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
    nuevo = request.json
    clientes.append(nuevo)
    return jsonify(nuevo), 201

@app.route('/api/clientes/<string:nit>', methods=['DELETE'])
def eliminar_cliente(nit):
    global clientes
    clientes = [c for c in clientes if c["nit"] != nit]
    return jsonify({"message": "Cliente eliminado"}), 200

#endpoints instancias
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

#sistem
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