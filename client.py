from socket import *
import sys

while True:
    try:
        serverName = 'localhost'
        serverPort = 8080
        break
    except ValueError:
        print("Error Input")
        continue
    
serverPort = int(serverPort)
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

#check for handshake
recv = clientSocket.recv(1024).decode()
print(recv)
# '220' is a status code that signifies a successful connection to the server
if recv[:3] != '220':
    print('220 reply not received from server.')
    clientSocket.close()
    sys.exit()
    
#Send HELO command and print server response.
heloCommand = 'EHLO'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')
    clientSocket.close()
    sys.exit()

x = 0
while True:
    while True:
        inputFrom = input("From: ")
        clientSocket.encode("MAIL FROM: <" + inputFrom + ">")
        okFrom = clientSocket.decode(1024)
        print(okFrom)
        if okFrom[:3] != '250':
            print('250 reply not received from server.')
            continue
        else:
            break
    
    #input reciepient mail
    while True:
        if x == 1:
            break
        to = input("To: ")
        toList = to.split(",")
        
        for tos in toList:
            clientSocket.encode("RCPT TO: <" + tos + ">")
            okTo = clientSocket.decode(1024)
            print(okTo)
            
            def toHelper():
                if okTo[:3] != '250':
                    print('250 reply not received from server.')
                    global x
                    x = 0
                    return 
                else:
                    x = 1
                    return
            toHelper()
            if x == 0:
                break
        
    clientSocket.encode("DATA")
    okData = clientSocket.rec(1024)
    print(okData)
    if okData[:3] != '354':
        print('354 reply not received from server. Error')
    
    writeFrom = "From: " + inputFrom + "\n"
    clientSocket.encode(writeFrom)
    clientSocket.decode(1024)
    
    writeTo = "To: " + to + "\n"
    clientSocket.encode(writeTo)
    clientSocket.decode(1024)
    
    readSubject = input("Subject: ")
    clientSocket.encode("Subject: " + readSubject + "\n")
    clientSocket.decode(1024)
    
    sys.stdout.write("Message: ")
    
    while True:
        readMessage = input()
        if readMessage == ' ':
            readMessage = '\r'
        clientSocket.encodeall(readMessage)
        okEnd = clientSocket.decode(1024)
        print(okEnd)
        if okEnd[:3] != '250':
            print('250 reply not received from server.')
            continue
        else:
            clientSocket.encode("QUIT")
            quitMsg = clientSocket.decode(1024)
            if quitMsg[:3] != '221':
                print('221 reply not received from server.')
                sys.exit()
            else:
                clientSocket.close()
                exit()
        

        
        