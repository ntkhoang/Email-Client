import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from EmailSender.send import MyEmailSender
from EmailRetriever.retrieve import MyEmailRetriever
import json
import os


class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail Client")

        self.email_retriever = MyEmailRetriever()
        self.sock = self.email_retriever.connect_to_pop3_server()

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

        #continue here

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailApp(root)
    app.run()
