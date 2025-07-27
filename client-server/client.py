import socket
import threading
import os
import json


# -configs-
host = socket.gethostname()
port = 55555

client_files_path = "client-server\\client-files"

# helper function, gets full data from socket
# helper function, gets full data from conn
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

# functions

def send_file(file_name):

    # validate input

    file_full_path = os.path.join(client_files_path, file_name)
    if not os.path.exists(file_full_path):
        return False, "file was not found"

    # prepare package

    command_obj = {
        "command": "UPLOAD",
        "fname": file_name,
        "data": open(file_full_path, 'rb').read().decode()
    }
    package = json.dumps(command_obj)

    # send package
    with socket.socket() as s:
        s.connect((host, port))
        sendall(s, package.encode())

        reply = recvall(s)
        if b"200 OK" != reply:
            return False, "server did not recieve"
    
    return True, "" # everything went fine


def get_file(file_name):

    # prepare package

    command_obj = {
        "command": "DOWNLOAD",
        "fname": file_name,
    }
    package = json.dumps(command_obj)

    # send package
    with socket.socket() as s:
        s.connect((host, port))
        sendall(s, package.encode())

        reply = recvall(s)
        if b"200 OK" != reply:
            return False, "server did not recieve"
    
        data = recvall(s)
    with open(os.path.join(client_files_path, file_name), "wb") as file:
        file.write(data)
        
    return True, "" # everything went fine

def get_file_list():
    
    # send request
    with socket.socket() as s:
        s.connect((host, port))
        sendall(s, b'{"command": "LIST"}')

        reply = recvall(s)
        if b"200 OK" != reply:
            return False, "server did not recieve"

        data = recvall(s).decode()
    list = json.loads(data)
    return list, ""

def client():
    while True:
        print("""
Welcome to Omer's Server-Client interface
Please input your desired command:
1) UPLOAD a file to the server.
2) DOWNLOAD a file from the server.
3) LIST the files in the server repos.
0) QUIT
""")
        user_command = input("->")
        
        match user_command:
            case "0":
                print("Goodbye!")
                return

            case "1":
                file_name = input("Enter file name:")
                result, reason = send_file(file_name)
                if result:
                    print("file sent OK.")
                else:
                    print("file was not sent:", reason)

            case "2":
                file_name = input("Enter file name:")
                result, reason = get_file(file_name)
                if result:
                    print("file received OK.")
                else:
                    print("file was not received:", reason)

            case "3":
                result, reason = get_file_list()
                if result:
                    print("List of files as follows:\n", result)
                else:
                    print("file list was not received:", reason)


if __name__ == '__main__':
    client()