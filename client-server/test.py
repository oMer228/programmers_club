import socket
import os

# -configs-
host = socket.gethostname()
port = 55555

client_files_path = "client-server\\client-files"
server_files_path = "client-server\\server-repository"

# helper function, gets full data from socket
def sendall(socket:socket.socket, bytes):
    socket.sendall(bytes + b"<<EOF>>")

def recvall(socket:socket.socket) -> bytes:
    data = b""

    while True:
        packet = socket.recv(1024)
        if not packet:
            break
        data += packet
        if b"<<EOF>>" == packet[-7:]:
            break

    return data[:-7]

# test uploading a file

target_file_on_server = os.path.join(server_files_path, "test.txt")
if os.path.exists(target_file_on_server):
    os.remove(target_file_on_server)

package = '{"command":"upload", "fname":"test.txt", "data":"abc"}'

# send package
with socket.socket() as s:
    s.connect((host, port))
    sendall(s, package.encode())

    reply = recvall(s)

assert(b"200 OK" == reply)
assert(os.path.exists(target_file_on_server))
assert(open(target_file_on_server, 'rb').read() == b"abc")

print("upload test done")
