from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from xmlrpc.client import Binary, Fault
import os

SERVER_DIR = "server_files"
os.makedirs(SERVER_DIR, exist_ok=True)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)

def list_files():
    return os.listdir(SERVER_DIR)

def upload_file(filename, data):
    try:
        safe_name = os.path.basename(filename)
        path = os.path.join(SERVER_DIR, safe_name)
        with open(path, "wb") as f:
            f.write(data.data)
        print(f"[INFO] Uploaded file: {path}")
        return True
    except Exception as e:
        print(f"[ERROR] upload_file: {e}")
        return False

def download_file(filename):
    safe_name = os.path.basename(filename)
    path = os.path.join(SERVER_DIR, safe_name)

    if not os.path.exists(path):
        raise Fault(1, f"File not found: {filename}")

    with open(path, "rb") as f:
        data = f.read()
    print(f"[INFO] Downloaded file: {path}")
    return Binary(data)


if __name__ == "__main__":
    host = "0.0.0.0"
    port = 9000

    with SimpleXMLRPCServer(
        (host, port),
        requestHandler=RequestHandler,
        allow_none=True,
        logRequests=True,
    ) as server:
        print(f"[INFO] RPC file server listening on {host}:{port}")

        # Register functions
        server.register_function(list_files, "list_files")
        server.register_function(upload_file, "upload_file")
        server.register_function(download_file, "download_file")

        # Start serving (blocking)
        server.serve_forever()
