import socket

PORT = 65432

def create_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', PORT))
    s.listen()
    conn, _ = s.accept()
    return conn, s

def connect_to_server(host_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host_ip, PORT))
        return s
    except ConnectionRefusedError:
        return None

def send_message(conn, message):
    conn.sendall(message.encode('utf-8'))

def receive_message(conn, buffer_size=4096):
    data = conn.recv(buffer_size)
    if not data:
        return None
    return data.decode('utf-8')