import socket
import os

HOST = "127.0.0.1"
PORT = 8000
BUF = 1024
SERVER_DIR = "server_files"

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n") and (chunk := conn.recv(1)):
        data += chunk
    return data[:-1].decode() if data else ""


def send_line(conn, text):
    conn.sendall((text + "\n").encode("utf-8"))

def handle_upload(conn):
    filename = recv_line(conn)
    size = int(recv_line(conn) or 0)

    os.makedirs(SERVER_DIR, exist_ok=True)
    path = os.path.join(SERVER_DIR, filename)

    remaining = size
    with open(path, "wb") as f:
        while remaining > 0:
            chunk = conn.recv(min(BUF, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)

    send_line(conn, "OK" if remaining == 0 else "ERR")

def handle_download(conn):
    filename = recv_line(conn)
    path = os.path.join(SERVER_DIR, filename)

    if not os.path.exists(path):
        send_line(conn, "ERR")
        return

    size = os.path.getsize(path)
    send_line(conn, str(size))

    with open(path, "rb") as f:
        while True:
            chunk = f.read(BUF)
            if not chunk:
                break
            conn.sendall(chunk)

def handle_chat(conn):
    print("[SERVER] Chat started. Type replies in this window.")
    while True:
        msg = recv_line(conn)
        if not msg:
            break
        print("Client:", msg)

        if msg.lower() == "bye":
            send_line(conn, "bye")
            break

        reply = input("Server: ")
        send_line(conn, reply)
        if reply.lower() == "bye":
            break

def handle_client(conn, addr):
    print(f"[SERVER] Connected:", addr)
    with conn:
        while True:
            cmd = recv_line(conn)
            if not cmd:
                break

            if cmd == "UPLOAD":
                handle_upload(conn)
            elif cmd == "DOWNLOAD":
                handle_download(conn)
            elif cmd == "CHAT":
                handle_chat(conn)
            elif cmd == "EXIT":
                break
            else:
                send_line(conn, "ERR")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            handle_client(conn, addr)
            print(f"[SERVER] Connection closed:", addr)


if __name__ == "__main__":
    main()