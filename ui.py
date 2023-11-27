import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
from EmailSender.send import MyEmailSender
from EmailRetriever.retrieve import MyEmailRetriever
import json
import os

class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail Client")
        
        email_retriever = MyEmailRetriever()
        self.sock = email_retriever.connect_to_pop3_server()

        self.frame = tk.Frame(root)
        self.frame.pack(padx=100, pady=100)
        
        username_label = tk.Label(self.frame, text="Username: ")
        username_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.username = tk.Entry(self.frame, width=50)
        self.username.grid(row=0, column=1, padx=10, pady=10)
        
        password_label = tk.Label(self.frame, text="Password: ")
        password_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.password = tk.Entry(self.frame, width=50)
        self.password.grid(row=1, column=1, padx=10, pady=10)
        
        self.login_button = tk.Button(self.frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def login(self):
        username = self.username.get()
        password = self.password.get()
        self.email_retriever = MyEmailRetriever()
        self.email_retriever.username = username
        self.email_retriever.password = password
        self.email_retriever.login(self.sock)
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        if username == config['general']['username'] and password == config['general']['password']:
            self.login_button.grid_remove()
            self.send_email_button = tk.Button(self.frame, text="Send Email", command=self.send_email)
            self.send_email_button.grid(row=3, column=0, padx=20, pady=20)  
            self.view_email_button = tk.Button(self.frame, text="View Email", command=self.view_email)
            self.view_email_button.grid(row=3, column=1, padx=20, pady=20, sticky='e')
            self.logout_button = tk.Button(self.frame, text="Log out", command=self.logout)
            self.logout_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def logout(self):
        self.email_retriever.quit(self.sock)
        self.username.delete(0, tk.END)
        self.password.delete(0, tk.END)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.send_email_button.grid_remove()
        self.view_email_button.grid_remove()
        self.logout_button.grid_remove()

    def send_email(self):
        self.send_email_window = tk.Toplevel(self.root)
        self.send_email_window.title("Send Email")
        
        to_label = tk.Label(self.send_email_window, text="To:")
        to_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.to_entry = tk.Entry(self.send_email_window, width=50)
        self.to_entry.grid(row=0, column=1, padx=10, pady=10)
        
        cc_label = tk.Label(self.send_email_window, text="CC:")
        cc_label.grid(row=1, column=0, padx=10, pady=10)

        self.cc_entry = tk.Entry(self.send_email_window, width=50)
        self.cc_entry.grid(row=1, column=1, padx=10, pady=10)
        
        bcc_label = tk.Label(self.send_email_window, text="BCC:")
        bcc_label.grid(row=2, column=0, padx=10, pady=10)

        self.bcc_entry = tk.Entry(self.send_email_window, width=50)
        self.bcc_entry.grid(row=2, column=1, padx=10, pady=10)
        
        subject_label = tk.Label(self.send_email_window, text="Subject:")
        subject_label.grid(row=3, column=0, padx=10, pady=10)

        self.subject_entry = tk.Entry(self.send_email_window, width=50)
        self.subject_entry.grid(row=3, column=1, padx=10, pady=10)

        message_label = tk.Label(self.send_email_window, text="Message:")
        message_label.grid(row=4, column=0, padx=10, pady=10)

        self.message_text = tk.Text(self.send_email_window, height=10, width=50)
        self.message_text.grid(row=4, column=1, padx=10, pady=10)
        
        attachment_label = tk.Label(self.send_email_window, text="Attachment: ")
        attachment_label.grid(row=5, column=0, padx=10, pady=10)

        self.attachment_entry = tk.Entry(self.send_email_window, width=50)
        self.attachment_entry.grid(row=5, column=1, padx=10, pady=10)

        self.attachment_button = tk.Button(self.send_email_window, text="Browse", command=self.browse_file)
        self.attachment_button.grid(row=5, column=2, padx=10, pady=10)
                        
        send_button = tk.Button(self.send_email_window, text="Send", command=self.send_email_action)
        send_button.grid(row=6, column=0, columnspan=3, padx=10, pady=20)
        
    def browse_file(self):
        filenames = filedialog.askopenfilenames()
        self.attachment_entry.delete(0, tk.END)
        self.attachment_entry.insert(0, ', '.join(filenames))  # insert all filenames into the entry
        
    def send_email_action(self):
        to_address = self.to_entry.get().split(',')
        cc_address = self.cc_entry.get().split(',')
        bcc_address = self.bcc_entry.get().split(',')
        subject = self.subject_entry.get()
        message = self.message_text.get("1.0", tk.END)
        
        attachment = self.attachment_entry.get().split(', ')
        if attachment == ['']:
            attachment = []
            
        for file in attachment:
            if os.path.getsize(file) > 3 * 1024 * 1024:
                messagebox.showerror("Error", f'Attachment {file} is too large. Please select files smaller than 3MB.')
                return
        
        email_sender = MyEmailSender()
        
        try:
            if len(attachment) == 0:
                email_sender.send_email(to_address, cc_address, bcc_address, subject, message)
            else:
                email_sender.send_email_with_attachments(to_address, cc_address, bcc_address, subject, message, attachment)
            messagebox.showinfo("Success", "Email sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f'An error occurred: {e}')
            
        self.send_email_window.destroy()

    def view_email(self):
        self.view_window = tk.Toplevel(self.root)
        self.view_window.title("View Email")
        
        folders = ["Inbox", "Project", "Important", "Work", "Spam"]
        for folder in folders:
            folder_button = tk.Button(self.view_window, text=folder, command=lambda folder=folder: self.view_folder(folder))
            folder_button.pack(padx=10, pady=10)
            
    def view_folder(self, folder):
        self.folder_window = tk.Toplevel(self.view_window)
        self.folder_window.title(folder)
        
        self.emails = []
        for root, dirs, files in os.walk(f'Mail/{self.email_retriever.username}/{folder}'):
            for file in files:
                self.emails.append(os.path.join(root, file))
        
        self.emails.sort(key=lambda email: os.path.getmtime(email))
        
        self.email_buttons = []
        for email in self.emails:
            from_address = ''
            subject = ''
            with open(email, 'r') as f:
                for line in f.read().splitlines():
                    if line.startswith('From: '):
                        from_address = line.split(': ')[1]
                    elif line.startswith('Subject: '):
                        subject = line.split(': ')[1]
            email_button = tk.Button(self.folder_window, text=f'From: <{from_address}>, Subject: {subject}', command=lambda email=email: self.view_email_action(email))
            email_button.pack(padx=10, pady=10)
            self.email_buttons.append(email_button)
        
    def view_email_action(self, email):
        self.email_window = tk.Toplevel(self.folder_window)
        self.email_window.title(email)
        
        with open(email, 'r') as f:
            raw_email_content = f.read()
        
        email_content = raw_email_content
        email_content = self.print_formated_email(email_content)
        
        self.email_text = scrolledtext.ScrolledText(self.email_window, width=100, height=30)
        self.email_text.pack(padx=10, pady=10)
        self.email_text.insert(tk.INSERT, email_content)
        
        attachment_name = self.get_attachments_name(raw_email_content)
        
        line = raw_email_content.splitlines()[0]
        if line.startswith('Content-Type: multipart/mixed;'):
            self.email_text.insert(tk.INSERT, '\n\nAttachments:\n')
            for attachment in attachment_name:
                self.email_text.insert(tk.INSERT, f'{attachment}\n')
            download_attachment_button = tk.Button(self.email_window, text="Download Attachment", command=lambda email=email: self.download_attachment(email))
            download_attachment_button.pack(padx=10, pady=10)
    
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
            
            
    def print_formated_email(self, email):
        headers_to_print = ['Date: ', 'User-Agent: ', 'To: ', 'CC: ', 'BCC: ', 'From: ', 'Subject: ']
        lines = email.split('\n')
        in_body = False
        email_content = ''
        for line in lines:
            if in_body:
                if line.startswith('--') or line == '.':
                    break
                email_content += line + '\n'
            else:  
                for header in headers_to_print:
                    if line.startswith(header):
                        email_content += f"{header}{line[len(header):]}\n"
                        break
                if line == 'Content-Transfer-Encoding: 7bit':
                    in_body = True
        return email_content
        
    def download_attachment(self, email):
        self.attachment_window = tk.Toplevel(self.email_window)
        self.attachment_window.title("Download Attachment")
        
        with open(email, 'r') as f:
            email_content = f.read()
        
        self.attachment_buttons = []
        for line in email_content.splitlines():
            if line.startswith('Attachment: '):
                attachment = line.split(': ')[1]
                attachment_button = tk.Button(self.attachment_window, text=attachment, command=lambda attachment=attachment: self.download_attachment_action(attachment))
                attachment_button.pack(padx=10, pady=10)
                self.attachment_buttons.append(attachment_button)
                
    def download_attachment_action(self, attachment):
        attachment_path = f'Mail/{self.email_retriever.username}/Attachments/{attachment}'
        if os.path.exists(attachment_path):
            messagebox.showinfo("Success", f'Attachment {attachment} already exists.')
            return
        
        with open('config.json', 'r') as f:
            config = json.load(f)
        attachment_path = f'Mail/{self.email_retriever.username}/Attachments/{attachment}'
        email_retriever = MyEmailRetriever()
        email_retriever.username = config['general']['username']
        email_retriever.password = config['general']['password']
        sock = email_retriever.connect_to_pop3_server()
        email_retriever.login(sock)
        email_retriever.download_attachment(sock, attachment, attachment_path)
        email_retriever.quit(sock)
        messagebox.showinfo("Success", f'Attachment {attachment} downloaded successfully.')
    

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailApp(root)
    app.run()
