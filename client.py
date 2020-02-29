import socket
import select
import sys
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 		#Making socket for TCP connectino

if len(sys.argv) != 3:
	print ("Correct usage: script, Username, port number")		#Checking input in command line is in correct format
	exit()

Username = str(sys.argv[1])						#Storing username
My_Port = int(sys.argv[2])						#Storing custom port number of client
server.bind(('127.0.0.1', My_Port))					#Binding server IP to socket
server.connect(('127.0.0.1', 25000))					#Connecting to server
server.send(Username.encode('utf-8'))					#Sending server my username so that it may be stored


#Function that handles the file that needs to be sent to Server	
def filesend(temp):							
	server.send("\\file".encode('utf-8'))				#Notifying server that client is sending file
	time.sleep(2)							#Waiting for server to accept instruction and get ready

	filename = temp[2].strip()				
	server.send(filename.encode('utf-8'))				#Sending server the file name that will be transferred
	
	#Opening the file that we want to transfer
	try:
		with open(temp[2].strip(), "rb") as f:
			print ("Sending file to server")

			data = f.read()
			server.sendall(data)

			#Notifying server of EOF
			server.send("\\End")
			print("Done sending file")
		
		#closing the file after reading
		f.close()
	except:
		print("Failed to open file")
		time.sleep(2)
		server.send("\\End")

#Function that handles the file that is being received from server
def filereceive(socks):
	print ("Receiving a file")

	filename = socks.recv(2048).decode('utf-8')
	f = open(filename, "wb")

	while True:
		data = socks.recv(4096)
		if not data:
			break

		#Checking for EOF and writing the rest of the file data
		if "\\End" in data:
			f.write(data[:-4])
			break

		f.write(data)

	#Closing file after write.
	f.close()
	print ("File received")


flag = True

#Main loop for Client side chat
while flag:
	sockets_list = [sys.stdin, server]						#List of input(User input or data from server)
	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])     #Selecting socket using Select library

	for socks in read_sockets:
		#If input is from server
		if socks == server:
			message = socks.recv(2048).decode('utf-8')
			print (message)
			
			#Message to check if server has accepted our Quit function and then exiting
			if message == "Hope you had fun! Come again soon":
				flag = False
			
			#Check if server wants to send a file
			elif message == "\\file":
				filereceive(socks)
		
		#If input is from console
		else:
			#Reading input			
			message = sys.stdin.readline()

			#Checking if client wants to send a file
			temp = message.split("\\")
			if message[0] == '\\' and temp[1] == 'file':
				filesend(temp)

			#Else sending the message to server and writing it on console as well
			else:
				server.send(message.encode('utf-8'))
				sys.stdout.write("You: ")
				sys.stdout.write(message)
				sys.stdout.write("\n")
				sys.stdout.flush()

server.close()
