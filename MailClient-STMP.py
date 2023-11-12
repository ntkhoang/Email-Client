import socket

def send_command(sock, command):
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print(response)
    return response

def send_email(smtp_server, from_address, to_address, subject, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((smtp_server, 2225))
        send_command(sock, 'EHLO client\r\n')
        send_command(sock, f'MAIL FROM: <{from_address}>\r\n')
        send_command(sock, f'RCPT TO: <{to_address}>\r\n')
        send_command(sock, 'DATA\r\n')
        send_command(sock, f'Subject: {subject}\r\n\r\n{message}\r\n.\r\n')
        send_command(sock, 'QUIT\r\n')

if __name__ == "__main__":
    smtp_server = input("Nhập địa chỉ máy chủ SMTP: ")
    from_address = input("Nhập địa chỉ email người gửi: ")
    to_address = input("Nhập địa chỉ email người nhận: ")
    subject = input("Nhập tiêu đề email: ")
    message = input("Nhập nội dung email: ")
    send_email(smtp_server, from_address, to_address, subject, message)
