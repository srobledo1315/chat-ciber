# CryptoChat: Functional Presentation Script

**Target Duration:** ~15 minutes
**Language:** English
**Format:** Sequential presentation. Each speaker presents their section entirely before the next speaker begins. No conversational back-and-forth. No live demonstration.

---

## Speaker 1: Introduction and System Architecture
**(Estimated Time: 3.5 - 4 minutes)**

"Hello everyone. Today, our team is presenting CryptoChat, an educational network traffic and cryptography analyzer. In modern network environments, it is easy to take terms like confidentiality, encryption, and man-in-the-middle attacks for granted without truly understanding how the data looks at the packet level. Our objective with CryptoChat is to provide a clear, functional tool that demonstrates exactly how different cryptographic choices affect the network traffic transmitted between clients.

The core of our project is built around a centralized TCP Relay Server. This server is designed to be as lightweight and straightforward as possible. It operates on port 9999 and functions strictly as a broadcast hub. This means that whenever a client sends a network packet to the server, the server takes that exact payload and forwards it to all other connected clients. It does not inspect, modify, or decrypt the traffic. By using this centralized relay architecture, we simulate a realistic network environment where traffic traverses public or untrusted nodes, making it susceptible to interception by packet sniffers like Wireshark.

The client application is where all the logic and cryptographic processing takes place. It features a modern, dark-themed graphical user interface that connects asynchronously to the TCP server. Because the server is just a blind relay, the clients bear the full responsibility for securing their communications. The system supports four distinct operational modes that users can switch between at any time: Unencrypted, AES, RSA, and Hybrid. This design allows users to directly compare the functional differences and the security implications of each cryptographic method without having to restart the application or reconfigure the server.

Ultimately, the architecture is intentionally designed to separate the transport layer from the application security layer. The server handles the transport, while the clients handle the security. This separation is fundamental to understanding end-to-end encryption, which is the primary concept our project aims to illustrate."

---

## Speaker 2: The Automated Handshake and Unencrypted Baseline
**(Estimated Time: 3.5 - 4 minutes)**

"Following the architecture, it is important to understand how the clients establish their initial connection. In many secure systems, exchanging cryptographic keys is the most vulnerable and complex phase. To streamline this and focus on the traffic analysis, our project implements an automated, bidirectional key exchange handshake. 

When a client application is launched, it immediately generates its own unique 2048-bit RSA key pair—a public key and a private key. As soon as a second client connects to the network, the first client automatically detects the presence of a new peer. Without requiring any user intervention, it broadcasts a 'Handshake Request' packet containing its RSA Public Key in PEM format. The receiving client captures this public key, stores it, and immediately responds with a 'Handshake Response' packet containing its own public key. Within milliseconds, both clients have securely exchanged their public keys. The graphical interface updates to reflect that a secure peer connection has been established. This automated handshake is the foundation that allows our asymmetric and hybrid encryption modes to function seamlessly.

With the handshake complete, we can examine the first and most basic mode of operation: Unencrypted transmission. In this baseline mode, the application applies no cryptographic protection whatsoever. When a user types a message and sends it, the application constructs a standard JSON object. This JSON object contains two simple fields: a 'mode' tag indicating it is unencrypted, and a 'payload' field containing the exact plain text of the user's message.

This JSON string is then encoded into standard bytes and pushed directly to the TCP socket on port 9999. If a network administrator or a malicious actor is monitoring that port using a tool like Wireshark, they can reconstruct the TCP stream perfectly. The entire message, including its content and structure, is completely legible in plain text. Functionally, this mode serves as an educational baseline. It visually demonstrates the zero-confidentiality risk inherent in legacy protocols like Telnet, FTP, or standard HTTP, proving that data transmitted without encryption is fundamentally compromised."

---

## Speaker 3: Symmetric (AES) and Asymmetric (RSA) Modes
**(Estimated Time: 3.5 - 4 minutes)**

"To address the vulnerabilities of unencrypted traffic, the project introduces two distinct cryptographic modes: AES and RSA. 

The first secure mode is AES, which stands for Advanced Encryption Standard. Specifically, our system utilizes AES-256 in Galois/Counter Mode, or GCM. This is a symmetric encryption algorithm, meaning the same secret key must be used to both encrypt and decrypt the message. Functionally, AES is incredibly fast and efficient, making it ideal for encrypting large amounts of data. Furthermore, GCM is an authenticated encryption mode. It not only scrambles the text to ensure confidentiality, but it also provides integrity, ensuring the payload has not been tampered with in transit. When a message is sent in AES mode, the resulting JSON payload no longer contains text; instead, it contains a randomly generated nonce and the ciphertext, both encoded in Base64. However, AES has a significant functional limitation: key distribution. Both clients must possess the exact same secret key beforehand. If that key is intercepted during distribution, the entire system is compromised.

To solve the key distribution problem, our third mode implements RSA, an asymmetric encryption algorithm. RSA uses the 2048-bit key pairs generated during the automated handshake. In this mode, when a user sends a message, the system encrypts the payload using the peer's Public Key. Because of the mathematical properties of RSA, this ciphertext can only be decrypted by the peer's corresponding Private Key, which never leaves their machine. This completely eliminates the need to share a secret key in advance.

However, RSA also has functional limitations. It is computationally expensive, making it significantly slower than AES. More importantly, RSA has strict payload size limits. The amount of data you can encrypt cannot exceed the mathematical size of the key itself. For a 2048-bit key, this restricts the payload to very short text messages. Therefore, while RSA solves the secure key distribution problem, it is functionally impractical for transmitting large volumes of data or sustained chat conversations."

---

## Speaker 4: Hybrid Encryption and the Wireshark Monitor
**(Estimated Time: 3.5 - 4 minutes)**

"To overcome the individual limitations of AES and RSA, the project features a fourth mode: Hybrid Encryption. This is the recommended operational mode and represents how modern secure communications, such as TLS and HTTPS, function in the real world.

The Hybrid mode is an automated, multi-step process that combines the speed of AES with the secure distribution of RSA. Functionally, when a message is sent in this mode, the system first generates a brand new, random 256-bit AES key. This key is 'ephemeral,' meaning it is created exclusively for this single message and will be discarded immediately afterward. The system then encrypts the user's message using this fast AES key. Next, to safely transmit this ephemeral AES key to the peer, the system encrypts the AES key itself using the peer's RSA Public Key. 

The final JSON payload transmitted over the network contains three components: the RSA-encrypted AES key, the AES nonce, and the AES-encrypted message. When the peer receives this complex payload, they use their RSA Private Key to decrypt the ephemeral AES key, and then use that AES key to decrypt the actual message. This completely secures the data while allowing for payloads of any size.

Finally, to make these concepts visible, the client features a built-in 'Socket Inspector' or 'Wireshark Monitor'. Rather than forcing users to run external network sniffing tools to see the results, this interface intercepts the exact raw byte strings just milliseconds before they are pushed to the TCP socket. It displays the raw JSON payload in a dedicated terminal window within the application, alongside metrics for packet counts and byte sizes. This allows users to immediately observe how switching from Unencrypted to Hybrid mode transforms legible text into high-entropy, opaque Base64 strings. It effectively demystifies network security by showing users precisely what an eavesdropper would capture, bridging the gap between theoretical cryptography and applied network analysis."
