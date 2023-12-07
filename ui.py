import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from EmailSender.send import MyEmailSender
from EmailRetriever.retrieve import MyEmailRetriever
import json
import os
import threading
import time

class EmailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mail Client")
        self.root.minsize(800, 600)
        self.root.maxsize(1080, 720)

        self.email_retriever = MyEmailRetriever()
        self.sock = self.email_retriever.connect_to_pop3_server()
        self.stop_thread = False
        threading.Thread(target=self.auto_load_mail, daemon=True).start()

        self.frame = tk.Frame(root)
        self.frame.place(relx=0.5, rely=0.5, anchor='c')
        
        self.email_listbox = None
        
        self.back_button_from_list_clicked = False
        
        self.back_button_from_list = None
        
        self.open_email_button = None

        self.selected_folder = None
        
        self.login_menu()
        
    def login_menu(self):
        self.username_label = tk.Label(self.frame, text="Username: ")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.username = tk.Entry(self.frame, width=50)
        self.username.grid(row=0, column=1, padx=10, pady=10)
        
        self.password_label = tk.Label(self.frame, text="Password: ")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        
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
            self.delete_login_menu()
            self.main_menu()
    
    def delete_login_menu(self):
        self.username_label.grid_forget()
        self.username.grid_forget()
        self.password_label.grid_forget()
        self.password.grid_forget()
        self.login_button.grid_remove()

    def main_menu(self):
        self.send_email_button = tk.Button(self.frame, text="Send Email", command=self.send_email)
        self.send_email_button.grid(row=2, column=0, padx=20, pady=20)  
        self.view_email_button = tk.Button(self.frame, text="View Email", command=self.view_email)
        self.view_email_button.grid(row=2, column=1, padx=20, pady=20, sticky='e')
        self.logout_button = tk.Button(self.frame, text="Log out", command=self.logout)
        self.logout_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        
    def delete_main_menu_widgets(self):
        self.send_email_button.grid_remove()
        self.view_email_button.grid_remove()
        self.logout_button.grid_remove()
    
    def logout(self):
        self.email_retriever.quit(self.sock)
        self.username_label = tk.Label(self.frame, text="Username: ")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.username = tk.Entry(self.frame, width=50)
        self.username.grid(row=0, column=1, padx=10, pady=10)
        
        self.password_label = tk.Label(self.frame, text="Password: ")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.password = tk.Entry(self.frame, width=50)
        self.password.grid(row=1, column=1, padx=10, pady=10)
        
        self.login_button = tk.Button(self.frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        self.send_email_button.grid_remove()
        self.view_email_button.grid_remove()
        self.logout_button.grid_remove()

    def send_email(self):
        self.delete_main_menu_widgets()
                
        self.to_label = tk.Label(self.frame, text="To:")
        self.to_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.to_entry = tk.Entry(self.frame, width=50)
        self.to_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.cc_label = tk.Label(self.frame, text="CC:")
        self.cc_label.grid(row=1, column=0, padx=10, pady=10)

        self.cc_entry = tk.Entry(self.frame, width=50)
        self.cc_entry.grid(row=1, column=1, padx=10, pady=10)
        
        self.bcc_label = tk.Label(self.frame, text="BCC:")
        self.bcc_label.grid(row=2, column=0, padx=10, pady=10)

        self.bcc_entry = tk.Entry(self.frame, width=50)
        self.bcc_entry.grid(row=2, column=1, padx=10, pady=10)
        
        self.subject_label = tk.Label(self.frame, text="Subject:")
        self.subject_label.grid(row=3, column=0, padx=10, pady=10)

        self.subject_entry = tk.Entry(self.frame, width=50)
        self.subject_entry.grid(row=3, column=1, padx=10, pady=10)

        self.message_label = tk.Label(self.frame, text="Message:")
        self.message_label.grid(row=4, column=0, padx=10, pady=10)

        self.message_text = tk.Text(self.frame, height=10, width=50)
        self.message_text.grid(row=4, column=1, padx=10, pady=10)
        
        self.attachment_label = tk.Label(self.frame, text="Attachment: ")
        self.attachment_label.grid(row=5, column=0, padx=10, pady=10)

        self.attachment_entry = tk.Entry(self.frame, width=50)
        self.attachment_entry.grid(row=5, column=1, padx=10, pady=10)

        self.attachment_button = tk.Button(self.frame, text="Browse", command=self.browse_file)
        self.attachment_button.grid(row=5, column=2, padx=10, pady=10)
                        
        self.send_button = tk.Button(self.frame, text="Send", command=self.send_email_action)
        self.send_button.grid(row=6, column=0, columnspan=3, padx=10, pady=20)
        
        # Create the back_button
        self.back_button_from_send = tk.Button(self.frame, text="Back")

        # Set the command attribute
        self.back_button_from_send["command"] = lambda: self.back_to_main_menu_from_send_email()

        # Grid the button
        self.back_button_from_send.grid(row=7, column=1, padx=10, pady=10)
        
    def back_to_main_menu_from_send_email(self):
        self.to_entry.grid_remove()
        self.cc_entry.grid_remove()
        self.bcc_entry.grid_remove()
        self.subject_entry.grid_remove()
        self.message_text.grid_remove()
        self.attachment_entry.grid_remove()
        self.attachment_button.grid_remove()
        self.send_button.grid_remove()
        self.back_button_from_send.grid_remove()
        self.to_label.grid_remove()
        self.cc_label.grid_remove()
        self.bcc_label.grid_remove()
        self.subject_label.grid_remove()
        self.message_label.grid_remove()
        self.attachment_label.grid_remove()
        self.main_menu()
        
    def browse_file(self):
        filenames = filedialog.askopenfilenames()
        self.attachment_entry.delete(0, tk.END)
        self.attachment_entry.insert(0, ', '.join(filenames))
        
    def send_email_action(self):
        self.stop_thread = True
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
            
        self.stop_thread = False
    
    def view_email(self):
        self.delete_main_menu_widgets()
        
        self.folder_label = tk.Label(self.frame, text="Your emails folder:")
        self.folder_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        
        self.folder_listbox = tk.Listbox(self.frame)
        self.folder_listbox.grid(row=1, column=0, padx=10, pady=10)

        for folder in os.listdir(f'Mail/{self.username.get()}'):
            self.folder_listbox.insert(tk.END, folder)
            
        self.list_emails_button_clicked = False

        self.list_emails_button = tk.Button(self.frame, text="List Emails", command=self.list_emails)
        self.list_emails_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.back_button_from_view = tk.Button(self.frame, text="Back")

        # Set the command attribute
        self.back_button_from_view["command"] = lambda: self.back_to_main_menu_from_view_email()

        # Grid the button
        self.back_button_from_view.grid(row=7, column=0, padx=10, pady=10)
        
        if self.list_emails_button_clicked:
            self.back_button_from_view.grid_forget()
        
    def delete_view_email_widgets(self):
        self.folder_label.grid_forget()
        self.folder_listbox.grid_forget()
        self.list_emails_button.grid_forget()
        self.back_button_from_view.grid_forget()
    
    def back_to_main_menu_from_view_email(self):
        self.delete_view_email_widgets()
        self.main_menu()

    def list_emails(self):
        self.list_emails_button_clicked = True
        self.back_button_from_view.grid_remove()
        # Get the selected folder
        self.selected_folder = self.folder_listbox.get(self.folder_listbox.curselection())

        if self.email_listbox is None or self.back_button_from_list_clicked == True:
            self.email_listbox = tk.Listbox(self.frame, width=50)
            self.email_listbox.grid(row=1, column=1, padx=10, pady=10)
        
        # self.back_button_from_list_clicked = False
        
        self.email_listbox.delete(0, tk.END)
 
        # Create a dictionary to store the email files
        self.email_files = {}
        # Populate the listbox with emails
        for email_file in os.listdir(f'Mail/{self.username.get()}/{self.selected_folder}'):
            with open(f'Mail/{self.username.get()}/{self.selected_folder}/{email_file}', 'r') as f:
                lines = f.readlines()
                from_line = [line for line in lines if line.startswith("From: ")]
                subject_line = [line for line in lines if line.startswith("Subject: ")]
                if from_line and subject_line:
                    from_user = from_line[0][6:].strip()
                    subject = subject_line[0][9:].strip()
                    if self.email_retriever.check_seen_email(email_file):
                        status = ''
                    else:
                        status = '(unseen)'
                    email_item = f"{status} From: {from_user}, Subject<{subject}>"
                    self.email_listbox.insert(tk.END, email_item)
                    self.email_files[email_item] = email_file
                    
        self.email_listbox.update_idletasks()

        if self.open_email_button is None or self.back_button_from_list_clicked == True:
            self.open_email_button = tk.Button(self.frame, text="Open Email", command=self.open_email)
            self.open_email_button.grid(row=2, column=1, padx=10, pady=10)
        
        if self.back_button_from_list is None or self.back_button_from_list_clicked == True:
            self.back_button_from_list = tk.Button(self.frame, text="Back")

            # Set the command attribute
            self.back_button_from_list["command"] = lambda: self.back_to_main_menu_from_list_emails()

            # Grid the button
            self.back_button_from_list.grid(row=7, column=1, padx=10, pady=10)
        
        self.back_button_from_list_clicked = False

    def back_to_main_menu_from_list_emails(self):
        # Remove the widgets in reverse order of creation
        self.back_button_from_list_clicked = True
        self.open_email_button.grid_forget()
        self.email_listbox.grid_forget()
        self.back_button_from_list.grid_remove()
        self.folder_label.grid_forget()
        self.folder_listbox.grid_forget()
        self.list_emails_button.grid_forget()

        # Call main_menu to create the main menu widgets
        self.main_menu()
   
    def open_email(self):
        # Get the selected email item
        selected_email_item = self.email_listbox.get(self.email_listbox.curselection())

        # Get the email file corresponding to the selected email item
        email_file = self.email_files[selected_email_item]
        if not self.email_retriever.check_seen_email(email_file):
            self.email_retriever.save_seen_email(email_file)

        seen_email_item = selected_email_item.replace('(unseen) ', '')
        selected_index = self.email_listbox.curselection()
        self.email_listbox.delete(selected_index)
        self.email_listbox.insert(selected_index, seen_email_item)
        self.email_files[seen_email_item] = self.email_files.pop(selected_email_item)

        # Open the email in a new window
        email_window = tk.Toplevel(self.frame)
        email_window.geometry("500x500")
        email_window.title(email_file)

        # Create a scrollbar
        scrollbar = tk.Scrollbar(email_window)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display the email content in a Text widget for better formatting and scrolling
        text_widget = tk.Text(email_window, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=("Consolas",16))
        with open(f'Mail/{self.username.get()}/{self.selected_folder}/{email_file}', 'r') as f:
            email_content = f.read()
        text_widget.insert(tk.END, self.email_retriever.formated_email(email_content))
        text_widget.configure(state="disabled")
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure the scrollbar
        scrollbar.config(command=text_widget.yview)

        # If there are attachments, create a button to download them
        if self.email_retriever.check_attachments(email_content):
            button_attachment = tk.Button(text_widget, text="Download Attachment", command=lambda:self.download_attachment(email_content))
            button_attachment.pack(side=tk.BOTTOM, pady=10)

    def download_attachment(self, email_content):
        try:
            self.email_retriever.get_attachments(email_content)
            messagebox.showinfo("Download Attachment", "Attachment downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f'An error occurred: {e}')


    def auto_load_mail(self):
        while True:
            if not self.stop_thread:
                self.email_retriever.quit(self.sock)
                self.sock = self.email_retriever.connect_to_pop3_server()
                self.email_retriever.login(self.sock)
                self.email_retriever.make_folder_emails(self.sock)
                time.sleep(int(self.email_retriever.autoload))


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailApp(root)
    app.run()
