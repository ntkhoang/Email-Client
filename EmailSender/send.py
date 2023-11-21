import socket
import json
import datetime
import uuid
import os
import base64

class MyEmailSender:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.general = self.config['general']
        self.username = self.general['username']
        self.password = self.general['password']
        self.mail_server = self.general['mailServer']
        self.smtp = self.general['smtp']
        self.autoload = self.general['autoload']

    def connect_to_smtp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.mail_server, self.smtp))
        return sock

    def send_command(self, sock, command):
        try:
            sock.send(command.encode())
            response = sock.recv(1024).decode()
            return response
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
    
    def send_command_not_response(self, sock, command):
        try:
            sock.send(command.encode())
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""

    def generate_boundary(self):
        boundary = str(uuid.uuid4()).replace('-', '')
        return f'--------------{boundary}'

    def check_file_size(self, file_name):
        try:
            return os.path.getsize(file_name)
        except Exception as e:
            print(f"An error occurred: {e}")
            return 0
        
    def generate_content_type_header(self, file_name):
        file_type = file_name.split('.')[-1]
        if file_type == 'txt':
            return 'text/plain'
        elif file_type == 'jpg' or file_type == 'jpeg':
            return 'image/jpeg'
        elif file_type == 'png':
            return 'image/png'
        elif file_type == 'pdf':
            return 'application/pdf'
        elif file_type == 'doc' or file_type == 'docx':
            return 'application/msword'
        elif file_type == 'xls' or file_type == 'xlsx':
            return 'application/vnd.ms-excel'
        elif file_type == 'ppt' or file_type == 'pptx':
            return 'application/vnd.ms-powerpoint'
        elif file_type == 'zip':
            return 'application/zip'
        else:
            return 'application/octet-stream'

    def send_email(self, to_address, cc_address, bcc_address, subject, message):
        current_time = datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        with self.connect_to_smtp_server() as sock:
            self.send_command(sock, 'EHLO client\r\n')
            self.send_command(sock, f'MAIL FROM: <{self.username}>\r\n')

            for address in to_address:
                self.send_command(sock, f'RCPT TO: <{address}>\r\n')
            for address in cc_address:
                self.send_command(sock, f'RCPT TO: <{address}>\r\n')
            for address in bcc_address:
                self.send_command(sock, f'RCPT TO: <{address}>\r\n')

            self.send_command(sock, 'DATA\r\n')
            if '@' in self.username:
                mail_dns = self.username.split('@')
                self.send_command_not_response(sock, f'Message-ID: <{uuid.uuid4()}@{mail_dns[1]}>\r\n')
            else:
                self.send_command_not_response(sock, f'Message-ID: <{uuid.uuid4()}>\r\n')
            self.send_command_not_response(sock, f'Date: {current_time}\r\n')
            self.send_command_not_response(sock, 'MIME-Version: 1.0\r\n')
            self.send_command_not_response(sock, 'User-Agent: MailClient\r\n')
            self.send_command_not_response(sock, f'To: {",".join(to_address)}\r\n')
            if len(cc_address) > 0:
                self.send_command_not_response(sock, f'CC: {",".join(cc_address)}\r\n')
            self.send_command_not_response(sock, f'From: <{self.username}>\r\n')
            self.send_command_not_response(sock, f'Subject: {subject}\r\n')
            self.send_command_not_response(sock, f'Content-Type: text/plain; charset={"utf-8" if any(ord(c) > 127 for c in message) else "us-ascii"}; format=flowed\r\n')
            self.send_command_not_response(sock, f'Content-Transfer-Encoding: {"base64" if any(ord(c) > 127 for c in message) else "7bit"}\r\n')
            self.send_command_not_response(sock, f'\r\n{message}\r\n.\r\n')
            self.send_command(sock, 'QUIT\r\n')

    def send_email_with_attachments(self, to_address, cc_address, bcc_address, subject, message, attachment_file_names):
        with self.connect_to_smtp_server() as sock:
            boundary = self.generate_boundary()
            current_time = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((self.mail_server, self.smtp))

                    self.send_command(sock, 'EHLO localhost\r\n')
                    self.send_command(sock, f'MAIL FROM: <{self.username}>\r\n')

                    for address in to_address:
                        self.send_command(sock, f'RCPT TO: <{address}>\r\n')
                    for address in cc_address:
                        self.send_command(sock, f'RCPT TO: <{address}>\r\n')
                    for address in bcc_address:
                        self.send_command(sock, f'RCPT TO: <{address}>\r\n')

                    self.send_command(sock, 'DATA\r\n')

                    email_msg = f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n'
                    if '@' in self.username:
                        email_msg += f'Message-ID: <{uuid.uuid4()}@{self.username.split("@")[1]}>\r\n'
                    else:
                        email_msg += f'Message-ID: <{uuid.uuid4()}>\r\n'
                    email_msg += f'Date: {current_time}\r\n'
                    email_msg += 'MIME-Version: 1.0\r\n'
                    email_msg += 'User-Agent: MailClient\r\n'
                    email_msg += f'To: {", ".join(to_address)}\r\n'
                    if len(cc_address) > 0:
                        email_msg += f'CC: {", ".join(cc_address)}\r\n'    
                    email_msg += f'From: <{self.username}>\r\n'
                    email_msg += f'Subject: {subject}\r\n'
                    email_msg += '\r\n'
                    email_msg += 'This is a multi-part message in MIME format.\r\n'
                    email_msg += f'{boundary}\r\n'

                    email_msg += f'Content-Type: text/plain; charset={"UTF-8" if any(ord(c) > 127 for c in message) else "us-ascii"}, format=flowed\r\n'
                    email_msg += f'Content-Transfer-Encoding: 7bit\r\n'
                    email_msg += f'\r\n{message}\r\n'

                    for file_name in attachment_file_names:
                        email_msg += f'{boundary}\r\n'
                        file_type = file_name.split('.')[-1]
                        if file_type == 'txt':
                            email_msg += f'Content-Type: {self.generate_content_type_header(file_name)}; charset={"UTF-8" if any(ord(c) > 127 for c in message) else "us-ascii"}, name="{file_name}"\r\n'
                        else:
                            email_msg += f'Content-Type: {self.generate_content_type_header(file_name)}; name="{file_name}"\r\n'
                        email_msg += f'Content-Disposition: attachment; filename="{file_name}"\r\n'
                        email_msg += f'Content-Transfer-Encoding: base64\r\n'
                        email_msg += '\r\n'
                        with open(file_name, 'rb') as attachment:  # Corrected line
                            attachment_data = base64.b64encode(attachment.read()).decode()
                            formatted_attachment_data = '\r\n'.join(attachment_data[i:i+72] for i in range(0, len(attachment_data), 72))
                            email_msg += formatted_attachment_data
                        email_msg += '\r\n'

                    email_msg += f'\r\n\r\n{boundary}--\r\n.\r\n'
                    self.send_command(sock, email_msg)
            except Exception as e:
                print(f"An error occurred: {e}")
                return ""
