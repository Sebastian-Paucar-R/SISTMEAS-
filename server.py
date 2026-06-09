import socket
import threading
import mysql.connector
from pymongo import MongoClient
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5000
clientes = []

db_mysql = mysql.connector.connect(
    host='localhost', user='root', password='1234', database='chat_db'
)
cursor = db_mysql.cursor()

mongo_client = MongoClient('mongodb://localhost:27017/')
db_mongo = mongo_client['chat_db']

def crear_usuario_si_no_existe(nombre):
    cursor.execute('SELECT id FROM usuarios WHERE nombre = %s', (nombre,))
    usuario = cursor.fetchone()
    if not usuario:
        cursor.execute('INSERT INTO usuarios (nombre, email) VALUES (%s, %s)',
                       (nombre, f'{nombre}@email.com'))
        db_mysql.commit()
    if not db_mongo.usuarios.find_one({'nombre': nombre}):
        db_mongo.usuarios.insert_one({
            'nombre': nombre,
            'email': f'{nombre}@email.com',
            'mensajes': []
        })

def guardar_mensaje(nombre, contenido):
    cursor.execute('SELECT id FROM usuarios WHERE nombre = %s', (nombre,))
    usuario = cursor.fetchone()
    if usuario:
        cursor.execute('INSERT INTO mensajes (id_usuario, contenido) VALUES (%s, %s)',
                       (usuario[0], f'{nombre}: {contenido}'))
        db_mysql.commit()
    db_mongo.usuarios.update_one(
        {'nombre': nombre},
        {'$push': {'mensajes': {'contenido': contenido, 'fecha': datetime.now()}}}
    )

def manejar_cliente(conn, addr):
    print(f'Nuevo cliente conectado: {addr}')
    nombre = conn.recv(1024).decode()
    crear_usuario_si_no_existe(nombre)
    clientes.append((conn, nombre))
    while True:
        try:
            data = conn.recv(1024).decode()
            if not data or data == 'salir':
                break
            mensaje = f'{nombre}: {data}'
            guardar_mensaje(nombre, data)
            print(f'({addr}): {mensaje}')
            for c, n in clientes:
                if c != conn:
                    c.sendall(mensaje.encode())
        except:
            break
    clientes.remove((conn, nombre))
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print('Servidor multiusuario escuchando...')
while True:
    conn, addr = server.accept()
    t = threading.Thread(target=manejar_cliente, args=(conn, addr))
    t.daemon = True
    t.start()