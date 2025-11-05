import discovery
import rsa
import network
import random
import sys

MSG_HEADS = 11111
MSG_TAILS = 22222

# Server discovery.
server_ip = discovery.find_server_ip()
if not server_ip:
    print("[NETWORK]\tCould not find Alice on the network. Exiting.")
    sys.exit()

print("============================================= Game Start (Bob) =============================================")

(n, eB, dB) = rsa.generate_bob_keys()
print(f"Bob's Keys: n={n}, e={eB}, d={dB}")

conn = network.connect_to_server()

if not conn:
    sys.exit()

with conn:
    packet_data = network.receive_message(conn)
    c_heads_str, c_tails_str = packet_data.split(':')
    c_heads = int(c_heads_str)
    c_tails = int(c_tails_str)
    print(f"[NETWORK]\tReceived encrypted packets from Alice:\n1: {c_heads}\n2: {c_tails}")

    # Pick one packet randomly.
    packets = [c_heads, c_tails]
    picked_packet = random.choice(packets)
    print(f"\n[INFO]\tRandomly picked packet: {picked_packet}")

    # User makes prediction.
    prediction = ""
    while prediction not in ["heads", "tails"]:
        prediction = input("[USER INPUT] Make your prediction (heads/tails): ").lower().strip()

    print("[ENCRYPTION]\tEncrypting the packet user picked with Bob's public key.")
    doubly_encrypted_packet = rsa.encrypt(picked_packet, eB, n)

    # Send packet and prediction to Alice
    payload = f"{doubly_encrypted_packet}:{prediction}"
    print(f"[NETWORK]\tSending doubly-encrypted packet and prediction to Alice.")
    network.send_message(conn, payload)

    half_decrypted_str = network.receive_message(conn)
    half_decrypted_packet = int(half_decrypted_str)
    print(f"\n[NETWORK]\tReceived half-decrypted packet from Alice: {half_decrypted_packet}")

    print("[DECRYPTION]\tDecrypting packet with Bob's private key.")
    original_message = rsa.decrypt(half_decrypted_packet, dB, n)
    print(f"[INFO]\tDecrypted Packet: {original_message}")

    original_choice = ""
    if original_message == MSG_HEADS:
        original_choice = "heads"
    elif original_message == MSG_TAILS:
        original_choice = "tails"

    print("\n[NETWORK]\tSending Bob's public and private keys to Alice for verification.")
    key_payload = f"{n}:{eB}:{dB}"
    network.send_message(conn, key_payload)

    print(f"[GAME]\tDecrypted Packet: {original_choice}")
    print(f"[GAME]\tBob's Prediction: {prediction}")

    if prediction == original_choice:
        print("[WINNER]\tBob wins!")
    else:
        print("[WINNER]\tAlice wins!")

print("[NETWORK]\tConnection closed.")
print("============================================= Game End (Bob) =============================================")