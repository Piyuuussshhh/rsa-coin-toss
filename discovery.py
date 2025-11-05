import socket

DISCOVERY_PORT = 65431
DISCOVERY_MESSAGE = "COIN_TOSS_ALICE_IP:"

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def broadcast_server_ip(stop_event):
    local_ip = get_local_ip()
    message = (DISCOVERY_MESSAGE + local_ip).encode('utf-8')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print(f"[NETWORK:DISCOVERY]\tBroadcasting Alice's IP ({local_ip}) on port {DISCOVERY_PORT}")

    while not stop_event.is_set():
        s.sendto(message, ('<broadcast>', DISCOVERY_PORT))
        try:
            stop_event.wait(2.0)
        except Exception:
            pass

    s.close()
    print("[NETWORK:DISCOVERY]\tBroadcast stopped.")

def find_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind(('', DISCOVERY_PORT))
    except OSError as e:
        print(f"[NETWORK:DISCOVERY]\tError: Could not bind to port {DISCOVERY_PORT}. Is another Bob running?")
        print(f"[NETWORK:DISCOVERY]\tDetails: {e}")
        return None

    print(f"[NETWORK:DISCOVERY]\tListening for Alice on port {DISCOVERY_PORT}...")

    while True:
        try:
            data, _ = s.recvfrom(1024)
            message = data.decode('utf-8')

            if message.startswith(DISCOVERY_MESSAGE):
                ip = message.split(':')[-1]
                print(f"[NETWORK:DISCOVERY]\tFound Alice at: {ip}")
                s.close()
                return ip
        except Exception as e:
            print(f"[NETWORK:DISCOVERY]\tError: {e}")
            s.close()
            return None