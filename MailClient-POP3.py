import socket
import os

def send_command(sock, command):
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print(response)
    return response

def connect_to_pop3_server(server_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, port))
    print(sock.recv(1024).decode())
    return sock

def login(sock, username, password):
    send_command(sock, f'USER {username}\r\n')
    send_command(sock, f'PASS {password}\r\n')

def retrieve_email(sock, email_id):
    return send_command(sock, f'RETR {email_id}\r\n')

def quit(sock):
    send_command(sock, 'QUIT\r\n')
    sock.close()

def load_downloaded_ids(): # Load downloaded email IDs from file
    if os.path.exists('downloaded_ids.txt'):
        with open('downloaded_ids.txt', 'r') as file:
            return file.read().splitlines()
    else:
        return []

def save_downloaded_id(id): # Save downloaded email ID to file
    with open('downloaded_ids.txt', 'a') as file:
        file.write(id + '\n')

def list_emails(sock): # List all emails on the server, not care whether they are downloaded or not
    response = send_command(sock, 'UIDL\r\n')
    lines = response.split('\n')
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 2:
            print(f'Email ID: {parts[1]}')

def list_emails(sock, downloaded_ids): # List all emails on the server, with addional information about whether they are downloaded or not
    response = send_command(sock, 'UIDL\r\n')
    lines = response.split('\n')
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 2 and parts[1] not in downloaded_ids:
            print(f'Email ID: {parts[1]}')           

if __name__ == "__main__":
    downloaded_ids = load_downloaded_ids()
    pop3_server = input("Nhập địa chỉ máy chủ POP3: ")
    port = int(input("Nhập cổng kết nối: "))
    username = input("Nhập tên người dùng: ")
    password = input("Nhập mật khẩu: ")
    sock = connect_to_pop3_server(pop3_server, port)
    login(sock, username, password)
    list_emails(sock, downloaded_ids)
    email_id = input("Nhập ID của email bạn muốn tải về: ")
    if email_id not in downloaded_ids:
        print(retrieve_email(sock, email_id))
        save_downloaded_id(email_id)
    else:
        print("Email này đã được tải về trước đó.")
    quit(sock)