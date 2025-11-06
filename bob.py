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
    print("[NETWORK]\t\tCould not find Alice on the network. Exiting.")
    sys.exit()

conn = network.connect_to_server(server_ip)
if not conn:
    sys.exit()
print("Would you like to connect to the server (Alice) (y/n): ")
n = input()
if n == "n":
    sys.exit()

print("Connection established! Would you like to start the game? (y/n): ")
n = input()
if n == "y":
    print("Great! Requested Alice for heads and tails packets!")


print("============================================= Game Start (Bob) =============================================")

(n, eB, dB) = rsa.generate_bob_keys()
print(f"Bob's Generated Keys: n= {n}, public key = {eB}, private key = {dB}")

with conn:
    packet_data = network.receive_message(conn)
    print("[GAME]\t\tReceived encrypted heads and tails from Alice!")
    c_heads_str, c_tails_str = packet_data.split(':')
    c_heads = int(c_heads_str)
    c_tails = int(c_tails_str)
    print(f"[NETWORK]\t\tReceived encrypted packets from Alice: \t{c_heads}\t\t{c_tails}")

    # Pick one packet randomly.
    print("[GAME]\t\tPick a packet (1/2): ")
    n = int(input())
    packets = [c_heads, c_tails]
    picked_packet = packets[n - 1]
    print(f"[GAME]\t\tUser picked the packet {picked_packet}")

    # User makes prediction.
    prediction = ""
    while prediction not in ["heads", "tails"]:
        prediction = input("[USER INPUT]\t\tBob's prediction (heads/tails): ").lower().strip()

    print("[ENCRYPTION]\t\tEncrypting the randomly picked packet Bob's public key.")
    doubly_encrypted_packet = rsa.encrypt(picked_packet, eB, n)

    payload = f"{doubly_encrypted_packet}:{prediction}"
    print(f"[NETWORK]\t\tSending doubly-encrypted packet and prediction to Alice.")
    network.send_message(conn, payload)

    half_decrypted_str = network.receive_message(conn)
    half_decrypted_packet = int(half_decrypted_str)
    print(f"\n[NETWORK]\t\tReceived half-decrypted packet from Alice: {half_decrypted_packet}")

    print("[DECRYPTION]\t\tDecrypting packet with Bob's private key.")
    original_message = rsa.decrypt(half_decrypted_packet, dB, n)
    print(f"[INFO]\t\t\tDecrypted Packet: {original_message}")

    original_choice = ""
    if original_message == MSG_HEADS:
        original_choice = "heads"
    elif original_message == MSG_TAILS:
        original_choice = "tails"

    print("\n[NETWORK]\t\tSending Bob's public and private keys to Alice for verification.")
    key_payload = f"{n}:{eB}:{dB}"
    network.send_message(conn, key_payload)

    print(f"[GAME]\t\t\tDecrypted Packet: {original_choice}")
    print(f"[GAME]\t\t\tBob's Prediction: {prediction}")

    if prediction == original_choice:
        print("[WINNER]\t\tBob wins!")
    else:
        print("[WINNER]\t\tAlice wins!")

print("[NETWORK]\t\tConnection closed.")
print("============================================= Game End (Bob) =============================================")