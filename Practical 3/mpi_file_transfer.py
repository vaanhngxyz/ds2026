from mpi4py import MPI
import os

SERVER_RANK = 1
CLIENT_RANK = 0
SERVER_DIR = "server_files"
CLIENT_DIR = "client_files"

COMM = MPI.COMM_WORLD
RANK = COMM.Get_rank()

def server():
    os.makedirs(SERVER_DIR, exist_ok=True)
    print(f"[SERVER {RANK}] Ready, storing files in '{SERVER_DIR}'")

    while True:
        cmd = COMM.recv(source=CLIENT_RANK, tag=0)
        if cmd == "EXIT":
            print("[SERVER] EXIT received, shutting down.")
            break
        elif cmd == "UPLOAD":
            handle_upload()

        elif cmd == "DOWNLOAD":
            handle_download()
        else:
            print(f"[SERVER] Unknown command: {cmd!r}")

def handle_upload():
    filename = COMM.recv(source=CLIENT_RANK, tag=1)
    filedata = COMM.recv(source=CLIENT_RANK, tag=2) 

    path = os.path.join(SERVER_DIR, filename)
    with open(path, "wb") as f:
        f.write(filedata)

    print(f"[SERVER] Stored file '{filename}' ({len(filedata)} bytes)")
    COMM.send("OK", dest=CLIENT_RANK, tag=3)

def handle_download():
    filename = COMM.recv(source=CLIENT_RANK, tag=1)
    path = os.path.join(SERVER_DIR, filename)

    if os.path.exists(path):
        with open(path, "rb") as f:
            data = f.read()
        COMM.send(True, dest=CLIENT_RANK, tag=3)   
        COMM.send(data, dest=CLIENT_RANK, tag=2) 
        print(f"[SERVER] Sent file '{filename}' ({len(data)} bytes)")
    else:
        COMM.send(False, dest=CLIENT_RANK, tag=3) 
        print(f"[SERVER] File not found: '{filename}'")

def client_menu():
    os.makedirs(CLIENT_DIR, exist_ok=True)
    print(f"[CLIENT {RANK}] Ready, local folder '{CLIENT_DIR}'")

    while True:
        print("\n=== MPI FILE TRANSFER MENU ===")
        print("1. Upload file to server")
        print("2. Download file from server")
        print("3. Exit")
        choice = input("Choose: ").strip()

        if choice == "1":
            upload_file()
        elif choice == "2":
            download_file()
        elif choice == "3":
            COMM.send("EXIT", dest=SERVER_RANK, tag=0)
            print("[CLIENT] Exit sent. Bye!")
            break
        else:
            print("Invalid choice, try again.")

def upload_file():
    path = input("Path to local file: ").strip()
    if not os.path.exists(path):
        print("File does not exist.")
        return

    filename = os.path.basename(path)
    with open(path, "rb") as f:
        data = f.read()

    COMM.send("UPLOAD", dest=SERVER_RANK, tag=0)
    COMM.send(filename, dest=SERVER_RANK, tag=1)
    COMM.send(data, dest=SERVER_RANK, tag=2)

    status = COMM.recv(source=SERVER_RANK, tag=3)
    if status == "OK":
        print(f"[CLIENT] Uploaded '{filename}' ({len(data)} bytes)")
    else:
        print("[CLIENT] Upload failed.")

def download_file():
    filename = input("Filename to download from server: ").strip()

    COMM.send("DOWNLOAD", dest=SERVER_RANK, tag=0)
    COMM.send(filename, dest=SERVER_RANK, tag=1)

    exists = COMM.recv(source=SERVER_RANK, tag=3)
    if not exists:
        print("[CLIENT] File does not exist on server.")
        return

    data = COMM.recv(source=SERVER_RANK, tag=2)
    path = os.path.join(CLIENT_DIR, filename)
    with open(path, "wb") as f:
        f.write(data)

    print(f"[CLIENT] Saved file to '{path}' ({len(data)} bytes)")

def main():
    if COMM.Get_size() < 2:
        if RANK == 0:
            print("Run with at least 2 MPI processes, e.g.:")
            print("  mpiexec -n 2 python mpi_file_transfer.py")
        return

    if RANK == SERVER_RANK:
        server()
    elif RANK == CLIENT_RANK:
        client_menu()
    else:
        print(f"[RANK {RANK}] No role assigned. Exiting.")

if __name__ == "__main__":
    main()