from flask import Flask, request, jsonify, render_template
import re
import sqlite3
import time

app = Flask(__name__)

# Función para validar y reconocer datos peligrosos
def validar_direccion(direccion):
    # Patrón que busca caracteres peligrosos: comillas, punto y coma, doble guion, palabras clave SQL
    patron_peligroso = re.compile(r"[';]|(--)|(DROP|INSERT|DELETE|UPDATE|ALTER)", re.IGNORECASE)
    
    if patron_peligroso.search(direccion):
        return False, "La dirección contiene caracteres o palabras clave peligrosas."
    return True, "Dirección segura."

# Simulación de una API externa comprometida
def api_externa_comprometida(direccion_usuario):
    # Simulación de respuesta lenta para provocar un ataque de DoS
    if direccion_usuario == "1010 Calle Lenta":
        time.sleep(10)  # Retardar la respuesta por 10 segundos
        return "Demora intencionada por la API comprometida"
    
    # Simulación de código malicioso inyectado
    if direccion_usuario == "999 Calle Hack":
        return "<script>alert('API Comprometida');</script>"
    
    # Simulación de exposición de datos sensibles
    if direccion_usuario == "789 Calle Privada":
        return "Número de tarjeta de crédito: 1234-5678-9101-1121"
    
    # Simulación de redireccionamiento malicioso
    if direccion_usuario == "456 Calle Falsa":
        return "http://malicioso.com/redireccion"  # URL comprometida
    
    # Simulación de SQL Injection malicioso
    if direccion_usuario == "123 Calle Principal":
        return "123 Calle Principal'; DROP TABLE direcciones; --"
    
    # Devolver la dirección original si no es un caso de ataque
    return direccion_usuario

# Función para conectar o crear la base de datos
def conectar_db():
    try:
        conn = sqlite3.connect('direcciones.db')
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Error al conectar a la base de datos: {e}")

# Endpoint para procesar la solicitud de dirección con validación
@app.route('/procesar_direccion', methods=['POST'])
def procesar_direccion():
    direccion_usuario = request.form['direccion']
    direccion_comprometida = api_externa_comprometida(direccion_usuario)

    # Validar la dirección antes de almacenarla
    valida, mensaje = validar_direccion(direccion_comprometida)
    if not valida:
        print(f"Validación fallida para la dirección: {direccion_usuario}. Motivo: {mensaje}")
        return jsonify({'resultado': mensaje}), 400

    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Crear tabla si no existe
        cursor.execute('''CREATE TABLE IF NOT EXISTS direcciones (id INTEGER PRIMARY KEY, direccion TEXT)''')

        # Almacenar la dirección usando parámetros preparados
        cursor.execute("INSERT INTO direcciones (direccion) VALUES (?)", (direccion_comprometida,))
        conn.commit()
        resultado = "Dirección almacenada correctamente."
        print(f"Dirección almacenada: {direccion_usuario}")
    except sqlite3.Error as e:
        print(f"Error al intentar guardar la dirección en la base de datos: {e}")
        return jsonify({'resultado': f"Error en la base de datos: {e}"}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'resultado': resultado}), 200

# Endpoint para listar todas las direcciones almacenadas@app.route('/listar_direcciones')@app.route('/listar_direcciones')
@app.route('/listar_direcciones')
def listar_direcciones():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        # Consultar todas las direcciones almacenadas
        cursor.execute("SELECT * FROM direcciones")
        direcciones = cursor.fetchall()  # Obtener todas las direcciones
        print(direcciones)  # <-- Añadir esto para ver qué datos están siendo recuperados
    except sqlite3.Error as e:
        print(f"Error al intentar leer la base de datos: {e}")
        return jsonify({'resultado': f"Error al leer la base de datos: {e}"}), 500
    finally:
        if conn:
            conn.close()

    # Renderizar la plantilla HTML con los datos
    return render_template('listar.html', direcciones=direcciones)


# Endpoint para eliminar todas las direcciones almacenadas
@app.route('/eliminar_direcciones', methods=['POST'])
def eliminar_direcciones():
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM direcciones")
        conn.commit()
        resultado = "Todas las direcciones han sido eliminadas."
        print("Direcciones eliminadas")
    except sqlite3.Error as e:
        print(f"Error al eliminar las direcciones: {e}")
        return jsonify({'resultado': f"Error al eliminar las direcciones: {e}"}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'resultado': resultado}), 200

# Endpoint para eliminar una dirección específica
@app.route('/eliminar_direccion/<int:id>', methods=['POST'])
def eliminar_direccion(id):
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM direcciones WHERE id = ?", (id,))
        conn.commit()
        resultado = f"La dirección con ID {id} ha sido eliminada."
        print(f"Dirección con ID {id} eliminada")
    except sqlite3.Error as e:
        print(f"Error al eliminar la dirección con ID {id}: {e}")
        return jsonify({'resultado': f"Error al eliminar la dirección con ID {id}: {e}"}), 500
    finally:
        if conn:
            conn.close()

    return jsonify({'resultado': resultado}), 200

# Página principal para la demo
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
