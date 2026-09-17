# CryptoChat - Network Traffic & Cryptographic Analysis Tool

An educational multi-instance chat application designed to compare **unencrypted** versus **encrypted** (AES-256-GCM, RSA-2048-OAEP, and Hybrid AES+RSA) network communications, using **Wireshark** for packet inspection and traffic analysis.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [System Architecture](#-system-architecture)
4. [Prerequisites & Installation](#-prerequisites--installation)
5. [How to Run the Application](#-how-to-run-the-application)
6. [Cryptographic Mechanisms Explained](#-cryptographic-mechanisms-explained)
7. [Base64 vs. Encryption Clarification](#-base64-vs-encryption-clarification)
8. [Wireshark Traffic Analysis Guide](#-wireshark-traffic-analysis-guide)
9. [Security Considerations](#-security-considerations)

---

## 🌐 Project Overview

Modern network protocols rely heavily on cryptography to guarantee **Confidentiality**, **Integrity**, and **Authenticity**. This project demonstrates the differences in network packet footprints when transmitting data in plaintext versus using symmetric, asymmetric, and hybrid encryption algorithms.

The application includes an integrated **Wireshark View Monitor** inside the GUI, allowing real-time visualization of the exact raw byte string sent over the socket before analyzing it in Wireshark.

---

## ✨ Key Features

* **Multi-Instance TCP Communication:** Allows multiple clients to connect to a central TCP relay server on port `9999`.
* **Four Encryption Modes (Selectable in Real-Time):**
  1. `UNENCRYPTED`: Plaintext JSON transmission.
  2. `AES`: AES-256-GCM authenticated symmetric encryption.
  3. `RSA`: RSA-OAEP 2048-bit asymmetric encryption.
  4. `HYBRID`: Ephemeral AES-256-GCM key encrypted with RSA-OAEP 2048-bit.
* **Automated Bidirectional Handshake:** Public keys are automatically exchanged (`HANDSHAKE_REQ` and `HANDSHAKE_RESP`) upon client connection—no manual key management required.
* **Live Socket Traffic Inspection:** GUI panel showing exact JSON payloads transmitted over the socket.
* **Wireshark Compatibility:** Unencrypted TCP streams easily readable via *Follow TCP Stream*, while encrypted modes show high-entropy Base64 ciphertext.

---

## 🏗️ System Architecture

The codebase is split into three modular components:

```
├── crypto_utils.py   # Cryptographic engine (AES-GCM, RSA-OAEP, Hybrid encryption)
├── server.py         # Multi-threaded TCP relay server (Port 9999)
├── client_gui.py     # Tkinter GUI client with real-time protocol switching
└── README.md         # Project documentation & execution guide
```

```
[ Client A ]  <--->  [ TCP Relay Server:9999 ]  <--->  [ Client B ]
     |                                                      |
     +-------------------- [ Wireshark ] -------------------+
                          (Capture Loopback)
```

---

## 🔧 Prerequisites & Installation

### Requirements

* **Python 3.8+**
* **Wireshark** (Installed natively on Kali Linux or downloaded from [wireshark.org](https://www.wireshark.org/))

### Installation Steps

1. **Clone or download this repository to your machine.**
2. **Install the required Python cryptography library:**

```bash
pip install cryptography
```

*(Note: `tkinter`, `socket`, `json`, `threading`, and `os` are included in the Python standard library).*

---

## 🚀 How to Run the Application

To test multi-user communication and inspect traffic with Wireshark, follow these steps:

### Step 1: Start the Relay Server
Open a terminal and execute:
```bash
python server.py
```
*Expected Output:*
`[*] Servidor de Relay TCP activo en 127.0.0.1:9999`

### Step 2: Start Client 1
Open a second terminal and execute:
```bash
python client_gui.py
```

### Step 3: Start Client 2
Open a third terminal and execute:
```bash
python client_gui.py
```

### Step 4: Automatic Handshake Verification
As soon as Client 2 opens, both clients will perform an automatic key exchange. You will see this message in the chat log:
`Sistema: Conexión segura establecida con el par.`

You can now select any encryption mode from the dropdown menu and exchange messages!

---

## 🔐 Cryptographic Mechanisms Explained

| Mode | Type | Algorithm / Parameters | Key Distribution | Pros / Cons |
| :--- | :--- | :--- | :--- | :--- |
| **UNENCRYPTED** | Plaintext | UTF-8 JSON | None | **Pros:** Zero overhead.<br>**Cons:** Vulnerable to eavesdropping in Wireshark. |
| **AES** | Symmetric | AES-GCM (256-bit), 12-byte random Nonce | Pre-shared key | **Pros:** Extremely fast, provides integrity (AEAD).<br>**Cons:** Requires prior key sharing. |
| **RSA** | Asymmetric | RSA-OAEP (2048-bit), MGF1 SHA-256 | Public Key Exchange | **Pros:** No secret shared beforehand.<br>**Cons:** Slow, payload size strictly limited by key size. |
| **HYBRID** | Combined | RSA-OAEP 2048 + AES-256-GCM | RSA exchanges AES key | **Pros:** Combines speed of AES with security of RSA distribution.<br>**Cons:** Slightly larger header size. |

### How the Hybrid Mode Works
1. The sender generates a **random ephemeral 256-bit AES key** specifically for this single message.
2. The message is encrypted using **AES-GCM** with this ephemeral key and a random 12-byte Nonce.
3. The ephemeral AES key is encrypted using the recipient's **RSA Public Key** via RSA-OAEP.
4. The final payload transmitted over the socket is:
   ```json
   {
     "mode": "HYBRID",
     "payload": {
       "encrypted_key": "<Base64 encoded RSA-encrypted AES key>",
       "nonce": "<Base64 encoded 12-byte Nonce>",
       "ciphertext": "<Base64 encoded AES ciphertext>"
     }
   }
   ```
5. The recipient uses their **RSA Private Key** to decrypt the ephemeral AES key, then uses that key to decrypt the AES ciphertext.

---

## 💡 Base64 vs. Encryption Clarification

> **Important Conceptual Note for Academic Defense:**
> Base64 is **NOT** an encryption algorithm; it is an **encoding format**.

* **Why is Base64 used here?**
  Cryptographic outputs (AES/RSA) are raw, non-printable binary byte sequences. Because our socket protocol transmits JSON strings over TCP, raw binary data would corrupt the JSON parser or socket stream. Base64 translates binary bytes into safe, printable ASCII characters (`A-Z`, `a-z`, `0-9`, `+`, `/`).
* **Summary Difference:**
  * **Encryption (AES/RSA):** Protects confidentiality. Requires a secret/private key to reverse.
  * **Encoding (Base64):** Converts data representation for transport. Requires **no key** and offers **zero security**.

---

## 🔍 Wireshark Traffic Analysis Guide

### Setting Up Wireshark Capture

1. Launch **Wireshark**.
2. Select the loopback interface:
   * **Windows:** `Adapter for loopback traffic capture`
   * **Linux / Kali Linux:** `lo`
3. Apply the display filter in the top bar:
   ```text
   tcp.port == 9999
   ```
4. Press **Enter**.

---

### Step-by-Step Inspection Procedure

#### Scenario A: Unencrypted Communication
1. In `client_gui.py`, select `UNENCRYPTED` from the dropdown.
2. Send a test message: `My password is 123456`.
3. In Wireshark, right-click any captured TCP packet with `Len > 0`.
4. Navigate to **Follow** -> **TCP Stream**.
5. **Observation:** The entire message content is plainly visible in red/blue text:
   `{"mode": "UNENCRYPTED", "payload": "My password is 123456"}`

#### Scenario B: Encrypted Communication (AES / RSA / HYBRID)
1. In `client_gui.py`, select `HYBRID` (or `AES` / `RSA`).
2. Send the exact same message: `My password is 123456`.
3. In Wireshark, right-click the packet and select **Follow** -> **TCP Stream**.
4. **Observation:** The payload is unreadable. An eavesdropper can see that a connection exists between `127.0.0.1` on port `9999`, but the actual message is replaced by high-entropy Base64 ciphertext.

---

## 🛡️ Security Considerations

* **Controlled Environment:** This application was developed strictly for educational and experimental purposes.
* **Fictional Data:** Always use mock passwords or test messages during demonstrations.
* **Network Metadata Exposure:** Note that standard encryption at the application layer hides payload contents, but lower-layer metadata (IP addresses, port numbers, packet timing, and packet sizes) remains visible to observers unless routing anonymizers (e.g., Tor or VPNs) are used.