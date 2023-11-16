import socket
import json
import os
import base64

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

def read_file_type(file_name):
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
    
def send_email_with_attachment(smtp_server, smtp_port, from_address, to_address: tuple, cc_address: tuple, bcc_address: tuple, subject, message, attachment_file_name):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((smtp_server, smtp_port))

            send_command_with_print(sock, 'EHLO example.com\r\n')
            send_command_with_print(sock, f'MAIL FROM: <{from_address}>\r\n')

            for address in to_address + cc_address:
                send_command_with_print(sock, f'RCPT TO: <{address}>\r\n')

            send_command_with_print(sock, 'DATA\r\n')

            # Compose the email message with attachment
            email_message = f"From: {from_address}\r\nTo: {', '.join(to_address)}\r\n"
            email_message += f"Cc: {', '.join(cc_address)}\r\n"
            email_message += f"Subject: {subject}\r\n"
            email_message += f"MIME-Version: 1.0\r\n"
            email_message += f"Content-Type: multipart/mixed; boundary=boundary123\r\n\r\n"
            email_message += f"--boundary123\r\nContent-Type: text/plain\r\n\r\n{message}\r\n\r\n"
            type = read_file_type(attachment_file_name)
            email_message += f"--boundary123\r\nContent-Type: {type}\r\nContent-Disposition: attachment; filename={attachment_file_name}\r\n\r\n"

            #In the MIME standard, base64 encoded data should be split into multiple lines, each containing no more than 76 characters.
            with open(attachment_file_name, 'rb') as attachment:
                attachment_data = base64.b64encode(attachment.read()).decode()
                formatted_attachment_data = '\r\n'.join(attachment_data[i:i+76] for i in range(0, len(attachment_data), 76))
                email_message += formatted_attachment_data

            email_message += "\r\n--boundary123--\r\n.\r\n"

            # Send the email message
            send_command_with_print(sock, email_message)

            for address in bcc_address:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((smtp_server, smtp_port))
                    send_command_with_print(sock, 'EHLO example.com\r\n')
                    send_command_with_print(sock, f'MAIL FROM: <{from_address}>\r\n')
                    send_command_with_print(sock, f'RCPT TO: <{address}>\r\n')
                    send_command_with_print(sock, 'DATA\r\n')
                    email_message = f"From: {from_address}\r\nTo: {', '.join(to_address)}\r\n"
                    email_message += f"Cc: {', '.join(cc_address)}\r\n"
                    email_message += f"Bcc: {address}\r\n"
                    email_message += f"Subject: {subject}\r\n"
                    email_message += f"MIME-Version: 1.0\r\n"
                    email_message += f"Content-Type: multipart/mixed; boundary=boundary123\r\n\r\n"
                    email_message += f"--boundary123\r\nContent-Type: text/plain\r\n\r\n{message}\r\n\r\n"
                    email_message += f"--boundary123\r\nContent-Type: {type}\r\nContent-Disposition: attachment; filename={attachment_file_name}\r\n\r\n"

                    with open(attachment_file_name, 'rb') as attachment:
                        attachment_data = base64.b64encode(attachment.read()).decode()
                        formatted_attachment_data = '\r\n'.join(attachment_data[i:i+76] for i in range(0, len(attachment_data), 76))
                        email_message += formatted_attachment_data

                    email_message += "\r\n--boundary123--\r\n.\r\n"

                    # Send the email message
                    send_command_with_print(sock, email_message)

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
    if not os.path.exists('User'):
        os.makedirs('User')
    # Lưu email đã xem vào tệp trong thư mục 'User'
    with open(f'User/{user}.txt', 'a') as f:
        f.write(f'{email_id}\n')

def check_seen_email(user, email_id):
    # Kiểm tra xem tệp có tồn tại không
    if not os.path.exists(f'User/{user}.txt'):
        return False
    # Đọc tệp để kiểm tra email đã xem
    with open(f'User/{user}.txt', 'r') as f:
        seen_emails = f.read().splitlines()
    return email_id in seen_emails

def list_emails(sock, user):
    # Load filters from config file
    with open('config.json', 'r') as f:
        config = json.load(f)
    filters = config['filters']

    # Create a dictionary to store emails by folder
    folders = {filter['folder']: [] for filter in filters}
    folders['Inbox'] = []

    response = send_command(sock, 'LIST\r\n')
    lines = response.split('\n')
    for line in lines[1:]:
        parts = line.split()
        if len(parts) == 2:
            email_id = parts[0]
            email = retrieve_email(sock, email_id)
            from_line = next((line for line in email.split('\n') if line.lower().startswith('from: ')), None)
            subject_line = next((line for line in email.split('\n') if line.lower().startswith('subject: ')), None)
            from_info = from_line.split(":")[1].strip() if from_line else 'None'
            subject_info = subject_line.split(":")[1].strip() if subject_line else 'None'

            # Apply filters
            folder = 'Inbox' 
            for filter in filters:
                if filter['type'] == 'from' and from_info in filter['keywords']:
                    folder = filter['folder']
                elif filter['type'] == 'subject' and subject_info in filter['keywords']:
                    folder = filter['folder']
                elif filter['type'] == 'content' and any(keyword in email for keyword in filter['keywords']):
                    folder = filter['folder']
                elif filter['type'] == 'spam' and any(keyword in email for keyword in filter['keywords']):
                    folder = filter['folder']

            # Check if email has been seen
            seen = check_seen_email(user, email_id)
            seen_status = '' if seen else '(unseen)'

            # Add email to folder
            folders[folder].append(f'{email_id} {seen_status} From: {from_info}, Subject: {subject_info}')

    # Print folders
    print('List folder in your mail box:')
    for i, folder in enumerate(folders.keys(), start=1):
        print(f'{i}. {folder}')

    while True:
        # Get user choice
        choice = input('Your choice: ')
        chosen_folder = list(folders.keys())[int(choice) - 1]

        # Print emails in chosen folder or allow to choose again
        if folders[chosen_folder]:
            for email in folders[chosen_folder]:
                print(email)
                email_id = email.split()[0]
            break
        else:
            print('No emails in this folder. Please choose another.')

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
