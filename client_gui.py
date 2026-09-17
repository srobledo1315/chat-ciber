import socket
import json
import threading
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from crypto_utils import CryptoEngine

class ChatClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CryptoChat | Traffic & Cryptography Inspector")
        self.root.geometry("880x720")
        self.root.minsize(780, 600)
        self.root.configure(bg="#0d1117")

        self.crypto = CryptoEngine()
        self.peer_public_key = None
        self.packet_count = 0
        self.last_payload_raw = ""

        # Configuración del Sistema de Estilos Dark Cyber
        self.setup_styles()
        self.setup_ui()
        self.connect_to_server()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Paleta de Colores Cyber/Dark
        self.colors = {
            "bg": "#0d1117",
            "card_bg": "#161b22",
            "border": "#30363d",
            "text": "#c9d1d9",
            "muted": "#8b949e",
            "accent_cyan": "#58a6ff",
            "accent_green": "#3fb950",
            "accent_purple": "#bc8cff",
            "accent_orange": "#d29922",
            "warning_red": "#f85149",
            "terminal_bg": "#080c14"
        }

        # Estilos TTK
        self.style.configure(".", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 9))
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("Card.TFrame", background=self.colors["card_bg"], relief="flat", borderwidth=1)
        
        self.style.configure("Header.TLabel", background=self.colors["bg"], foreground=self.colors["accent_cyan"], font=("Segoe UI", 13, "bold"))
        self.style.configure("SubHeader.TLabel", background=self.colors["bg"], foreground=self.colors["muted"], font=("Segoe UI", 8))
        self.style.configure("Card.TLabel", background=self.colors["card_bg"], foreground=self.colors["text"], font=("Segoe UI", 9))
        self.style.configure("Badge.TLabel", background=self.colors["card_bg"], foreground=self.colors["accent_green"], font=("Segoe UI", 8, "bold"))
        
        # Botones
        self.style.configure("Cyber.TButton", background="#238636", foreground="#ffffff", borderwidth=0, font=("Segoe UI", 9, "bold"), padding=6)
        self.style.map("Cyber.TButton", background=[("active", "#2ea043"), ("disabled", "#21262d")])

        self.style.configure("Action.TButton", background="#21262d", foreground=self.colors["text"], borderwidth=1, relief="solid", padding=3)
        self.style.map("Action.TButton", background=[("active", "#30363d")])

        # OptionMenu / Combobox
        self.style.configure("TMenubutton", background=self.colors["card_bg"], foreground=self.colors["accent_cyan"], borderwidth=1, relief="solid", padding=5, font=("Segoe UI", 9, "bold"))

    def setup_ui(self):
        # Contenedor Principal
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------------
        # 1. HEADER & PANEL DE ESTADO
        # -------------------------------------------------------------------
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_box = ttk.Frame(header_frame)
        title_box.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(title_box, text="🛡️ CryptoChat Inspector", style="Header.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Analizador de Tráfico de Red & Criptografía (Wireshark Suite)", style="SubHeader.TLabel").pack(anchor="w")

        # Badges de Estado
        status_box = ttk.Frame(header_frame)
        status_box.pack(side=tk.RIGHT, fill=tk.Y)

        self.server_status_lbl = tk.Label(
            status_box, text="🔴 Servidor: Desconectado", bg="#21262d", fg=self.colors["warning_red"],
            font=("Segoe UI", 8, "bold"), padx=8, pady=3
        )
        self.server_status_lbl.pack(side=tk.RIGHT, padx=4)

        self.peer_status_lbl = tk.Label(
            status_box, text="⏳ Esperando Par RSA", bg="#21262d", fg=self.colors["accent_orange"],
            font=("Segoe UI", 8, "bold"), padx=8, pady=3
        )
        self.peer_status_lbl.pack(side=tk.RIGHT, padx=4)

        # -------------------------------------------------------------------
        # 2. SELECTOR DE MODO DE CIFRADO Y BANNER INFORMATIVO
        # -------------------------------------------------------------------
        mode_card = ttk.Frame(main_container, style="Card.TFrame", padding=8)
        mode_card.pack(fill=tk.X, pady=(0, 10))

        mode_top = ttk.Frame(mode_card, style="Card.TFrame")
        mode_top.pack(fill=tk.X)

        ttk.Label(mode_top, text="Algoritmo de Transmisión:", style="Card.TLabel", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        self.mode_var = tk.StringVar(value="UNENCRYPTED")
        modes = ["UNENCRYPTED", "AES", "RSA", "HYBRID"]
        
        self.mode_selector = ttk.OptionMenu(
            mode_top, self.mode_var, modes[0], *modes, command=self.on_mode_changed
        )
        self.mode_selector.pack(side=tk.LEFT)

        # Banner Explicativo Criptográfico
        self.info_banner = tk.Label(
            mode_card, text="", bg="#1f1b24", fg="#f0883e",
            font=("Segoe UI", 8, "italic"), anchor="w", justify=tk.LEFT, padx=8, pady=4, wraplength=820
        )
        self.info_banner.pack(fill=tk.X, pady=(6, 0))
        self.update_mode_banner("UNENCRYPTED")

        # -------------------------------------------------------------------
        # 3. SECCIÓN SUPERIOR: CHAT LOG (HISTORIAL)
        # -------------------------------------------------------------------
        chat_frame = ttk.Frame(main_container, style="Card.TFrame", padding=6)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(chat_frame, text="💬 HISTORIAL DE MENSAJES", style="Card.TLabel", font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, height=10, bg="#11151c", fg=self.colors["text"],
            insertbackground=self.colors["text"], relief="flat", font=("Segoe UI", 9)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.setup_chat_tags()

        # -------------------------------------------------------------------
        # 4. SECCIÓN INFERIOR: MONITOR DE SOCKET (WIRESHARK VIEW)
        # -------------------------------------------------------------------
        net_frame = ttk.Frame(main_container, style="Card.TFrame", padding=6)
        net_frame.pack(fill=tk.X, pady=(0, 10))

        net_header = ttk.Frame(net_frame, style="Card.TFrame")
        net_header.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(net_header, text="📡 INSPECTOR DE SOCKET (Wireshark Raw Payload)", style="Card.TLabel", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT)
        
        self.metrics_lbl = ttk.Label(net_header, text="Paquetes: 0 | Último: 0 B", style="Card.TLabel", font=("Segoe UI", 8))
        self.metrics_lbl.pack(side=tk.LEFT, padx=15)

        copy_btn = ttk.Button(net_header, text="📋 Copiar Payload", style="Action.TButton", command=self.copy_last_payload)
        copy_btn.pack(side=tk.RIGHT, padx=2)

        clear_btn = ttk.Button(net_header, text="🗑️ Limpiar Log", style="Action.TButton", command=self.clear_network_log)
        clear_btn.pack(side=tk.RIGHT, padx=2)

        self.network_display = scrolledtext.ScrolledText(
            net_frame, height=6, bg=self.colors["terminal_bg"], fg="#39c5bb",
            insertbackground="#39c5bb", relief="flat", font=("Consolas", 8)
        )
        self.network_display.pack(fill=tk.X)
        self.setup_network_tags()

        # -------------------------------------------------------------------
        # 5. BARRA DE ENTRADA Y ENVÍO
        # -------------------------------------------------------------------
        input_frame = ttk.Frame(main_container)
        input_frame.pack(fill=tk.X)

        self.msg_entry = tk.Entry(
            input_frame, bg="#161b22", fg=self.colors["text"],
            insertbackground=self.colors["text"], relief="solid", bd=1,
            font=("Segoe UI", 10)
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=5)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = ttk.Button(input_frame, text="ENVIAR 🚀", style="Cyber.TButton", command=self.send_message)
        self.send_btn.pack(side=tk.RIGHT, ipadx=10, ipady=2)

    def setup_chat_tags(self):
        self.chat_display.tag_config("time", foreground=self.colors["muted"], font=("Segoe UI", 8))
        self.chat_display.tag_config("sender_me", foreground=self.colors["accent_cyan"], font=("Segoe UI", 9, "bold"))
        self.chat_display.tag_config("sender_peer", foreground=self.colors["accent_green"], font=("Segoe UI", 9, "bold"))
        self.chat_display.tag_config("sender_sys", foreground=self.colors["accent_purple"], font=("Segoe UI", 9, "bold"))
        
        self.chat_display.tag_config("tag_UNENCRYPTED", background="#3d1518", foreground="#f85149", font=("Segoe UI", 7, "bold"))
        self.chat_display.tag_config("tag_AES", background="#123820", foreground="#56d364", font=("Segoe UI", 7, "bold"))
        self.chat_display.tag_config("tag_RSA", background="#152b48", foreground="#79c0ff", font=("Segoe UI", 7, "bold"))
        self.chat_display.tag_config("tag_HYBRID", background="#2c174d", foreground="#d2a8ff", font=("Segoe UI", 7, "bold"))

    def setup_network_tags(self):
        self.network_display.tag_config("tx", foreground="#58a6ff")
        self.network_display.tag_config("rx", foreground="#3fb950")
        self.network_display.tag_config("mode_unencrypted", foreground="#f85149")
        self.network_display.tag_config("mode_encrypted", foreground="#bc8cff")

    def on_mode_changed(self, selected_mode):
        self.update_mode_banner(selected_mode)

    def update_mode_banner(self, mode):
        descriptions = {
            "UNENCRYPTED": (
                "⚠️ ALERTA DE SEGURIDAD (Texto Plano): El mensaje se enviará codificado en JSON normal sin ningún cifrado. "
                "Cualquier observador con Wireshark capturando la interfaz de red podrá ver el texto exacto del mensaje.",
                "#3d1518", "#f85149"
            ),
            "AES": (
                "🔐 CIFRADO SIMÉTRICO (AES-256-GCM): El mensaje se cifra con una clave secreta simétrica. "
                "Proporciona alta velocidad y autenticidad (AEAD). En Wireshark solo se observará un ciphertext en Base64.",
                "#16271c", "#56d364"
            ),
            "RSA": (
                "🔑 CIFRADO ASIMÉTRICO (RSA-2048-OAEP): El mensaje se cifra usando la Clave Pública del destinatario. "
                "No requiere compartir una clave secreta previa, pero la longitud del mensaje está limitada por el tamaño de la clave RSA.",
                "#122033", "#79c0ff"
            ),
            "HYBRID": (
                "🛡️ CIFRADO HÍBRIDO (Recomendado): Combina la velocidad de AES con la distribución segura de RSA. "
                "Se genera una clave AES efímera por mensaje, la cual se cifra con la Clave Pública RSA del par receptor.",
                "#231438", "#d2a8ff"
            )
        }
        text, bg, fg = descriptions.get(mode, ("", "#161b22", "#c9d1d9"))
        self.info_banner.config(text=text, bg=bg, fg=fg)

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(('127.0.0.1', 9999))
            
            # Actualizar Estado Servidor
            self.server_status_lbl.config(text="🟢 Servidor: 127.0.0.1:9999", fg=self.colors["accent_green"])

            # Iniciar escucha asíncrona
            threading.Thread(target=self.receive_loop, daemon=True).start()

            # Enviar solicitud de handshake inicial
            req = {
                "type": "HANDSHAKE_REQ",
                "pub_key": self.crypto.get_public_key_pem()
            }
            raw_req = json.dumps(req)
            self.sock.sendall(raw_req.encode('utf-8') + b'\n')
            self.log_network("[HANDSHAKE_REQ] Enviando clave pública RSA al servidor...", is_tx=True, mode="SYSTEM")

        except Exception as e:
            self.server_status_lbl.config(text="🔴 Servidor: Error de Conexión", fg=self.colors["warning_red"])
            self.log_chat("Sistema", f"Error al conectar con 127.0.0.1:9999 - {e}", mode="SYSTEM")

    def send_message(self):
        text = self.msg_entry.get().strip()
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
                messagebox.showwarning("Handshake Requerido", "Se requiere otro cliente conectado para cifrar con RSA.")
                self.log_chat("Sistema", "Error: Se requiere otro cliente conectado para cifrar con RSA.", mode="SYSTEM")
                return
            packet["payload"] = self.crypto.encrypt_rsa(text, self.peer_public_key)
        elif mode == "HYBRID":
            if not self.peer_public_key:
                messagebox.showwarning("Handshake Requerido", "Se requiere otro cliente conectado para cifrar en modo Híbrido.")
                self.log_chat("Sistema", "Error: Se requiere otro cliente conectado para cifrar en modo Híbrido.", mode="SYSTEM")
                return
            packet["payload"] = self.crypto.encrypt_hybrid(text, self.peer_public_key)

        raw_json = json.dumps(packet)
        try:
            self.sock.sendall(raw_json.encode('utf-8') + b'\n')
            self.log_chat("Yo", text, mode=mode)
            self.log_network(raw_json, is_tx=True, mode=mode)
            self.msg_entry.delete(0, tk.END)
        except Exception as e:
            self.log_chat("Sistema", f"Error al enviar mensaje: {e}", mode="SYSTEM")

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
                        self.process_incoming(json.loads(line), line)
            except:
                break

    def process_incoming(self, packet, raw_line):
        msg_type = packet.get("type")

        # 1. Petición de Handshake de un nuevo cliente
        if msg_type == "HANDSHAKE_REQ":
            self.peer_public_key = CryptoEngine.load_public_key_pem(packet["pub_key"])
            self.peer_status_lbl.config(text="🔑 Par: Clave RSA Recibida", fg=self.colors["accent_green"])
            self.log_chat("Sistema", "Clave pública RSA del par recibida automáticamente.", mode="SYSTEM")
            self.log_network(f"[HANDSHAKE_REQ RECIBIDO] Clave RSA agregada", is_tx=False, mode="SYSTEM")

            # Responder con nuestra clave pública al cliente entrante
            resp = {
                "type": "HANDSHAKE_RESP",
                "pub_key": self.crypto.get_public_key_pem()
            }
            self.sock.sendall(json.dumps(resp).encode('utf-8') + b'\n')
            return

        # 2. Respuesta de Handshake recibida
        elif msg_type == "HANDSHAKE_RESP":
            self.peer_public_key = CryptoEngine.load_public_key_pem(packet["pub_key"])
            self.peer_status_lbl.config(text="🔑 Par: Conexión Segura OK", fg=self.colors["accent_green"])
            self.log_chat("Sistema", "Conexión segura y clave RSA establecida con el par.", mode="SYSTEM")
            self.log_network(f"[HANDSHAKE_RESP RECIBIDO] Handshake completado exitosamente", is_tx=False, mode="SYSTEM")
            return

        # 3. Mensajes de chat
        mode = packet.get("mode", "UNENCRYPTED")
        payload = packet.get("payload")
        self.log_network(raw_line, is_tx=False, mode=mode)

        try:
            if mode == "UNENCRYPTED":
                text = payload
            elif mode == "AES":
                text = self.crypto.decrypt_aes(payload)
            elif mode == "RSA":
                text = self.crypto.decrypt_rsa(payload)
            elif mode == "HYBRID":
                text = self.crypto.decrypt_hybrid(payload)
            self.log_chat("Par", text, mode=mode)
        except Exception as e:
            self.log_chat("Sistema", f"Error al descifrar mensaje ({mode}): {str(e)}", mode="SYSTEM")

    def log_chat(self, sender, msg, mode=None):
        self.chat_display.config(state='normal')
        
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{now}] ", "time")

        if sender == "Yo":
            self.chat_display.insert(tk.END, "Yo: ", "sender_me")
        elif sender == "Par":
            self.chat_display.insert(tk.END, "Par: ", "sender_peer")
        else:
            self.chat_display.insert(tk.END, "Sistema: ", "sender_sys")

        self.chat_display.insert(tk.END, f"{msg} ")

        if mode and mode != "SYSTEM":
            self.chat_display.insert(tk.END, f" [{mode}] \n", f"tag_{mode}")
        else:
            self.chat_display.insert(tk.END, "\n")

        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def log_network(self, raw_data, is_tx=True, mode="UNENCRYPTED"):
        self.packet_count += 1
        byte_len = len(raw_data.encode('utf-8'))
        self.last_payload_raw = raw_data
        
        self.metrics_lbl.config(text=f"Paquetes: {self.packet_count} | Último: {byte_len} B")

        self.network_display.config(state='normal')
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        direction = "[ENVIADO -> 9999]" if is_tx else "[RECIBIDO <- 9999]"
        tag_dir = "tx" if is_tx else "rx"

        self.network_display.insert(tk.END, f"[{now}] {direction} ", tag_dir)

        # Formatear el JSON para que sea ultra legible si es un JSON válido
        try:
            parsed = json.loads(raw_data)
            pretty_json = json.dumps(parsed, indent=2)
            mode_tag = "mode_unencrypted" if mode == "UNENCRYPTED" else "mode_encrypted"
            self.network_display.insert(tk.END, f"[{mode}]\n{pretty_json}\n\n", mode_tag)
        except:
            self.network_display.insert(tk.END, f"{raw_data}\n\n")

        self.network_display.config(state='disabled')
        self.network_display.see(tk.END)

    def copy_last_payload(self):
        if self.last_payload_raw:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_payload_raw)
            messagebox.showinfo("Copiado", "Payload JSON copiado al portapapeles. Listo para comparar con Wireshark.")
        else:
            messagebox.showwarning("Vacío", "Aún no hay payloads transmitidos para copiar.")

    def clear_network_log(self):
        self.network_display.config(state='normal')
        self.network_display.delete('1.0', tk.END)
        self.network_display.config(state='disabled')
        self.packet_count = 0
        self.metrics_lbl.config(text="Paquetes: 0 | Último: 0 B")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientGUI(root)
    root.mainloop()