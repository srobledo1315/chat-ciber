import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
from crypto_utils import CryptoEngine

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoChat - Analizador de Tráfico")
        self.crypto = CryptoEngine()
        self.peer_public_key = None

        self.setup_ui()
        self.connect_to_server()

    def setup_ui(self):
        # Selección de Modo
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(top_frame, text="Modo de Cifrado:").pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value="UNENCRYPTED")
        modes = ["UNENCRYPTED", "AES", "RSA", "HYBRID"]
        self.mode_selector = ttk.OptionMenu(top_frame, self.mode_var, modes[0], *modes)
        self.mode_selector.pack(side=tk.LEFT, padx=5)

        # Historial de Chat
        self.chat_display = scrolledtext.ScrolledText(self.root, height=15, state='disabled')
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Monitor de datos transmitidos en la red (Carga Cruda)
        ttk.Label(self.root, text="Payload transmitido al socket (Wireshark View):", font=('bold', 9)).pack(anchor='w', padx=5)
        self.network_display = scrolledtext.ScrolledText(self.root, height=6, bg='#1e1e1e', fg='#00ff00')
        self.network_display.pack(fill=tk.X, padx=5, pady=5)

        # Entrada de mensaje
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        self.msg_entry = ttk.Entry(bottom_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.send_btn = ttk.Button(bottom_frame, text="Enviar", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, padx=5)

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 9999))
            
            # Iniciar escucha en segundo plano
            threading.Thread(target=self.receive_loop, daemon=True).start()

            # Enviar solicitud de handshake inicial para anunciar presencia y pedir la clave del par
            req = {
                "type": "HANDSHAKE_REQ",
                "pub_key": self.crypto.get_public_key_pem()
            }
            self.sock.sendall(json.dumps(req).encode('utf-8') + b'\n')
        except Exception as e:
            self.log_chat("Sistema", f"Error de conexión con el servidor: {e}")

    def send_message(self):
        text = self.msg_entry.get()
        if not text:
            return

        mode = self.mode_var.get()
        packet = {"mode": mode, "payload": None}

        if mode == "UNENCRYPTED":
            packet["payload"] = text
        elif mode == "AES":
            packet["payload"] = self.crypto.encrypt_aes(text)
        elif mode == "RSA":
            if not self.peer_public_key:
                self.log_chat("Sistema", "Error: Se requiere otro cliente conectado para cifrar con RSA.")
                return
            packet["payload"] = self.crypto.encrypt_rsa(text, self.peer_public_key)
        elif mode == "HYBRID":
            if not self.peer_public_key:
                self.log_chat("Sistema", "Error: Se requiere otro cliente conectado para cifrar en modo Híbrido.")
                return
            packet["payload"] = self.crypto.encrypt_hybrid(text, self.peer_public_key)

        raw_json = json.dumps(packet)
        self.sock.sendall(raw_json.encode('utf-8') + b'\n')
        
        self.log_chat("Yo", text)
        self.log_network(f"[ENVIADO - {mode}] {raw_json}")
        self.msg_entry.delete(0, tk.END)

    def receive_loop(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        self.process_incoming(json.loads(line))
            except:
                break

    def process_incoming(self, packet):
        msg_type = packet.get("type")

        # 1. Petición de Handshake de un nuevo cliente
        if msg_type == "HANDSHAKE_REQ":
            self.peer_public_key = CryptoEngine.load_public_key_pem(packet["pub_key"])
            self.log_chat("Sistema", "Clave pública del par recibida automáticamente.")
            
            # Responder con nuestra propia clave pública al cliente entrante
            resp = {
                "type": "HANDSHAKE_RESP",
                "pub_key": self.crypto.get_public_key_pem()
            }
            self.sock.sendall(json.dumps(resp).encode('utf-8') + b'\n')
            return

        # 2. Respuesta de Handshake recibida
        elif msg_type == "HANDSHAKE_RESP":
            self.peer_public_key = CryptoEngine.load_public_key_pem(packet["pub_key"])
            self.log_chat("Sistema", "Conexión segura establecida con el par.")
            return

        # 3. Procesamiento de mensajes de chat
        mode = packet["mode"]
        payload = packet["payload"]
        self.log_network(f"[RECIBIDO - {mode}] {json.dumps(packet)}")

        try:
            if mode == "UNENCRYPTED":
                text = payload
            elif mode == "AES":
                text = self.crypto.decrypt_aes(payload)
            elif mode == "RSA":
                text = self.crypto.decrypt_rsa(payload)
            elif mode == "HYBRID":
                text = self.crypto.decrypt_hybrid(payload)
            self.log_chat("Par", text)
        except Exception as e:
            self.log_chat("Sistema", f"Error al descifrar mensaje ({mode}): {str(e)}")

    def log_chat(self, sender, msg):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}: {msg}\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def log_network(self, data):
        self.network_display.insert(tk.END, data + "\n")
        self.network_display.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()