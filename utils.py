import socket

def check_port(ip, port):
    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Set a short timeout so it doesn't hang on closed IPs
        s.settimeout(0.1)
        try:
            # result 0 means the connection was successful
            result = s.connect_ex((ip, port))
            return result == 0
        except socket.error:
            return False

def scan_ips(network_prefix: str, target_port: int):
    print(f"Scanning {network_prefix}.0/24 on port {target_port}...")
    ips = []
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        if check_port(ip, target_port):
            ips.append(ip)
    
    return ips

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def send_message_to_server(ip: str, port: int, message: str):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        try:
            s.connect((ip, port))
        except socket.error:
            return False
        bytes_sent = s.send(bytes(message, "utf-8"))
        buf = s.recv(10000)
        response = buf.decode()
        return {"r": response, "sent": bytes_sent}