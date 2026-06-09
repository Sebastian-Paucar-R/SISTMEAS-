import socket
import threading

HOST = 'localhost'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
nombre = input('Ingresa tu nombre: ')
client.sendall(nombre.encode())

def recibir():
    while True:
        try:
            data = client.recv(1024).decode()
            if data:
                print(data)
        except:
            break

t = threading.Thread(target=recibir, daemon=True)
t.start()

print('Conectado al servidor. Escribe mensajes (escribe salir para terminar)')
while True:
    mensaje = input('Tu: ')
    client.sendall(mensaje.encode())
    if mensaje == 'salir':
        break

client.close()