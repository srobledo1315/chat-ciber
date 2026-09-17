# CryptoChat: Functional Presentation Script

**Target Duration:** ~15 minutes
**Language:** English
**Format:** A structured presentation where all 4 team members introduce themselves and present specific parts of the project's code logic. At the end, there is a live demonstration using Wireshark to prove the network capture.

---

## 1. Melo: Introduction and Server Architecture
**(Estimated Time: 3 - 4 minutes)**

**Melo:** "Hello everyone, my name is Melo, and along with Robledo, Angela, and Karold, we are going to present our project: CryptoChat. CryptoChat is an educational network traffic and cryptography analyzer. Our goal with this project is to demonstrate exactly how different encryption algorithms protect data—or fail to protect it—at the network level. 

To achieve this, we divided our code into three main Python files: a Graphical User Interface for the clients (`client_gui.py`), a cryptographic engine (`crypto_utils.py`), and a central relay server (`server.py`).

I will start by explaining the server. The architecture is a classic client-server model, but we designed our server to be a simple 'blind' TCP relay. Operating on port 9999, the server accepts incoming connections from multiple clients. Whenever a client sends a message, the server reads the data and uses a `broadcast` function to forward that exact byte stream to every other connected socket. The server does not inspect, parse, or decrypt the data; it simply routes it. This design accurately simulates an untrusted public network or ISP, where the data transport layer is insecure by default. If we want privacy, the clients themselves must handle the encryption before the data ever reaches the socket."

---

## 2. Robledo: The Handshake and Unencrypted Mode
**(Estimated Time: 3 - 4 minutes)**

**Robledo:** "Thank you, Melo. I'm Robledo, and I will explain how our clients establish a connection and how our baseline communication works. 

When you launch our `client_gui.py`, it initializes an instance of our `CryptoEngine`. The very first thing the engine does is generate a unique 2048-bit RSA key pair. Once the client connects to the server, it automatically triggers a handshake. It constructs a JSON packet called `HANDSHAKE_REQ` containing its newly generated RSA Public Key in PEM format, and sends it to the server. When another client receives this request, it automatically replies with a `HANDSHAKE_RESP` containing its own public key. This process happens entirely in the background within milliseconds, securely distributing the public keys necessary for our asymmetric encryption modes.

Now, let's talk about the first of our four transmission modes: 'Unencrypted'. This is our baseline to demonstrate network vulnerability. When the user selects this mode, the client takes the plain text message from the input box, wraps it in a standard JSON format with the mode labeled as 'UNENCRYPTED', and sends it directly over the TCP socket. Absolutely no cryptographic functions are called. As we will see later in our Wireshark demonstration, anyone sniffing the network will be able to read the exact text of the message effortlessly."

---

## 3. Angela: Symmetric (AES) and Asymmetric (RSA) Encryption
**(Estimated Time: 3 - 4 minutes)**

**Angela:** "Hello, I am Angela, and I will explain the first two secure modes handled by our `crypto_utils.py` file: AES and RSA.

Our second mode is AES, which is a Symmetric encryption algorithm. We use AES-256 in Galois/Counter Mode (GCM). This mode provides extremely fast encryption and ensures both confidentiality and data integrity. In our code, we simulate a pre-shared key environment by initializing a static 32-byte key in the `CryptoEngine`. When a user selects AES, the message is encrypted using this pre-shared key, and the resulting JSON payload sent to the socket contains only a Base64-encoded nonce and the ciphertext. While highly secure and fast, the limitation here is key distribution: in the real world, securely sharing that 32-byte key beforehand is incredibly difficult.

To solve the key distribution problem, our third mode implements RSA, an Asymmetric algorithm. Remember the public keys Robledo mentioned during the handshake? When a user selects RSA mode, the application encrypts the message using the peer's Public Key via RSA-OAEP padding. Since only the peer has the corresponding Private Key, the message is perfectly secure without needing a pre-shared secret. However, RSA is slow and has a strict mathematical size limit. For our 2048-bit keys, we can only encrypt very short text payloads. If a user tries to send a large paragraph in RSA mode, the encryption process will functionally fail. This brings us to the ultimate solution, which Karold will explain."

---

## 4. Karold: Hybrid Encryption and Wireshark Live Proof
**(Estimated Time: 4 - 5 minutes)**

**Karold:** "Hi everyone, I'm Karold. To solve the limitations of AES and RSA, our project features a fourth mode: Hybrid Encryption. This combines the speed of AES with the secure key distribution of RSA. 

When a user selects Hybrid mode, our code does three things: First, it generates a brand-new, random 256-bit AES key—an ephemeral key used only for this single message. Second, it encrypts the user's message with this fast AES key. Third, it encrypts the AES key itself using the peer's RSA Public Key. The JSON sent over the network contains the RSA-encrypted AES key, the AES nonce, and the AES-encrypted text. The receiving client simply reverses this process. This represents how modern protocols like TLS actually work.

Now, I am going to prove that our code works exactly as described by intercepting our own traffic using Wireshark. 

*(Karold shares her screen, showing two CryptoChat clients side-by-side, and Wireshark running in the background).*

I have Wireshark capturing traffic on my local loopback interface, filtering for `tcp.port == 9999`. 

First, I will set Client A to 'Unencrypted' mode and send the message: 'This is a secret password'. 
*(Karold hits send).*
If I go to Wireshark, I see the packet. I right-click it, select 'Follow TCP Stream', and... right there in plain red text, you can read the full JSON payload: `{"mode": "UNENCRYPTED", "payload": "This is a secret password"}`. The vulnerability is clearly exposed.

Now, I will set the client to 'Hybrid' mode and send the message: 'Classified data transfer'.
*(Karold hits send).*
I go back to Wireshark, find the new packet, and Follow the TCP Stream. This time, the stream is completely unintelligible. You can see the `"mode": "HYBRID"` tag, but the payload consists entirely of high-entropy Base64 strings representing the encrypted AES key and the ciphertext. The actual message content is cryptographically sealed and impossible to read without the Private Key. 

This proves that our application successfully secures network traffic and that our built-in UI accurately reflects the real-world network bytes. Thank you all for your attention!"
