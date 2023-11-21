from EmailSender.send import MyEmailSender
from EmailRetriever.retrieve import MyEmailRetriever
import asyncio
import aioconsole

async def MailClient():
    while True:
        print("1. Send email")
        print("2. View email from server")
        print("3. Exit")
        choice = await aioconsole.ainput("Input choice: ")
        if choice == '1':
            email_sender = MyEmailSender()
            print("To: ")
            to_address = []
            while True:
                email = await aioconsole.ainput()
                if email == 'end':
                    break
                to_address.append(email)
            print("CC: ")
            cc_address = []
            while True:
                email = await aioconsole.ainput()
                if email == 'end':
                    break
                cc_address.append(email)
            print("BCC: ")
            bcc_address = []
            while True:
                email = await aioconsole.ainput()
                if email == 'end':
                    break
                bcc_address.append(email)
            subject = await aioconsole.ainput("Subject: ")
            print ("Message: ")
            message = ""
            while True:
                line = await aioconsole.ainput()
                if line == '.':
                    break
                message += line + "\n"
            print("Do you want to attach a file? (y/n)")
            choice = await aioconsole.ainput("Input choice: ")
            if choice == 'y':
                num_of_file = await aioconsole.ainput("How many files do you want to attach? ")
                attachment_file_name = []
                for i in range(int(num_of_file)):
                    check = False
                    while check == False:
                        file_name = await aioconsole.ainput("Input file name: ")
                        if email_sender.check_file_size(file_name) <= 3e+6:
                            attachment_file_name.append(file_name)
                            check = True
                        else:
                            print("File size is too large")                        
                email_sender.send_email_with_attachments(to_address, cc_address, bcc_address, subject, message, attachment_file_name)
            else:
                email_sender.send_email(to_address, cc_address, bcc_address, subject, message)
            print("Send success")
        elif choice == '2':
            email_retriever = MyEmailRetriever()
            sock = email_retriever.connect_to_pop3_server()
            email_retriever.login(sock)
            email_retriever.make_folder_emails(sock)
            email_retriever.list_emails()
            email_retriever.quit(sock)

async def main():
    email_retriever = MyEmailRetriever()
    sock = email_retriever.connect_to_pop3_server()
    asyncio.create_task(email_retriever.make_folder_emails(sock))
    await MailClient()

asyncio.run(main())