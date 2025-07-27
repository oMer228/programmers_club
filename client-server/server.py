import socket
import threading
import os
import json


# -configs-
host = socket.gethostname()
port = 55555
repository_dir = 'client-server\\server-repository'

# helper function, gets full data from conn
def sendall(socket:socket.socket, data:bytes):
    socket.sendall(data + b"<<EOF>>")

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


def send_file(file_name):

    # validate input

    file_full_path = os.path.join(repository_dir, file_name)
    if not os.path.exists(file_full_path):
        return False, "file was not found"

    # prepare package

    command_obj = {
        "command": "DOWNLOAD",
        "fname": file_name,
        "data": open(file_full_path, 'rb').read().encode()
    }
    package = json.dumps(command_obj)

    # send package

    with socket.socket() as s:
        s.connect((host, port))
        s.sendall(package.encode())

        reply = recvall(s)
        if "200 OK" != reply:
            return False, "server did not recieve"
    
    return True # everything went fine



def server():
    # make repo dir if does not exist
    if not os.path.exists(repository_dir):
        os.makedirs(repository_dir)
        print(f"Created repository directory: {repository_dir}")


    with socket.socket() as s:
        s.bind((host, port))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected user from {addr}")
            data = recvall(conn)
            

            # decipher command
            rcv_packet = json.loads(data.decode())
            match rcv_packet["command"].upper():
                # send client file list
                case "LIST":
                    list = os.listdir(repository_dir) 
                    file_list = json.dumps(list)
                    s.sendall(file_list.encode())

                # getting client uploaded file
                case "UPLOAD":
                    with open(os.path.join(repository_dir, rcv_packet["fname"]), "wb") as file:
                        file.write(rcv_packet["data"].encode())
                    
                    # confirm reciept 
                    sendall(conn, b"200 OK")


                # sending client requested file
                case "DOWNLOAD":
                    with open(os.path.join(repository_dir, rcv_packet["fname"]), "rb") as file:
                        buffer = file.read()
                        conn.sendall(buffer) 



if __name__ == '__main__':
    server()