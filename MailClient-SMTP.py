import socket

def send_command(sock, command):
    sock.sendall(command.encode())
    response = sock.recv(1024)
    if not response:
        print("No response from server. The connection may have been closed.")
        return
    print(response.decode())
    
def send_email(smtp_server, from_address, to_address : tuple, cc_address : tuple, bcc_address : tuple, subject, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((smtp_server, 2225))
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
                sock.connect((smtp_server, 2225))
                send_command(sock, 'EHLO client\r\n')
                send_command(sock, f'MAIL FROM: <{from_address}>\r\n')
                send_command(sock, f'RCPT TO: <{address}>\r\n')
                send_command(sock, 'DATA\r\n')
                send_command(sock, f'From: {from_address}\r\n')
                send_command(sock, f'Subject: {subject}\r\nTo: {",".join(to_address)}\r\nCc: {",".join(cc_address)}\r\nBCC: {address}\r\n\r\n{message}\r\n.\r\n')
                send_command(sock, 'QUIT\r\n')

if __name__ == "__main__":
    smtp_server = input("Input SMPT: ")
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
            send_email(smtp_server, from_address, to_address, cc_address, bcc_address, subject, message)
