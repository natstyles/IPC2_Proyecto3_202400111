import xml.etree.ElementTree as ET
from werkzeug.utils import secure_filename
from flask import Flask, jsonify, request, send_file, Response
from flask_cors import CORS
import secrets
import string
import json, os
from xml.etree import ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
CORS(app) #Peticiones del frontend

#---------------------------------------------- CONFIGURACIÓN INICIAL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Archivos de datos
CLIENTES_FILE = os.path.join(DATA_DIR, "clientes.json")
RECURSOS_FILE = os.path.join(DATA_DIR, "recursos.json")
INSTANCIAS_FILE = os.path.join(DATA_DIR, "instancias.json")
CONSUMOS_FILE = os.path.join(DATA_DIR, "consumos.json")
FACTURAS_FILE = os.path.join(DATA_DIR, "facturas.json")
CATEGORIAS_FILE = os.path.join(DATA_DIR, "categorias.json")
CONFIGURACIONES_FILE = os.path.join(DATA_DIR, "configuraciones.json")

#---------------------------------------------- FUNCIONES DE UTILIDAD
def cargar_datos(ruta, datos_defecto):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(ruta):
        guardar_datos(ruta, datos_defecto)
        return datos_defecto
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return datos_defecto

def guardar_datos(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def buscar_por_id(lista, id):
    """Busca un elemento por ID en una lista de diccionarios."""
    for item in lista:
        if item["id"] == id:
            return item
    return None

#---------------------------------------------- CARGA INICIAL DE DATOS PERSISTENTES
recursos = cargar_datos(RECURSOS_FILE, [])
clientes = cargar_datos(CLIENTES_FILE, [])
instancias = cargar_datos(INSTANCIAS_FILE, [])
categorias = cargar_datos(CATEGORIAS_FILE, [])
configuraciones = cargar_datos(CONFIGURACIONES_FILE, [])

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

#----------------------------------------------CARGA DE ARCHIVO DE CONFIGURACIÓN GLOBAL
@app.route('/api/configuracion', methods=['POST'])
def cargar_configuracion():
    """Carga un XML con recursos, categorías, configuraciones y clientes (robusto: case-insensitive y sin namespaces).
       Hace upsert (crea/actualiza) y devuelve resúmenes coherentes con tu frontend.
    """

    if 'archivo' not in request.files:
        return jsonify({"error": "No se envió ningún archivo XML"}), 400

    archivo = request.files['archivo']

    try:
        tree = ET.parse(archivo)
        root = tree.getroot()
    except Exception as e:
        return jsonify({"error": f"Error al procesar XML: {str(e)}"}), 400

    # Helpers
    def tag_name(element):
        if '}' in element.tag:
            return element.tag.split('}', 1)[1].lower()
        return element.tag.lower()

    def find_child(parent, name):
        for c in parent:
            if tag_name(c) == name.lower():
                return c
        return None

    print("=== DEBUG ESTRUCTURA XML ===")
    print("Raíz:", tag_name(root))
    print("Etiquetas hijas:", [tag_name(c) for c in root])
    print("=============================")

    # Contadores
    nuevos_recursos = 0
    recursos_actualizados = 0
    nuevas_categorias = 0
    categorias_actualizadas = 0
    nuevas_configuraciones = 0
    configuraciones_actualizadas = 0
    nuevos_clientes = 0
    clientes_actualizados = 0
    nuevas_instancias = 0
    instancias_actualizadas = 0

    # ---------------------- RECURSOS (upsert) ----------------------
    lista_recursos = find_child(root, "listarecursos")
    if lista_recursos is not None:
        recursos_xml = [r for r in lista_recursos if tag_name(r) == "recurso"]
        print(f"DEBUG -> Recursos detectados en XML: {len(recursos_xml)}")

        # índice de recursos por id para buscar rápido
        idx_recursos = {r["id"]: r for r in recursos if "id" in r}

        for elem in recursos_xml:
            id_attr = next((elem.attrib[k] for k in elem.attrib if "id" in k.lower()), None)
            recurso_id = int(id_attr) if id_attr and str(id_attr).isdigit() else 0
            data = {
                "id": recurso_id,
                "nombre": (elem.findtext("nombre") or "").strip(),
                "abreviatura": (elem.findtext("abreviatura") or "").strip(),
                "metrica": (elem.findtext("metrica") or "").strip(),
                "tipo": (elem.findtext("tipo") or "").strip(),
                "valor_x_hora": float(elem.findtext("valorXhora", 0))
            }
            if recurso_id == 0:
                print("⚠️  Recurso ignorado por ID inválido")
                continue

            if recurso_id in idx_recursos:
                # actualizar
                idx_recursos[recurso_id].update(data)
                recursos_actualizados += 1
            else:
                # crear
                recursos.append(data)
                idx_recursos[recurso_id] = data
                nuevos_recursos += 1

        guardar_datos(RECURSOS_FILE, recursos)
        print(f"✅ Recursos -> nuevos: {nuevos_recursos}, actualizados: {recursos_actualizados}")

    # ---------------------- CATEGORÍAS y CONFIGURACIONES (upsert) ----------------------
    lista_categorias = find_child(root, "listacategorias")
    if lista_categorias is not None:
        cats_xml = [c for c in lista_categorias if tag_name(c) == "categoria"]
        print(f"DEBUG -> Categorías detectadas en XML: {len(cats_xml)}")

        idx_categorias = {c["id"]: c for c in categorias if "id" in c}
        idx_configuraciones = {c["id"]: c for c in configuraciones if "id" in c}

        for cat in cats_xml:
            id_cat = next((cat.attrib[k] for k in cat.attrib if "id" in k.lower()), None)
            cat_id = int(id_cat) if id_cat and str(id_cat).isdigit() else None
            if cat_id is None:
                # si viniera sin id, asignamos uno nuevo incremental
                cat_id = (max([c["id"] for c in categorias], default=0) + 1)

            cat_data = {
                "id": cat_id,
                "nombre": (cat.findtext("nombre") or "").strip(),
                "descripcion": (cat.findtext("descripcion") or "").strip(),
                "carga_trabajo": (cat.findtext("cargaTrabajo") or "").strip()
            }

            if cat_id in idx_categorias:
                idx_categorias[cat_id].update(cat_data)
                categorias_actualizadas += 1
            else:
                categorias.append(cat_data)
                idx_categorias[cat_id] = cat_data
                nuevas_categorias += 1

            # Configuraciones dentro de la categoría
            lista_config = find_child(cat, "listaconfiguraciones")
            if lista_config is not None:
                confs_xml = [c for c in lista_config if tag_name(c) == "configuracion"]
                for conf in confs_xml:
                    id_conf = next((conf.attrib[k] for k in conf.attrib if "id" in k.lower()), None)
                    conf_id = int(id_conf) if id_conf and str(id_conf).isdigit() else None
                    if conf_id is None:
                        conf_id = (max([c["id"] for c in configuraciones], default=0) + 1)

                    conf_data = {
                        "id": conf_id,
                        "nombre": (conf.findtext("nombre") or "").strip(),
                        "descripcion": (conf.findtext("descripcion") or "").strip(),
                        "categoria_id": cat_id,
                        "recursos": []
                    }

                    # recursosConfiguracion
                    rec_conf = find_child(conf, "recursosconfiguracion")
                    if rec_conf is not None:
                        for rnode in rec_conf:
                            if tag_name(rnode) == "recurso":
                                rid_attr = next((rnode.attrib[k] for k in rnode.attrib if "id" in k.lower()), None)
                                rid = int(rid_attr) if rid_attr and str(rid_attr).isdigit() else 0
                                cantidad = float((rnode.text or "0").strip())
                                conf_data["recursos"].append({"id_recurso": rid, "cantidad": cantidad})

                    if conf_id in idx_configuraciones:
                        idx_configuraciones[conf_id].update({
                            k: v for k, v in conf_data.items() if k != "recursos"
                        })
                        # reemplazar lista de recursos de la configuración
                        idx_configuraciones[conf_id]["recursos"] = conf_data["recursos"]
                        configuraciones_actualizadas += 1
                    else:
                        configuraciones.append(conf_data)
                        idx_configuraciones[conf_id] = conf_data
                        nuevas_configuraciones += 1

        guardar_datos(CATEGORIAS_FILE, categorias)
        guardar_datos(CONFIGURACIONES_FILE, configuraciones)
        print(f"✅ Categorías -> nuevas: {nuevas_categorias}, actualizadas: {categorias_actualizadas}")
        print(f"✅ Configuraciones -> nuevas: {nuevas_configuraciones}, actualizadas: {configuraciones_actualizadas}")

    # ---------------------- CLIENTES e INSTANCIAS (upsert) ----------------------
    lista_clientes = find_child(root, "listaclientes")
    if lista_clientes is not None:
        clientes_xml = [c for c in lista_clientes if tag_name(c) == "cliente"]
        print(f"DEBUG -> Clientes detectados en XML: {len(clientes_xml)}")

        # índices para búsquedas rápidas
        idx_clientes_por_nit = {c.get("nit"): c for c in clientes if c.get("nit")}
        idx_instancias = {i["id"]: i for i in instancias if "id" in i}

        for cli in clientes_xml:
            nit_attr = next((cli.attrib[k] for k in cli.attrib if "nit" in k.lower()), None)
            nit = nit_attr or f"NO_NIT_{len(clientes)+1}"

            cli_data = {
                "nombre": (cli.findtext("nombre") or "").strip(),
                "usuario": (cli.findtext("usuario") or "").strip(),
                "clave": (cli.findtext("clave") or "").strip(),
                "direccion": (cli.findtext("direccion") or "").strip(),
                "correo": (cli.findtext("correoElectronico") or "").strip(),
                "nit": nit
            }

            if nit in idx_clientes_por_nit:
                # actualizar existente
                idx_clientes_por_nit[nit].update(cli_data)
                cliente_id = idx_clientes_por_nit[nit]["id"]
                clientes_actualizados += 1
            else:
                # crear nuevo con id incremental seguro
                cliente_id = (max([c["id"] for c in clientes], default=0) + 1)
                nuevo = {"id": cliente_id, **cli_data}
                clientes.append(nuevo)
                idx_clientes_por_nit[nit] = nuevo
                nuevos_clientes += 1

            # Instancias del cliente (upsert por id)
            lista_instancias = find_child(cli, "listainstancias")
            if lista_instancias is not None:
                for inst in lista_instancias:
                    if tag_name(inst) != "instancia":
                        continue
                    # id de instancia
                    inst_id_raw = inst.get("id")
                    inst_id = int(inst_id_raw) if inst_id_raw and str(inst_id_raw).isdigit() else (max([i["id"] for i in instancias], default=0) + 1)

                    inst_data = {
                        "id": inst_id,
                        "cliente_id": cliente_id,
                        "configuracion_id": int(inst.findtext("idConfiguracion", 0)),
                        "nombre": (inst.findtext("nombre") or "").strip(),
                        "fecha_inicio": (inst.findtext("fechaInicio") or "").strip(),
                        "estado": (inst.findtext("estado") or "").strip(),
                        "fecha_final": (inst.findtext("fechaFinal") or "").strip(),
                        "horas": 0.0 if idx_instancias.get(inst_id) is None else idx_instancias[inst_id].get("horas", 0.0),
                        "costo_total": 0.0 if idx_instancias.get(inst_id) is None else idx_instancias[inst_id].get("costo_total", 0.0),
                        "recurso_id": None if idx_instancias.get(inst_id) is None else idx_instancias[inst_id].get("recurso_id")
                    }

                    if inst_id in idx_instancias:
                        idx_instancias[inst_id].update(inst_data)
                        instancias_actualizadas += 1
                    else:
                        instancias.append(inst_data)
                        idx_instancias[inst_id] = inst_data
                        nuevas_instancias += 1

        guardar_datos(CLIENTES_FILE, clientes)
        guardar_datos(INSTANCIAS_FILE, instancias)
        print(f"✅ Clientes -> nuevos: {nuevos_clientes}, actualizados: {clientes_actualizados}")
        print(f"✅ Instancias -> nuevas: {nuevas_instancias}, actualizadas: {instancias_actualizadas}")

    # --------- Resumen (mantenemos las claves que usa tu frontend) ---------
    resumen = {
        "recursos_cargados": nuevos_recursos,
        "categorias_cargadas": nuevas_categorias,
        "configuraciones_cargadas": nuevas_configuraciones,
        "clientes_cargados": nuevos_clientes,
        "instancias_cargadas": nuevas_instancias,
        # info extra opcional (por si la quieres mostrar)
        "recursos_actualizados": recursos_actualizados,
        "categorias_actualizadas": categorias_actualizadas,
        "configuraciones_actualizadas": configuraciones_actualizadas,
        "clientes_actualizados": clientes_actualizados,
        "instancias_actualizadas": instancias_actualizadas,
    }

    print("=== RESUMEN FINAL ===")
    for k, v in resumen.items():
        print(f"{k}: {v}")
    print("=====================")

    return jsonify({
        "message": "Archivo procesado correctamente",
        "resumen": resumen
    }), 200

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
    data = request.get_json() or {}
    nombre = data.get("nombre")
    abreviatura = data.get("abreviatura")
    tipo = data.get("tipo")
    metrica = data.get("metrica")
    valor_x_hora = data.get("valor_x_hora")


    #Validar campos obligatorios
    if not nombre or valor_x_hora is None:
        return jsonify({"error": "Los campos 'nombre' ó 'valor_x_hora' son obligatorios."}), 400

    #Validar tipo de dato del costo
    try:
        valor_x_hora = float(valor_x_hora)
        if valor_x_hora <= 0:
            return jsonify({"error": "El costo por hora debe ser mayor que 0."}), 400
    except ValueError:
        return jsonify({"error": "El costo por hora debe ser numérico."}), 400

    #Validar duplicados
    for r in recursos:
        if r["nombre"].lower() == nombre.lower():
            return jsonify({"error": "Ya existe un recurso con ese nombre."}), 400

    #Crear nuevo recurso
    nuevo_recurso = {
        "id": len(recursos) + 1,
        "nombre": nombre,
        "abreviatura": abreviatura,
        "tipo": tipo,
        "metrica": metrica,
        "valor_x_hora": float(valor_x_hora)
    }

    recursos.append(nuevo_recurso)
    guardar_datos(RECURSOS_FILE, recursos)

    return jsonify(nuevo_recurso), 201

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
    guardar_datos(RECURSOS_FILE, recursos)
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

    #Validar campos obligatorios
    if not all([nombre, nit, direccion, correo]):
        return jsonify({"error": "Todos los campos son obligatorios (nombre, NIT, dirección, correo)."}), 400

    #Validar formato de correo simple
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
        return jsonify({"error": "El formato del correo electrónico no es válido."}), 400

    #Validar duplicado por NIT o correo
    for c in clientes:
        if c["nit"] == nit:
            return jsonify({"error": "Ya existe un cliente con ese NIT."}), 400
        if c["correo"].lower() == correo.lower():
            return jsonify({"error": "Ya existe un cliente con ese correo electrónico."}), 400

    #Generar usuario y clave automáticamente
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
    guardar_datos(CLIENTES_FILE, clientes)

    print("Cliente registrado:", nuevo_cliente)
    return jsonify(nuevo_cliente), 201

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    global clientes
    clientes = [c for c in clientes if c["id"] != id]
    guardar_datos(CLIENTES_FILE, clientes)
    return jsonify({"message": "Cliente eliminado"}), 200

#----------------------------------------------ENDPOINTS INSTANCIAS
@app.route('/api/instancias', methods=['GET'])
def obtener_instancias():
    return jsonify(instancias)

@app.route('/api/instancias', methods=['POST'])
def crear_instancia():
    data = request.get_json() or {}

    #Validar campos obligatorios
    if not all([data.get("cliente_id"), data.get("recurso_id"), data.get("horas")]):
        return jsonify({"error": "Los campos 'cliente_id', 'recurso_id' y 'horas' son obligatorios."}), 400

    try:
        cliente_id = int(data["cliente_id"])
        recurso_id = int(data["recurso_id"])
        horas = float(data["horas"])
    except ValueError:
        return jsonify({"error": "Los campos 'cliente_id', 'recurso_id' y 'horas' deben ser numéricos."}), 400

    #Validar existencia de cliente y recurso
    cliente = buscar_por_id(clientes, cliente_id)
    recurso = buscar_por_id(recursos, recurso_id)

    if not cliente:
        return jsonify({"error": f"No existe el cliente con ID {cliente_id}."}), 404
    if not recurso:
        return jsonify({"error": f"No existe el recurso con ID {recurso_id}."}), 404

    #Validar que las horas sean mayores que cero
    if horas <= 0:
        return jsonify({"error": "Las horas deben ser mayores que 0."}), 400

    #Calcular costo total según el recurso
    costo = float(recurso.get("valor_x_hora", 0))
    if costo <= 0:
        return jsonify({"error": "El recurso tiene un costo inválido."}), 400

    nueva = {
        "id": len(instancias) + 1,
        "cliente_id": cliente_id,
        "recurso_id": recurso_id,
        "horas": horas,
        "estado": "Vigente",
        "costo_total": horas * costo
    }

    instancias.append(nueva)
    guardar_datos(INSTANCIAS_FILE, instancias)

    print("Instancia creada:", nueva)
    return jsonify(nueva), 201


@app.route('/api/instancias/<int:id>/cancelar', methods=['PUT'])
def cancelar_instancia(id):
    instancia = buscar_por_id(instancias, id)
    if instancia:
        instancia["estado"] = "Cancelada"
        guardar_datos(INSTANCIAS_FILE, instancias)
        return jsonify(instancia)
    return jsonify({"error": "Instancia no encontrada"}), 404

#----------------------------------------------ENDPOINTS CONSUMOS
@app.route('/api/consumos', methods=['POST'])
def cargar_consumos():
    archivo = request.files.get('archivo')
    if not archivo:
        return jsonify({"error": "No se envió ningún archivo XML"}), 400

    tree = ET.parse(archivo)
    root = tree.getroot()

    instancias = cargar_datos(INSTANCIAS_FILE, [])
    recursos = cargar_datos(RECURSOS_FILE, [])
    nuevos_consumos = []

    print("=== DEBUG INICIO ===")
    print("INSTANCIAS CARGADAS:", instancias)
    print("RECURSOS CARGADOS:", recursos)

    for consumo in root.findall(".//Consumo"):
        id_instancia = int(consumo.find('idInstancia').text)
        horas_uso = float(consumo.find('horasUso').text)
        print(f"Procesando consumo -> Instancia: {id_instancia}, Horas: {horas_uso}")

        encontrada = False
        for instancia in instancias:
            if instancia["id"] == id_instancia:
                encontrada = True
                print(f"✔ Instancia encontrada: {instancia}")

                recurso_id = instancia.get("recurso_id")
                recurso = next((r for r in recursos if r["id"] == recurso_id), None)
                print(f"→ Recurso asociado: {recurso}")

                costo_hora = recurso["valor_x_hora"] if recurso else 0
                instancia["horas"] += horas_uso
                instancia["costo_total"] = round(instancia["horas"] * costo_hora, 2)
                nuevos_consumos.append({
                    "idInstancia": id_instancia,
                    "horasUso": horas_uso,
                    "nuevoTotal": instancia["costo_total"]
                })
                break

        if not encontrada:
            print(f"⚠ No se encontró instancia con ID {id_instancia}")

    print("=== DEBUG FIN ===")
    guardar_datos(INSTANCIAS_FILE, instancias)
    guardar_datos(RECURSOS_FILE, recursos)
    return jsonify({
        "message": f"Se cargaron {len(nuevos_consumos)} consumos",
        "consumos": nuevos_consumos
    })

#----------------------------------------------ENDPOINTS FACTURACIÓN
@app.route('/api/facturar', methods=['POST'])
def generar_facturas():
    clientes = cargar_datos(CLIENTES_FILE, [])
    instancias = cargar_datos(INSTANCIAS_FILE, [])
    recursos = cargar_datos(RECURSOS_FILE, [])
    facturas = []

    for cliente in clientes:
        total_cliente = 0
        detalle = []

        for instancia in instancias:
            if instancia["cliente_id"] == cliente["id"] and instancia["estado"] == "Vigente":
                recurso = next((r for r in recursos if r["id"] == instancia["recurso_id"]), None)
                if recurso:
                    subtotal = instancia["horas"] * recurso["valor_x_hora"]
                    detalle.append({
                        "recurso": recurso["nombre"],
                        "horas": instancia["horas"],
                        "costo_hora": recurso["valor_x_hora"],
                        "subtotal": subtotal
                    })
                    total_cliente += subtotal

        if total_cliente > 0:
            factura = {
                "cliente_id": cliente["id"],
                "cliente": cliente["nombre"],
                "correo": cliente["correo"],
                "total": round(total_cliente, 2),
                "detalle": detalle
            }
            facturas.append(factura)

    guardar_datos(CONSUMOS_FILE.replace("consumos", "facturas"), facturas)
    guardar_facturas_xml(facturas)
    return jsonify({"message": f"Se generaron {len(facturas)} facturas", "facturas": facturas})

def guardar_facturas_xml(facturas):
    root = ET.Element("Facturas")

    for factura in facturas:
        f_elem = ET.SubElement(root, "Factura")
        ET.SubElement(f_elem, "Cliente").text = factura["cliente"]
        ET.SubElement(f_elem, "Correo").text = factura["correo"]
        ET.SubElement(f_elem, "Total").text = str(factura["total"])

        detalle_elem = ET.SubElement(f_elem, "Detalle")
        for item in factura["detalle"]:
            item_elem = ET.SubElement(detalle_elem, "Item")
            ET.SubElement(item_elem, "Recurso").text = item["recurso"]
            ET.SubElement(item_elem, "Horas").text = str(item["horas"])
            ET.SubElement(item_elem, "CostoHora").text = str(item["costo_hora"])
            ET.SubElement(item_elem, "Subtotal").text = str(item["subtotal"])

    tree = ET.ElementTree(root)
    ruta_xml = os.path.join(DATA_DIR, "facturas.xml")
    tree.write(ruta_xml, encoding="utf-8", xml_declaration=True)
    print(f"Facturas exportadas correctamente a {ruta_xml}")

@app.route('/api/facturas', methods=['GET'])
def obtener_facturas():

    facturas = []

    # Recalcular todas las facturas desde instancias vigentes o canceladas
    for instancia in instancias:
        cliente = next((c for c in clientes if c["id"] == instancia["cliente_id"]), None)
        recurso = next((r for r in recursos if r["id"] == instancia["recurso_id"]), None)

        if not cliente or not recurso:
            continue

        if instancia["estado"] in ["Vigente", "Cancelada"]:
            factura_existente = next((f for f in facturas if f["cliente_id"] == cliente["id"]), None)
            detalle = {
                "recurso": recurso["nombre"],
                "costo_hora": float(recurso["valor_x_hora"]),
                "horas": float(instancia["horas"]),
                "subtotal": float(instancia["costo_total"])
            }

            if factura_existente:
                factura_existente["detalle"].append(detalle)
                factura_existente["total"] += float(instancia["costo_total"])
            else:
                facturas.append({
                    "cliente_id": cliente["id"],
                    "cliente": cliente["nombre"],
                    "correo": cliente["correo"],
                    "detalle": [detalle],
                    "total": float(instancia["costo_total"])
                })

    # Guardar las facturas recalculadas
    ruta = os.path.join(DATA_DIR, "facturas.json")
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(facturas, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando facturas.json: {e}")

    print(f"Se generaron {len(facturas)} facturas y se guardaron en facturas.json")

    return jsonify(facturas), 200


#----------------------------------------------GENERACION DE FACTURAS EN PDF
@app.route('/api/facturas/pdf', methods=['GET'])
def descargar_facturas_pdf():
    if not os.path.exists(FACTURAS_FILE):
        return jsonify({"error": "No hay facturas generadas"}), 404

    with open(FACTURAS_FILE, "r", encoding="utf-8") as f:
        facturas = json.load(f)

    #Crear PDF en memoria
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("Facturas - Tecnologías Chapinas S.A.")

    #Encabezado general
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, 750, "Reporte de Facturas - Tecnologías Chapinas S.A.")
    pdf.setFont("Helvetica", 12)
    y = 720

    if not facturas:
        pdf.drawString(200, y, "No existen facturas registradas.")
    else:
        for factura in facturas:
            #Verificar espacio
            if y < 120:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)

            #Datos del cliente
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(50, y, f"Cliente: {factura.get('cliente', 'N/A')}")
            y -= 20
            pdf.setFont("Helvetica", 11)
            pdf.drawString(50, y, f"Correo: {factura.get('correo', 'N/A')}")
            y -= 20
            pdf.drawString(50, y, f"Total: Q{factura.get('total', 0):.2f}")
            y -= 20

            #Encabezado de detalle
            pdf.setFont("Helvetica-Bold", 11)
            pdf.drawString(70, y, "Recurso")
            pdf.drawString(250, y, "Horas")
            pdf.drawString(320, y, "Costo/h")
            pdf.drawString(400, y, "Subtotal")
            y -= 15
            pdf.line(50, y, 550, y)
            y -= 10

            #Detalle
            pdf.setFont("Helvetica", 10)
            for item in factura.get("detalle", []):
                pdf.drawString(70, y, item.get("recurso", ""))
                pdf.drawString(260, y, str(item.get("horas", "")))
                pdf.drawString(330, y, f"Q{item.get('costo_hora', 0):.2f}")
                pdf.drawString(410, y, f"Q{item.get('subtotal', 0):.2f}")
                y -= 15

                #Salto de página si se llena
                if y < 100:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 10)
                    y = 750

            #Separador entre facturas
            y -= 20
            pdf.line(50, y, 550, y)
            y -= 30

    # Guardar PDF
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="facturas.pdf",
        mimetype="application/pdf"
    )

#----------------------------------------------GENERACION DE FACTURAS EN XML
@app.route('/api/facturas/xml', methods=['GET'])
def descargar_facturas_xml():
    ruta = os.path.join(DATA_DIR, "facturas.json")

    if not os.path.exists(ruta):
        return jsonify({"error": "No hay facturas registradas"}), 404

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            facturas = json.load(f)

        # Crear elemento raíz
        root = ET.Element("facturas")

        for factura in facturas:
            factura_elem = ET.SubElement(root, "factura")
            ET.SubElement(factura_elem, "cliente").text = factura["cliente"]
            ET.SubElement(factura_elem, "correo").text = factura["correo"]
            ET.SubElement(factura_elem, "total").text = str(factura["total"])

            detalle_elem = ET.SubElement(factura_elem, "detalle")

            for item in factura.get("detalle", []):
                item_elem = ET.SubElement(detalle_elem, "item")
                ET.SubElement(item_elem, "recurso").text = item["recurso"]
                ET.SubElement(item_elem, "horas").text = str(item["horas"])
                ET.SubElement(item_elem, "costo_hora").text = str(item["costo_hora"])
                ET.SubElement(item_elem, "subtotal").text = str(item["subtotal"])

        #Convertir a XML string
        xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        return Response(xml_str, mimetype="application/xml",
                        headers={"Content-Disposition": "attachment; filename=facturas.xml"})

    except Exception as e:
        return jsonify({"error": f"Error generando XML: {str(e)}"}), 500



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