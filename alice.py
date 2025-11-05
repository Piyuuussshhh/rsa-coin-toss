import threading
import discovery
import rsa
import network

MSG_HEADS = 11111
MSG_TAILS = 22222

# Server Discovery.
stop_broadcast_event = threading.Event()
broadcast_thread = threading.Thread(
    target=discovery.broadcast_server_ip,
    args=(stop_broadcast_event,),
    daemon=True
)
broadcast_thread.start()

print("============================================= Game Start (Alice) =============================================")

(n, eA, dA) = rsa.generate_alice_keys()
print(f"[INFO]\t\t\tAlice's Keys: n= {n}, public key =  {eA}, private key = {dA}")

print("\n[ENCRYPTION]\t\tEncrypting 'heads' and 'tails' with Alice's public key.")
c_heads = rsa.encrypt(MSG_HEADS, eA, n)
c_tails = rsa.encrypt(MSG_TAILS, eA, n)
print(f"[INFO]\t\t\tEncrypted HEADS = {c_heads}")
print(f"[INFO]\t\t\tEncrypted TAILS = {c_tails}")
alice_copy = {c_heads: MSG_HEADS, c_tails: MSG_TAILS}

conn, server_socket = network.create_server()

with conn:
    packet_payload = f"{c_heads}:{c_tails}"
    network.send_message(conn, packet_payload)

    data = network.receive_message(conn)
    bob_packet_str, bob_prediction = data.split(':')
    bob_packet_doubly_encrypted = int(bob_packet_str)

    print(f"\n[NETWORK]\t\tReceived packet from Bob: {bob_packet_doubly_encrypted}")
    print(f"[GAME]\t\t\tBob's prediction: {bob_prediction}")

    print("[DECRYPTION]\t\tDecrypting packet with Alice's private key.")
    half_decrypted_packet = rsa.decrypt(bob_packet_doubly_encrypted, dA, n)
    print(f"[NETWORK]\t\tSending half-decrypted packet: {half_decrypted_packet}")
    network.send_message(conn, str(half_decrypted_packet))

    bob_key_verification = network.receive_message(conn)
    _, eB_str, dB_str = bob_key_verification.split(":")
    eB = int(eB_str)
    dB = int(dB_str)
    print(f"\n[GAME]\t\t\tReceived Bob's keys for verification: public key = {eB}, private key = {dB}")

    original_message = rsa.decrypt(half_decrypted_packet, dB, n)

    # 2. Check the message
    original_choice = ""
    if original_message == MSG_HEADS:
        original_choice = "heads"
    elif original_message == MSG_TAILS:
        original_choice = "tails"
    else:
        print("VERIFICATION FAILED: Unknown message!")

    print(f"[INFO]\t\t\tBob's half-decrypted packet decrypted with his key is: {original_message}")
    print(f"[INFO]\t\t\tThis corresponds to: {original_choice}")

    if bob_prediction == original_choice:
        print(f"[GAME]\t\t\tBob's prediction ({bob_prediction}) was CORRECT.")
        print("[WINNER]\t\tBOB WINS")
    else:
        print(f"[GAME]\t\t\tBob's prediction ({bob_prediction}) was INCORRECT.")
        print("[WINNER]\t\tALICE WINS")

# Clean up the main server socket
server_socket.close()
print("\n[NETWORK]\t\tServer shut down.")
print("============================================= Game End (Alice) =============================================")