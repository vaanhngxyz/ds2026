from xmlrpc.client import ServerProxy, Binary, Fault
import os

CLIENT_DIR = "client_files"
os.makedirs(CLIENT_DIR, exist_ok=True)

def menu():
    print("\n=== RPC File Transfer Client ===")
    print("1. List files on server")
    print("2. Upload file to server")
    print("3. Download file from server")
    print("0. Exit")

def list_files(proxy):
    try:
        files = proxy.list_files()
        if not files:
            print("No files on server.")
        else:
            print("Files on server:")
            for name in files:
                print(" -", name)
    except Exception as e:
        print("Error listing files:", e)

def upload(proxy):
    filepath = input("Enter local file path to upload: ").strip()

    if not os.path.exists(filepath):
        print("File does not exist.")
        return

    filename = os.path.basename(filepath)

    try:
        with open(filepath, "rb") as f:
            data = f.read()

        ok = proxy.upload_file(filename, Binary(data))
        if ok:
            print("Upload successful.")
        else:
            print("Upload failed (server returned False).")
    except Exception as e:
        print("Error uploading file:", e)

def download(proxy):
    filename = input("Enter server file name to download: ").strip()

    try:
        binary_data = proxy.download_file(filename)
        # Save to client_files directory
        save_path = os.path.join(CLIENT_DIR, filename)
        with open(save_path, "wb") as f:
            f.write(binary_data.data)
        print(f"Downloaded and saved to {save_path}")
    except Fault as fault:
        print(f"Server error ({fault.faultCode}): {fault.faultString}")
    except Exception as e:
        print("Error downloading file:", e)

if __name__ == "__main__":
    server_host = input("Enter server IP/hostname (default: localhost): ").strip() or "localhost"
    server_port = input("Enter server port (default: 9000): ").strip() or "9000"

    url = f"http://{server_host}:{server_port}"
    proxy = ServerProxy(url, allow_none=True)

    while True:
        menu()
        choice = input("Choose: ").strip()

        if choice == "1":
            list_files(proxy)
        elif choice == "2":
            upload(proxy)
        elif choice == "3":
            download(proxy)
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice.")
