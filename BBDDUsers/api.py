
from flask import Flask, request, jsonify
import psycopg

app = Flask(__name__)

DATABASE = {
    'dbname': 'users',       # Nombre de la base de datos
    'user': 'admin',         # usuario de Postgres
    'password': 'yahel',     # contraseña de Postgres
    'host': 'localhost',     # host.
    'port': 5432             # Puerto
}

def get_db_connection():
    return psycopg.connect(**DATABASE)

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM usuarios;')
        usuarios = cursor.fetchall()
    conn.close()
    usuarios_list = []
    for usuario in usuarios:
        usuarios_list.append({
            'id': usuario[0],
            'nombre': usuario[1],
            'apellido': usuario[2],
            'dni': usuario[3],
            'email': usuario[4],
            'fecha_nacimiento': usuario[5],
            'fecha_creacion': usuario[6],
            'activo': usuario[7]
        })
    return jsonify(usuarios_list)

@app.route('/usuario/<int:id>', methods=['GET'])
def get_usuario(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('SELECT * FROM usuarios WHERE id = %s;', (id,))
        usuario = cursor.fetchone()
    conn.close()
    if usuario:
        usuario_dict = {
            'id': usuario[0],
            'nombre': usuario[1],
            'apellido': usuario[2],
            'dni': usuario[3],
            'email': usuario[4],
            'fecha_nacimiento': usuario[5],
            'fecha_creacion': usuario[6],
            'activo': usuario[7]
        }
        return jsonify(usuario_dict)
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/usuario', methods=['POST'])
def create_usuario():
    new_usuario = request.json
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('''
            INSERT INTO usuarios (nombre, apellido, dni, email, fecha_nacimiento)
            VALUES (%s, %s, %s, %s, %s) RETURNING id;
        ''', (new_usuario['nombre'], new_usuario['apellido'], new_usuario['dni'], new_usuario['email'], new_usuario['fecha_nacimiento']))
        new_id = cursor.fetchone()[0]
        conn.commit()
    conn.close()
    return jsonify({'id': new_id}), 201

@app.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM usuarios WHERE id = %s RETURNING id;', (id,))
        deleted_id = cursor.fetchone()
        conn.commit()
    conn.close()
    if deleted_id:
        return jsonify({'message': f'Usuario con id {id} eliminado'}), 200
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    update_data = request.json
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute('''
            UPDATE usuarios
            SET nombre = %s,
                apellido = %s,
                dni = %s,
                email = %s,
                fecha_nacimiento = %s
            WHERE id = %s RETURNING id;
        ''', (update_data['nombre'], update_data['apellido'], update_data['dni'], update_data['email'], update_data['fecha_nacimiento'], id))
        updated_id = cursor.fetchone()
        conn.commit()
    conn.close()
    if updated_id:
        return jsonify({ 'update' : f'Usuario con id {id} actualizado'}), 200
    else:
        return jsonify({ 'error' : 'Usuario no encontrado'}), 404

if __name__ == '__main__':
    app.run(debug=True)
