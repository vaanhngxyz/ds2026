import socket
import os

HOST = "127.0.0.1"
PORT = 8000
BUF = 1024
CLIENT_DIR = "client_files"

def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.rstrip(b"\n").decode("utf-8")

def send_line(sock, text):
    sock.sendall((text + "\n").encode("utf-8"))

def upload_file(sock):
    path = input("File to upload: ").strip()
    if not os.path.exists(path):
        print("File does not exist.")
        return

    filename = os.path.basename(path)
    size = os.path.getsize(path)

    send_line(sock, "UPLOAD")
    send_line(sock, filename)
    send_line(sock, str(size))

    with open(path, "rb") as f:
        while True:
            chunk = f.read(BUF)
            if not chunk:
                break
            sock.sendall(chunk)

    resp = recv_line(sock)
    print("Upload:", "success" if resp == "OK" else "failed")

def download_file(sock):
    filename = input("File to download: ").strip()
    send_line(sock, "DOWNLOAD")
    send_line(sock, filename)

    size_line = recv_line(sock)
    if not size_line or size_line == "ERR":
        print("File not found on server.")
        return

    size = int(size_line)
    os.makedirs(CLIENT_DIR, exist_ok=True)
    path = os.path.join(CLIENT_DIR, filename)

    remaining = size
    with open(path, "wb") as f:
        while remaining > 0:
            chunk = sock.recv(min(BUF, remaining))
            if not chunk:
                break
            f.write(chunk)
            remaining -= len(chunk)

    if remaining == 0:
        print("Downloaded to:", path)
    else:
        print("Download incomplete.")

def chat(sock):
    send_line(sock, "CHAT")
    print("Type 'bye' to end chat.")
    while True:
        msg = input("You: ")
        send_line(sock, msg)
        if msg.lower() == "bye":
            print("[CLIENT] Chat ended by you.")
            break

        reply = recv_line(sock)
        if not reply:
            print("[CLIENT] Server disconnected.")
            break
        print("Server:", reply)
        if reply.lower() == "bye":
            print("[CLIENT] Chat ended by server.")
            break

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"[CLIENT] Connected to {HOST}:{PORT}")

        while True:
            print("\n=== MENU ===")
            print("1. Upload file")
            print("2. Download file")
            print("3. Chat")
            print("4. Exit")
            choice = input("Choose: ").strip()

            if choice == "1":
                upload_file(sock)
            elif choice == "2":
                download_file(sock)
            elif choice == "3":
                chat(sock)
            elif choice == "4":
                send_line(sock, "EXIT")
                print("[CLIENT] Bye!")
                break
            else:
                print("Invalid choice.")

if __name__ == "__main__":
    main()
