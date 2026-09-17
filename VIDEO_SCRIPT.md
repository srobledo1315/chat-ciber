# CryptoChat: Functional Demonstration Video Script

**Target Duration:** ~15 minutes
**Language:** English
**Focus:** Functional aspects, network traffic analysis, cryptography modes, and Wireshark integration.

## The Cast (4 Speakers)
1. **Alice (Host)**: Introduces the project, manages the flow, and asks guiding questions.
2. **Bob (Network Specialist)**: Explains the TCP server, the base architecture, and the Unencrypted mode.
3. **Charlie (Cryptography Expert)**: Explains the different encryption modes (AES, RSA, Hybrid) and the key exchange mechanism.
4. **Diana (Security Analyst / Demo Lead)**: Operates the GUI, performs the live demonstration, and analyzes the socket inspector payloads.

---

### [0:00 - 2:30] Introduction
**(Scene opens with a title card: "CryptoChat: Traffic & Cryptography Inspector". Cut to a 4-way split screen of the speakers.)**

**Alice:** Hello everyone, and welcome to our presentation. Today, our team is thrilled to showcase **CryptoChat**, an educational tool designed specifically for analyzing network traffic and understanding applied cryptography in real-time. I'm Alice, and I'll be guiding our discussion today. Joining me are Bob, Charlie, and Diana. 

**Bob:** Hi everyone. I'll be walking you through the network architecture and how our data travels across the wire.

**Charlie:** Hello! I'll be diving into the cryptographic engines that secure our communications.

**Diana:** And I'm Diana. I'll be running the live demonstration, showing you exactly what our GUI looks like and what a network eavesdropper would see if they were listening in.

**Alice:** Perfect. So, to kick things off, let's talk about the *why*. When we study cybersecurity, we hear a lot about "Confidentiality" and "Man-in-the-Middle" attacks, but visualizing exactly what that looks like at the packet level can be tough. Our project, CryptoChat, bridges that gap. It's a multi-client chat application that lets users toggle between different encryption algorithms in real-time, and it includes a built-in payload inspector that mimics what Wireshark captures. 

**Bob:** Exactly, Alice. Functionally, the system relies on a very straightforward architecture. We have a central TCP Relay Server running on port 9999. It acts as a broadcast hub. When any client sends a packet to the server, the server simply forwards it to all other connected clients. This simulates a typical client-server model over a network where traffic could potentially be intercepted by anyone analyzing that specific port.

**Alice:** That makes sense. But before we even start sending messages, how do the clients establish a secure connection? 

---

### [2:30 - 5:30] The Handshake and Architecture

**Charlie:** That’s a great question, Alice. From a functional perspective, as soon as two clients connect to the server, an automatic handshake takes place. The users don't have to manually type in keys or configure certificates. The moment Diana opens her client, and then Bob opens his, the system generates a 2048-bit RSA key pair for each of them. 

**Diana:** I can show that on the screen right now. *(Screen shares the CryptoChat GUI)*. Notice the status bar at the top right. When I launch my client, it connects to the server and says "Waiting for Peer RSA". As soon as Bob connects his client, a `HANDSHAKE_REQ` packet is sent over the network containing our public keys. Once received, the status badge turns green and says "Peer: Secure Connection OK". 

**Charlie:** Right. And functionally, this means both clients now hold each other's Public Key. This is critical for the asymmetric and hybrid encryption modes we'll discuss later. 

**Alice:** So the setup is entirely automated for the user. Diana, your screen looks very detailed. Can you walk us through the functional areas of the GUI?

**Diana:** Absolutely. The interface is divided into a few key functional zones. At the top, we have our real-time status indicators. Just below that is the most interactive part: the "Transmission Algorithm" selector. This dropdown lets the user switch between four modes on the fly: Unencrypted, AES, RSA, and Hybrid. 

**Alice:** And I see a banner changing below the selector.

**Diana:** Yes! Whenever I select a different mode, a dynamic security banner updates to explain exactly what is happening to the data and what the security implications are. Below that is our Chat History, which formats messages clearly with sender tags and the encryption mode used. Finally, at the bottom, we have the "Socket Inspector" or the "Wireshark View". This terminal shows the exact raw JSON byte string being pushed to the TCP socket, along with packet counts and byte sizes. 

---

### [5:30 - 9:00] Mode 1: Unencrypted Traffic

**Alice:** Let’s get into the core functionality. Bob, can you explain what happens when we use the Unencrypted mode?

**Bob:** Certainly. The Unencrypted mode is our baseline. It represents legacy protocols or poorly configured applications. Functionally, when Diana types a message and hits send in Unencrypted mode, the application takes her text, wraps it in a standard JSON structure with the mode tag set to "UNENCRYPTED", and pushes it directly to the socket.

**Diana:** Let’s demonstrate that. I have "UNENCRYPTED" selected. The red warning banner tells me that my message will be sent in plain text. I'll type: "Secret Password is 12345" and hit send. 

**(Diana hits send. The chat log shows the message with a red [UNENCRYPTED] tag.)**

**Diana:** If we look down at the Socket Inspector, we can see exactly what was transmitted. It shows the raw JSON: `{"mode": "UNENCRYPTED", "payload": "Secret Password is 12345"}`. I can even click the "Copy Payload" button here and paste it right into a Wireshark filter to find this exact packet.

**Bob:** And from a network administrator's perspective, if I am running Wireshark on the loopback interface monitoring port 9999, and I follow the TCP stream for that packet, I will read that exact JSON string. The confidentiality is zero. 

**Alice:** That’s a clear demonstration of why plaintext is dangerous. So, how do we fix it? Charlie, let's talk about AES.

---

### [9:00 - 12:00] Mode 2 & 3: AES and RSA

**Charlie:** To protect the payload, our first option is AES—Advanced Encryption Standard. Functionally, this is a symmetric encryption mode. When Diana selects AES, the application uses a 256-bit AES-GCM key to encrypt the payload. GCM is an authenticated mode, meaning it guarantees both confidentiality and integrity.

**Diana:** I'll switch the dropdown to AES. The banner now turns green, indicating a secure symmetric cipher. I'll send the same message. 

**(Diana sends the message. The chat log shows a green [AES] tag.)**

**Diana:** Now, looking at the Socket Inspector, the transmitted JSON is very different. The payload is no longer text. It contains a `nonce` and a `ciphertext`, both encoded in Base64. If Bob intercepted this in Wireshark, he would just see random alphanumeric characters. 

**Charlie:** Exactly. But AES has a functional limitation: it's symmetric. Both clients need the exact same secret key beforehand. In our educational simulation, we use a pre-shared key for this mode. But in the real world, distributing that key securely over the internet is a massive problem. That brings us to RSA.

**Alice:** Right, RSA uses public and private keys. How does the application handle this functionally?

**Charlie:** When the user selects RSA, the application uses the peer's Public Key—which was exchanged during that initial automated handshake—to encrypt the message. Only the peer, who possesses the matching Private Key, can decrypt it. 

**Diana:** Let’s try it. I select RSA. The banner updates to blue. I send the message. Again, the socket inspector shows a Base64 ciphertext. 

**Charlie:** But here is the functional catch with RSA. It is computationally heavy, meaning it's slow. More importantly, the amount of data you can encrypt is strictly limited by the key size. With a 2048-bit key, you can only send very short text messages. If Diana tried to send a massive paragraph in RSA mode, the application would functionally fail to encrypt it because the payload exceeds the mathematical limits of the key.

---

### [12:00 - 14:00] Mode 4: Hybrid Encryption

**Alice:** So AES is fast but has key distribution problems. RSA solves key distribution but is slow and has size limits. How does CryptoChat solve this?

**Charlie:** This is the pinnacle of the tool's functionality: the Hybrid mode. It combines the best of both algorithms. 

**Alice:** How does that work in practice when a user hits send?

**Charlie:** Functionally, it's a three-step automated process. First, when Diana hits send, the application generates a brand new, random 256-bit AES key—an "ephemeral" key just for this one message. Second, it encrypts her long message using that fast AES key. Third, it takes that small AES key and encrypts *it* using the peer's RSA Public Key. 

**Diana:** I'll select Hybrid mode right now. The banner turns purple and marks it as the "Recommended" mode. I'll type a longer message and send it. 

**(Diana sends the message. The chat log shows a purple [HYBRID] tag.)**

**Diana:** Let's look at the Socket Inspector for this one, because the JSON structure is the most complex. The payload now contains three fields: the `encrypted_key`, which is the AES key wrapped in RSA; the `nonce` for the AES algorithm; and the `ciphertext`, which is the actual encrypted message. 

**Bob:** From a network analysis standpoint, this is what modern secure protocols like TLS do behind the scenes. If I capture this in Wireshark, the payload is completely opaque to me. I can see the packet size and the timing, but the contents are cryptographically sealed. The Socket Inspector in the GUI is brilliant because it lets students see this exact JSON structure without having to dig through hexadecimal streams in Wireshark right away.

---

### [14:00 - 15:00] Conclusion

**Alice:** That is incredibly insightful. To summarize, CryptoChat isn't just a chat application; it's a functional magnifying glass for network traffic. 

**Diana:** Exactly. The fact that I can see the raw bytes in the Socket Inspector, check the exact byte size of the payload, and copy it to my clipboard means I can easily cross-reference the application's behavior with real Wireshark captures. 

**Bob:** And by seamlessly toggling between Unencrypted, AES, RSA, and Hybrid modes, users can immediately observe how security choices impact network packet sizes and payload visibility. 

**Charlie:** Ultimately, it functionally demonstrates the journey from a vulnerable plaintext transmission to a modern, hybrid-encrypted secure channel, complete with automated key exchanges. 

**Alice:** Thank you, Bob, Charlie, and Diana. And thank you all for watching our demonstration of the CryptoChat Traffic and Cryptography Inspector. We hope this tool helps demystify network security and makes packet analysis a bit more accessible. Goodbye!

**(Fade to black with CryptoChat logo and credits.)**
