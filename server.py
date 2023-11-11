import os.path
import re
from socket import *
import sys

global boolean
boolean = True
Boolean = True
save_path = 'email/'

while True:
    try:
        print("Server starting")
        serverPort = 8080
        serverName = 'localhost'
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.bind((serverName, serverPort))
        serverSocket.listen(5)
        break
    except:
        print('Socket connection error. Try again.')
        sys.exit()
print ("Connection Establish")

while Boolean:
    try:
        connectionSocket, addr = serverSocket.accept()
        connectionSocket.send("220 Connection accepted from " + gethostname().encode())
    except:
        print('Socket connection error.')
        sys.exit()

    # receive HELO from client
    try:
        helo = connectionSocket.decode(1024)
        print(helo)
        if helo[:4] == 'EHLO':
            helo = connectionSocket.recv(1024).decode()
            boolean = True
    except:
        print('HELO error. Try again.')
        sys.exit()
        
    while boolean:
        # receive mail command
        command = connectionSocket.decode(1024)
        print(command)
        # check if command input is out of order
        _check1 = re.match(r'RCPT(\s+|$)TO:', command)
        _check2 = re.match(r'DATA', command)

        # checks for valid MAIL FROM command 
        _cmd = re.match(r'MAIL(\s+|$)FROM:' , command)
        # checks for valid path
        _path = re.match(r'MAIL(.+)FROM:(\s*)<[^\s](.+)@(.+)[^\s]>', command)
        # checks for valid mailbox
        _mb = re.match(r'MAIL(.+)FROM:(\s*)<([\+/\'!\?\w-]+)@[^\s](.+)[^\s]>', command)
        # checks for valid local-part
        _lp = re.match(r'MAIL(.+)FROM:(\s*)<([\+/\'!\?\w-]+)@(.+)>', command)
        # checks for valid url domain 
        _domain = re.search(r'MAIL(.+)FROM:(\s*)<(.+)@([\D.]+)>', command)

        if _check1:
            connectionSocket.encode('503 Bad sequence of commands')
            continue
        if _check2:
            connectionSocket.encode('503 Bad sequence of commands')
            continue
        elif not _cmd:
            connectionSocket.encode('500 Syntax error: command unrecognized')
            continue
        elif not _path:
            connectionSocket.encode('501 Syntax error in parameters or arguments')
            continue
        elif not _mb:
            connectionSocket.encode('501 Syntax error in parameters or arguments')
            continue
        elif not _lp:
            connectionSocket.encode('501 Syntax error in parameters or arguments')
            continue
        elif not _domain:
            connectionSocket.encode('501 Syntax error in parameters or arguments')
            continue
        else:
            From = command.replace("MAIL FROM", "From")
            connectionSocket.encode('250 OK')

        _bool = True
        to_list = []
        rcpt_list = []

        while boolean:

            # receive receipt
            receipt = connectionSocket.decode(1024)
            print(receipt)
            # checks for out of order commands 
            check = re.match(r'DATA', receipt)
            # if check:
            # _bool=False   
            check2 = re.match(r'MAIL(\s+|$)FROM:' , receipt)

            # checks for valid RECEIPT TO command 
            rcpt = re.match(r'RCPT(\s+|$)TO:', receipt)
            # checks for valid path
            fpath = re.match(r'RCPT(.+)TO:(\s*)<([\+/\'!\?\w-]+)@([\D.]+)>', receipt)

            if receipt[:7] == 'Subject':
                receipt = 'DATA'
                _bool = False
                continue

            if _bool is False:
                if check:
                    break

                if check2:
                    connectionSocket.encode('503 Bad sequence of commands')
                    continue
            if not rcpt:
                connectionSocket.encode('501 Syntax error in parameters or arguments')
                continue
            elif not fpath:
                connectionSocket.encode('501 Syntax error in parameters or arguments')
                continue
            else:
                _bool = False
                # make save names from recipients
                name_of_file = receipt.replace("RCPT TO: ", "")
                name_of_file = name_of_file.strip('>')
                name_of_file = name_of_file.split('@', 1)[-1]
                to = receipt.replace("RCPT TO: ", "")
                rcpt_list.append(to)
                save_name = os.path.join(save_path, name_of_file)
                if not os.path.exists(save_path):
                    os.makedirs(save_path)
                file1 = open(save_name, "a")
                to_list.append(file1)

                connectionSocket.encode('250 OK')
                continue
        # write From and To in files
        '''for files in to_list:
            file1 = files
            size = len(rcpt_list)
            file1.write(From + "\n")
            file1.write("To: ")
            for rcpt in rcpt_list:
                size = size - 1
                if size is 0:
                    file1.write(rcpt + "\n")
                else:
                    file1.write(rcpt + ", ")'''


        while boolean:
            if not check:
                # receive DATA cmd 
                datacmd = connectionSocket.decode(1024)
                print(datacmd)
                check = re.match(r'DATA', datacmd)

            if not check:
                connectionSocket.encode('500 Syntax error: command unrecognized')
                continue
            else:
                connectionSocket.encode('354 Start mail input; end with <CRLF>.<CRLF>')
            
            while boolean:
                # receive msg until QUIT      
                data = connectionSocket.decode(1024)
                print(data)
                if data == '.':
                    connectionSocket.encode('250 OK')
                    boolean = False
                
                    for files in to_list:
                        file1 = files
                        file1.close()

                    quitCmd = connectionSocket.decode(1024)
                    print(quitCmd)
                    if re.match(r'QUIT', quitCmd):
                        connectionSocket.encode('221 Bye')
                        boolean = False
                        break

                else:
                    connectionSocket.encode(data)
                    for files in to_list:
                        file1 = files
                        file1.write(data + "\n")
                        continue
