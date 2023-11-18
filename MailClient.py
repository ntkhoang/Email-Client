import socket
import json
import os
import base64
import datetime
import uuid

def send_command(sock, command):
    try:
        sock.send(command.encode())
        response = sock.recv(1024).decode()
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
    
def send_command_not_response(sock, command):
    try:
        sock.send(command.encode())
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
    current_time = datetime.datetime.now().strftime( '%d/%m/%Y %H:%M:%S' )
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((smtp_server, smtp_port))
        send_command(sock, 'EHLO client\r\n')
        send_command(sock, f'MAIL FROM: <{from_address}>\r\n')
        
        for address in to_address:
            send_command(sock, f'RCPT TO: <{address}>\r\n')
        for address in cc_address:
            send_command(sock, f'RCPT TO: <{address}>\r\n')
        for address in bcc_address:
            send_command(sock, f'RCPT TO: <{address}>\r\n')
            
        send_command(sock, 'DATA\r\n')
        if '@' in from_address:
            mail_dns = from_address.split('@')
            send_command_not_response(sock, f'Message-ID: <{uuid.uuid4()}@{mail_dns[1]}>\r\n')
        else:
            send_command_not_response(sock, f'Message-ID: <{uuid.uuid4()}>\r\n')
        send_command_not_response(sock, f'Date: {current_time}\r\n')
        send_command_not_response(sock, 'MIME-Version: 1.0\r\n')
        send_command_not_response(sock, 'User-Agent: MailClient\r\n')
        send_command_not_response(sock, f'To: {",".join(to_address)}\r\nCC: {",".join(cc_address)}\r\n')
        send_command_not_response(sock, f'From: {from_address}\r\n')
        send_command_not_response(sock, f'Subject: {subject}\r\n')
        send_command_not_response(sock, f'Content-Type: text/plain; charset={"utf-8" if any(ord(c) > 127 for c in message) else "us-ascii"}, format=flowed\r\n')
        send_command_not_response(sock, f'Content-Transfer-Encoding: {"base64" if any(ord(c) > 127 for c in message) else "7bit"}\r\n')
        send_command_not_response(sock, f'\r\n{message}\r\n.\r\n')
        send_command(sock, 'QUIT\r\n')

def generate_content_type_header(file_name):
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

def generate_boundary():
    boundary = str(uuid.uuid4()).replace('-', '')
    return f'--------------{boundary}'
    
def send_email_with_attachment(smtp_server, smtp_port, from_address, to_address: tuple, cc_address: tuple, bcc_address: tuple, subject, message, attachment_file_name):
    boundary = generate_boundary()
    current_time = datetime.datetime.now().strftime( '%d/%m/%Y %H:%M:%S' )
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((smtp_server, smtp_port))

            send_command(sock, 'EHLO example.com\r\n')
            send_command(sock, f'MAIL FROM: <{from_address}>\r\n')

            for address in to_address + cc_address + bcc_address:
                send_command(sock, f'RCPT TO: <{address}>\r\n')

            send_command(sock, 'DATA\r\n')

            email_message = f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n'
            if '@' in from_address:
                email_message += f"Message-ID: <{uuid.uuid4()}@{from_address.split('@')[1]}>\r\n"
            else:
                email_message += f"Message-ID: <{uuid.uuid4()}>\r\n"
            email_message += f'Date: {current_time}\r\n'
            email_message += 'MIME-Version: 1.0\r\n'
            email_message += 'User-Agent: MailClient\r\n'
            email_message += f'To: {", ".join(to_address)}\r\n'
            email_message += f'CC: {", ".join(cc_address)}\r\n'
            email_message += f'From: <{from_address}>\r\n'
            email_message += f'Subject: {subject}\r\n'
            email_message += '\r\nThis is a multi-part message in MIME format.\r\n'
            email_message += f'{boundary}\r\n'

            email_message += f'Content-Type: text/plain; charset={"UTF-8" if any(ord(c) > 127 for c in message) else "us-ascii"}, format=flowed\r\n'
            email_message += f'Content-Transfer-Encoding: {"base64" if any(ord(c) > 127 for c in message) else "7bit"}\r\n\r\n'
            email_message += f'{message}\r\n\r\n'
            
            email_message += f'{boundary}\r\n'
            email_message += f'Content-Type: {generate_content_type_header(attachment_file_name)}; name="{attachment_file_name}"\r\n'
            email_message += f'Content-Disposition: attachment; filename="{attachment_file_name}"\r\n'
            email_message += f"Content-Transfer-Encoding: base64\r\n\r\n"

            #In the MIME standard, base64 encoded data should be split into multiple lines, each containing no more than 76 characters.
            with open(attachment_file_name, 'rb') as attachment:
                attachment_data = base64.b64encode(attachment.read()).decode()
                formatted_attachment_data = '\r\n'.join(attachment_data[i:i+76] for i in range(0, len(attachment_data), 76))
                email_message += formatted_attachment_data

            email_message += f'\r\n\r\n{boundary}\r\n.\r\n'
            
            # Send the email message
            send_command(sock, email_message)


    except Exception as e:
        print(f"An error occurred while sending the email: {e}")
        
def connect_to_pop3_server(server_address, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_address, port))
    print(sock.recv(1024).decode())
    return sock

def login(sock, username, password):
    send_command(sock, f'USER {username}\r\n')
    send_command(sock, f'PASS {password}\r\n')

def retrieve_email_with_print(sock, email_id):
    return send_command_with_print(sock, f'RETR {email_id}\r\n')

def retrieve_email(sock, email_id):
    return send_command(sock, f'RETR {email_id}\r\n')

def quit(sock):
    send_command(sock, 'QUIT\r\n')
    sock.close()

def save_seen_email(user, email_id):
    # Kiểm tra xem thư mục 'User' có tồn tại không, nếu không thì tạo mới
    if not os.path.exists('SeenEmails'):
        os.makedirs('SeenEmails')
    # Lưu email đã xem vào tệp trong thư mục 'User'
    with open(f'SeenEmails/{user}.txt', 'a') as f:
        f.write(f'{email_id}\n')

def check_seen_email(user, email_id):
    # Kiểm tra xem tệp có tồn tại không
    if not os.path.exists(f'SeenEmails/{user}.txt'):
        return False
    # Đọc tệp để kiểm tra email đã xem
    with open(f'SeenEmails/{user}.txt', 'r') as f:
        seen_emails = f.read().splitlines()
    return email_id in seen_emails

def list_emails(user):
    # Initialize a dictionary to store the emails
    emails_by_folder = {}

    # Walk through the user's mail directory
    for root, dirs, files in os.walk(f'Mail/{user}'):
        for dir in dirs:
            # Initialize a list to store the emails in this folder
            emails = []

            # Walk through this folder
            for subroot, subdirs, subfiles in os.walk(os.path.join(root, dir)):
                # Add each email to the list
                for file in subfiles:
                    emails.append(os.path.join(subroot, file))

            # Add the list of emails to the dictionary
            emails_by_folder[dir] = emails

    # Print the folders
    print("Your mail folders")
    for i, folder in enumerate(emails_by_folder.keys(), start=1):
        print(f"{i}. {folder}")

    # Ask the user to choose a folder
    choice = int(input("Input choice: ")) - 1
    chosen_folder = list(emails_by_folder.keys())[choice]

    # Print the emails in the chosen folder
    for i, email_path in enumerate(emails_by_folder[chosen_folder], start=1):
        with open(email_path, 'r') as f:
            raw_email = f.read()
        lines = raw_email.split('\n')
        from_line = next((line for line in lines if line.lower().startswith('from: ')), None)
        subject_line = next((line for line in lines if line.lower().startswith('subject: ')), None)
        email_id = os.path.basename(email_path)
        seen_status = '(seen)' if check_seen_email(user, email_id) else '(unseen)'
        print(f"{i}. {seen_status} From: {from_line[6:] if from_line else 'Unknown'}, Subject: {subject_line[9:] if subject_line else 'No subject'}")

    # Ask the user to choose an email
    choice = int(input("Input mail you want to read: ")) - 1
    chosen_email = emails_by_folder[chosen_folder][choice]
    # Print the email
    with open(chosen_email, 'r') as f:
        raw_email = f.read()
    print("-------------------------Email-------------------------")
    print(raw_email)
    print("-------------------------------------------------------")
    # Mark the email as seen
    save_seen_email(user, os.path.basename(chosen_email))

def get_downloaded_mail(user):
    return {i for i in os.listdir(f'Mail/{user}')}

def download_mail(sock, user):
    if not os.path.exists(f'Mail/{user}'):
        os.makedirs(f'Mail/{user}')
    downloaded_mail = get_downloaded_mail(user)
    response = send_command(sock, 'UIDL\r\n')
    lines = response.split('\r\n')
    for line in lines[1:-2]:
        parts = line.split(' ')
        if len(parts) != 2: continue
        if parts[1] not in downloaded_mail:
            email = retrieve_email(sock, parts[0]).replace('\r\n', '\n')
            with open(f'Mail/{user}/{parts[1]}', 'w') as f:
                f.write(email[email.find('\n') + 1:])

def get_downloaded_mail(user):
    mails = set()
    for root, dirs, files in os.walk(f'Mail/{user}'):
        for file in files:
            mails.add(os.path.join(root, file))
    return mails

def download_mail(sock, user):
    if not os.path.exists(f'Mail/{user}'):
        os.makedirs(f'Mail/{user}')
    downloaded_mail = get_downloaded_mail(user)
    response = send_command(sock, 'UIDL\r\n')
    lines = response.split('\r\n')
    for line in lines[1:-2]:
        parts = line.split(' ')
        if len(parts) != 2: continue
        mail_path = f'Mail/{user}/{parts[1]}'
        if any(mail.endswith(parts[1]) for mail in downloaded_mail):
            continue  # Skip this email if it's already downloaded
        email = retrieve_email(sock, parts[0]).replace('\r\n', '\n')
        with open(mail_path, 'w') as f:
            f.write(email[email.find('\n') + 1:])


def make_folder_emails(sock, user):
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    # Download all emails
    download_mail(sock, user)

    # Get downloaded emails
    downloaded_mail = get_downloaded_mail(user)

    # Process each email
    for mail_path in downloaded_mail:
        with open(mail_path, 'r') as f:
            raw_email = f.read()
        headers, body = raw_email.split('\n\n', 1)

        moved = False  # Flag to check if the email has been moved

        # Check each filter
        for filter in config['filters']:
            if filter['type'] == 'from':
                from_header = next(line for line in headers.split('\n') if line.lower().startswith('from: '))
                if any(keyword in from_header for keyword in filter['keywords']):
                    move_to_folder(user, mail_path, filter['folder'])
                    moved = True
                    break
            elif filter['type'] == 'subject':
                subject = next(line for line in headers.split('\n') if line.lower().startswith('subject: '))
                if any(keyword in subject for keyword in filter['keywords']):
                    move_to_folder(user, mail_path, filter['folder'])
                    moved = True
                    break
            elif filter['type'] == 'content':
                if any(keyword in body for keyword in filter['keywords']):
                    move_to_folder(user, mail_path, filter['folder'])
                    moved = True
                    break
            elif filter['type'] == 'spam':
                if any(keyword in body for keyword in filter['keywords']):
                    move_to_folder(user, mail_path, filter['folder'])
                    moved = True
                    break

        # If the email has not been moved, move it to the "Inbox" folder
        if not moved:
            move_to_folder(user, mail_path, 'Inbox')

def move_to_folder(user, mail_path, folder):
    if not os.path.exists(f'Mail/{user}/{folder}'):
        os.makedirs(f'Mail/{user}/{folder}')
    new_path = f'Mail/{user}/{folder}/{os.path.basename(mail_path)}'
    if os.path.exists(mail_path) and not os.path.exists(new_path):
        os.rename(mail_path, new_path)

if __name__ == "__main__":
    with open('config.json', 'r') as f:
        config = json.load(f)
    general = config['general']
    username = general['username']
    password = general['password']
    mail_server = general['mailServer']
    smtp = general['smtp']
    pop3 = general['pop3']
    autoload = general['autoload']
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
            print ("Message: ")
            message = ""
            while True:
                line = input()
                if line == '.':
                    break
                message += line + "\n"
            print("Do you want  to attach a file? (y/n)")
            choice = input("Input choice: ")
            if choice == 'y':
                attachment_file_name = input("Input file name: ")
                send_email_with_attachment(mail_server,smtp, username, to_address, cc_address, bcc_address, subject, message, attachment_file_name)
            else:
                send_email(mail_server,smtp, username, to_address, cc_address, bcc_address, subject, message)
            print("Send success")
        elif choice == '2':
            sock = connect_to_pop3_server(mail_server, pop3)
            login(sock, username, password)
            list_emails(sock, username)
            email_id = input("Input mail ID: ")
            retrieve_email_with_print(sock, email_id)
            if not check_seen_email(username, email_id) and not '-ERR Invalid message number' in retrieve_email(sock, email_id):
                save_seen_email(username, email_id)
            quit(sock)
        elif choice == '3':
            break
