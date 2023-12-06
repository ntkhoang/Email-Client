import socket
import json
import os
import base64


class MyEmailRetriever:
    def __init__(self, config_file='config.json'):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.general = self.config['general']
        self.username = self.general['username']
        self.password = self.general['password']
        self.mail_server = self.general['mailServer']
        self.pop3 = self.general['pop3']
        self.autoload = self.general['autoload']

    def send_command(self, sock, command):
        try:
            sock.send(command.encode())
            total_data = []
            sock.settimeout(0.1)
            while True:
                try:
                    data = sock.recv(1024)
                    if not data:
                        break
                    total_data.append(data.decode())
                except socket.timeout:
                    break 
            return ''.join(total_data)
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
        
    def connect_to_pop3_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.mail_server, self.pop3))
        sock.recv(1024).decode()
        return sock

    def retrieve_email(self, sock, email_id):
        return self.send_command(sock, f'RETR {email_id}\r\n')
    
    def quit(self, sock):
        self.send_command(sock, 'QUIT\r\n')
        sock.close()

    def login(self, sock):
        self.send_command(sock, f'USER {self.username}\r\n')
        self.send_command(sock, f'PASS {self.password}\r\n')
    
    def save_seen_email(self, email_id):
        if not os.path.exists('SeenEmails'):
            os.makedirs('SeenEmails')
        with open(f'SeenEmails/{self.username}.txt', 'a') as f:
            f.write(f'{email_id}\n')

    def check_seen_email(self, email_id):
        if not os.path.exists(f'SeenEmails/{self.username}.txt'):
            return False
        with open(f'SeenEmails/{self.username}.txt', 'r') as f:
            seen_emails = f.read().splitlines()
        return email_id in seen_emails
    
    def get_downloaded_mail(self):
        mails = set()
        for root, dirs, files in os.walk(f'Mail/{self.username}'):
            for file in files:
                mails.add(os.path.join(root, file))
        return mails

    def download_mail(self, sock):
        if not os.path.exists(f'Mail/{self.username}'):
            os.makedirs(f'Mail/{self.username}')

        filters = self.config['filters']
        folders = [filter['folder'] for filter in filters]
        for folder in folders:
            if not os.path.exists(f'Mail/{self.username}/{folder}'):
                os.makedirs(f'Mail/{self.username}/{folder}')
        
        if not os.path.exists(f'Mail/{self.username}/Inbox'):
            os.makedirs(f'Mail/{self.username}/Inbox')

        downloaded_mail = self.get_downloaded_mail()
        response = self.send_command(sock, 'UIDL\r\n')
        lines = response.split('\r\n')

        for line in lines[1:-2]:
            parts = line.split(' ')
            if len(parts) != 2: continue
            mail_path = f'Mail/{self.username}/{parts[1]}'
            if any(mail.endswith(parts[1]) for mail in downloaded_mail):
                continue 
            email = self.retrieve_email(sock, parts[0]).replace('\r\n', '\n')

            with open(mail_path, 'w') as f:
                f.write(email[email.find('\n') + 1:])

    def move_to_folder(self, mail_path, folder):
        if not os.path.exists(f'Mail/{self.username}/{folder}'):
            os.makedirs(f'Mail/{self.username}/{folder}')

        new_path = f'Mail/{self.username}/{folder}/{os.path.basename(mail_path)}'

        if os.path.exists(mail_path) and not os.path.exists(new_path):
            os.rename(mail_path, new_path)
        
    def make_folder_emails(self, sock):
        with open('config.json', 'r') as f:
                config = json.load(f)
                self.download_mail(sock)
                downloaded_mail = self.get_downloaded_mail()

                for mail_path in downloaded_mail:
                    with open(mail_path, 'r') as f:
                        raw_email = f.read()
                    raw_email = self.formated_email(raw_email)
                    headers, body = raw_email.split('\n\n', 1)
                    moved = False  

                    for filter in config['filters']:
                        if filter['type'] == 'from':
                            from_header = next(line for line in headers.split('\n') if line.lower().startswith('from: '))
                            if any(keyword in from_header for keyword in filter['keywords']):
                                self.move_to_folder(mail_path, filter['folder'])
                                moved = True
                                break
                        elif filter['type'] == 'subject':
                            subject = next(line for line in headers.split('\n') if line.lower().startswith('subject: '))
                            if any(keyword in subject for keyword in filter['keywords']):
                                self.move_to_folder(mail_path, filter['folder'])
                                moved = True
                                break
                        elif filter['type'] == 'content':
                            if any(keyword in body for keyword in filter['keywords']):
                                self.move_to_folder(mail_path, filter['folder'])
                                moved = True
                                break
                        elif filter['type'] == 'spam':
                            if any(keyword in body for keyword in filter['keywords']):
                                self.move_to_folder(mail_path, filter['folder'])
                                moved = True
                                break
                            
                    if not moved:
                        self.move_to_folder(mail_path, 'Inbox')
    
    def check_attachments(self, email):
        first_line = email.split('\n')[0]
        if (first_line.startswith('Content-Type: multipart/mixed;')):
            return True
        return False

    def get_attachments(self, email):
        boundary = email.split('\n')[0].split(';')[1].split('=')[1]
        boundary = boundary.replace('"', '')
        parts = email.split(boundary)

        for part in parts:
            if "Content-Disposition: attachment;" in part:
                filename = part.split('filename="')[-1].split('"')[0]
                content = part.split("Content-Transfer-Encoding: base64")[-1].strip()
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(content))

    def get_attachments_name(self, email):
        names = []
        lines = email.split('\n')
        for line in lines:
            if line.startswith('Content-Disposition: attachment;'):
                attachment = line.split('=')[1]
                filename = os.path.basename(attachment.strip())
                filename = filename.replace('"', '')
                names.append(filename)
        return names

    def formated_email(self, email):
        formated_mail = []
        headers_to_print = ['Date: ', 'User-Agent: ', 'To: ', 'CC: ', 'BCC: ', 'From: ', 'Subject: ']
        lines = email.split('\n')
        in_body = False
        for line in lines:
            if in_body:
                if line.startswith('--') or line == '.':
                    break
                formated_mail.append(line)
            else:  
                for header in headers_to_print:
                    if line.startswith(header):
                        formated_mail.append(f"{header}{line[len(header):]}")
                        break
                if line == 'Content-Transfer-Encoding: 7bit':
                    in_body = True
        if self.check_attachments(email):
            formated_mail.append('\nAttachment file name:\n')
            formated_mail.extend(self.get_attachments_name(email))
        return '\n'.join(formated_mail)
