import socket
import json

def send_command(sock, command):
    try:
        sock.send(command.encode())
        response = sock.recv(1024).decode()
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def send_command_with_print(sock, command):
    try:
        sock.send(command.encode())
        response = sock.recv(1024).decode()
        print(response)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    
def send_email(smtp_server,smtp_port, from_address, to_address : tuple, cc_address : tuple, bcc_address : tuple, subject, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((smtp_server, smtp_port))
        send_command(sock, 'EHLO client\r\n')
        send_command(sock, f'MAIL FROM: <{from_address}>\r\n')
        for address in to_address:
            send_command(sock, f'RCPT TO: <{address}>\r\n')
        for address in cc_address:
            send_command(sock, f'RCPT TO: <{address}>\r\n')
        send_command(sock, 'DATA\r\n')
        send_command(sock, f'From: {from_address}\r\n')
        send_command(sock, f'Subject: {subject}\r\nTo: {",".join(to_address)}\r\nCc: {",".join(cc_address)}\r\n\r\n{message}\r\n.\r\n')
        send_command(sock, 'QUIT\r\n')

        for address in bcc_address:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((smtp_server, smtp_port))
                send_command(sock, 'EHLO client\r\n')
                send_command(sock, f'MAIL FROM: <{from_address}>\r\n')
                send_command(sock, f'RCPT TO: <{address}>\r\n')
                send_command(sock, 'DATA\r\n')
                send_command(sock, f'From: {from_address}\r\n')
                send_command(sock, f'Subject: {subject}\r\nTo: {",".join(to_address)}\r\nCc: {",".join(cc_address)}\r\nBCC: {address}\r\n\r\n{message}\r\n.\r\n')
                send_command(sock, 'QUIT\r\n')

def connect_to_pop3_server(server_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, port))
    print(sock.recv(1024).decode())
    return sock

def login(sock, username, password):
    send_command(sock, f'USER {username}\r\n')
    send_command(sock, f'PASS {password}\r\n')

def retrieve_email(sock, email_id):
    return send_command_with_print(sock, f'RETR {email_id}\r\n')

def quit(sock):
    send_command(sock, 'QUIT\r\n')
    sock.close()

def list_emails(sock):
    response = send_command(sock, 'LIST\r\n')
    lines = response.split('\n')
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 2:
            email_id = parts[0]
            email = retrieve_email(sock, email_id)
            from_line = next((line for line in email.split('\n') if line.lower().startswith('from: ')), None)
            subject_line = next((line for line in email.split('\n') if line.lower().startswith('subject: ')), None)
            if from_line and subject_line:
                from_info = from_line.split(":")[1].strip()
                subject_info = subject_line.split(":")[1].strip()
                print(f'{email_id} From: {from_info}, Subject:{subject_info}')


if __name__ == "__main__":
    smtp_server = input("Input Mail Sever: ")
    smtp_port = int(input("Input SMTP port: "))
    from_address = input("Input email address: ")
    while True:
        print("1. Send email")
        print("2. View email from server")
        print("3. Exit")
        choice = input("Input choice: ")
        if choice == '1':
            print("To: ")
            to_address = []
            while True:
                email = input()
                if email == 'end':
                    break
                to_address.append(email)
            print("CC: ")
            cc_address = []
            while True:
                email = input()
                if email == 'end':
                    break
                cc_address.append(email)
            print("BCC: ")
            bcc_address = []
            while True:
                email = input()
                if email == 'end':
                    break
                bcc_address.append(email)
            subject = input("Subject: ")
            message = input("Message: ")
            send_email(smtp_server,smtp_port, from_address, to_address, cc_address, bcc_address, subject, message)
            print("Send success")
        elif choice == '2':
            pop3_server = smtp_server
            port = int(input("Input POP3 port: "))
            username = from_address
            password = input("Input password: ")
            sock = connect_to_pop3_server(pop3_server, port)
            login(sock, username, password)
            list_emails(sock)
            email_id = input("Input mail ID: ")
            retrieve_email(sock, email_id)
            quit(sock)
        elif choice == '3':
            break
