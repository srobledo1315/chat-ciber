import socket
import threading

HOST = '127.0.0.1'
PORT = 9999

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message + b'\n')
            except:
                clients.remove(client)

def handle_client(client_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            broadcast(data, client_socket)
        except:
            break
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[*] Servidor de Relay TCP activo en {HOST}:{PORT}")

    while True:
        client_sock, addr = server.accept()
        clients.append(client_sock)
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    main()