import socket
import select
from thread import *
import sys
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			#Creating socket for TCP connection
server.bind(('127.0.0.1', 25000))						#Binding self IP to socket

server.listen(100)								#Listening for incoming connections

print("Server has started")

list_of_clients = dict ()							#Dictionary to maintain details of clients
block_list = dict()								#Dictionary to maintain list of blocked clients


#Creating function for threading cleints
def clientthread(conn, addr):
	sentence = ("Welcome to DUMB DUO CHAT EXTREMO!")
	conn.send(sentence.encode('utf-8'))

	while True:
		try:	
			message = conn.recv(2048).decode('utf-8')
			if (message):		
				#Checking message for any Functions		
				if message[0] == "\\":
					#Check which kind of command has been issued by client
					c_check(conn, addr, message[1:])		
				
				#Otherwise sending message to all clients and printing on console
				else: 
					#Displaying message in required format
					message_to_send = list_of_clients[addr[1]][0] + ": " + message

					print (message_to_send)
	
					#Sending message to all clients
					broadcast(message_to_send, conn, addr)
			
			#If connection is broken, remove client from list
			else:
				remove(addr)
		except:
			continue
			

#Function to broadcast message to all clients
def broadcast(message, connection, addr):
	for clients in list_of_clients:

		#Message should not be resent to the one sending it
		if list_of_clients[clients][1]!=connection:

			#Checking if receiver has blocked anyone
			if list_of_clients[clients][0] not in block_list:
				try:
					list_of_clients[clients][1].send(message)
				except:
					list_of_clients[clients][1].close()
					remove(list_of_clients[clients])

			#Checking if the sender is in the blocked list of receiver and sending to the rest of clients
			elif list_of_clients[addr[1]][0] not in block_list[list_of_clients[clients][0]]:
				try:
					list_of_clients[clients][1].send(message)
				except:
					list_of_clients[clients][1].close()
					remove(list_of_clients[clients])

#Function to broadcast the file to everyone, same as above except the "sendall" command used to send all data using max buffersize.
def broadcast_file(message, connection, addr):
	for clients in list_of_clients:
		if list_of_clients[clients][1]!=connection:
			if list_of_clients[clients][0] not in block_list:
				try:
					list_of_clients[clients][1].sendall(message)
				except:
					list_of_clients[clients][1].close()
					remove(list_of_clients[clients])
			elif list_of_clients[addr[1]][0] not in block_list[list_of_clients[clients][0]]:
				try:
					list_of_clients[clients][1].sendall(message)
				except:
					list_of_clients[clients][1].close()
					remove(list_of_clients[clients])

#Function to remove a client from client list
def remove(addr):
	list_of_clients.pop(addr[1])


#Function to check which command has been issued by client
def c_check(conn, addr, message):
	temp = message.split("\\")
	if temp[0] == "name":
		c_name(conn, addr, temp)

	elif temp[0] == "sleep":
		c_sleep(conn, addr, temp)
	
	elif temp[0] == "block":
		c_block(addr, temp)

	elif temp[0] == "unblock":
		c_unblock(addr, temp)

	elif message == "file":
		fileReceive(conn, addr)

	elif message == "quit\n":
		print(list_of_clients[addr[1]][0] + " has disconnected.")
		broadcast(list_of_clients[addr[1]][0] + " has left the chat", conn, addr)
		remove(addr)
		conn.send("Hope you had fun! Come again soon").encode('utf-8')
		conn.close()

#Function to change name of client
def c_name(conn, addr, temp):

	#Informing client that their username has been changed
	conn.send("Changing Username from " + list_of_clients[addr[1]][0] + " to: " + temp[1])

	#Informing all other clients that their someone has changed their name
	broadcast(list_of_clients[addr[1]][0] + " is now known as: " + temp[1], conn, addr)

	name = temp[1].strip()

	#Checking if client changing name has blocked anyone and storing their block list with their new username
	if list_of_clients[addr[1]][0] in block_list:
		blk_name_list = block_list[list_of_clients[addr[1]][0]]
		block_list[name] = blk_name_list
		block_list.pop(list_of_clients[addr[1]][0])
	
	#Checking if user changing name is blocked by someone and updating their block list 
	for username in block_list:
		if list_of_clients[addr[1]][0] in block_list[username]:
			block_list[username].remove(list_of_clients[addr[1]][0])
			block_list[username].append(name)


	#Changing username of client in our cleint list
	list_of_clients[addr[1]][0] = name
	#Printing list of clients with updated username
	print(list_of_clients)
	

#Function to snooze client
def c_sleep(conn, addr, temp):
	#Receiving time to snooze
	timeout = int(temp[1])

	#Storing snoozed clients name
	username = list_of_clients[addr[1]][0]
	
	#Removing user from client list temporarily
	remove(addr)

	#Snoozing for defined time
	time.sleep(timeout)
	
	#Readding client to client list
	list_of_clients[addr[1]] = [username, conn]

	#Informing user that snooze has completed
	conn.send(str(timeout) + " seconds have elapsed :)").encode('utf-8')

#Function to add a client to block list
def c_block(addr, temp):
	#client to be blocked
	name = temp[1].strip()

	#Checking if the blocker already has a block list or not
	if list_of_clients[addr[1]][0] not in block_list:
		block_list[list_of_clients[addr[1]][0]] = [name]
	
	#If exists, appending name to be blocked in block list
	else: 
		#Checking if name to be blocked doesn't already exist in block list
		if name not in block_list[list_of_clients[addr[1]][0]]: 
			block_list[list_of_clients[addr[1]][0]].append(name)

	print(block_list)

#Function to unblock a client
def c_unblock(addr, temp):
	name = temp[1].strip()
	if list_of_clients[addr[1]][0] in block_list:
		block_list[list_of_clients[addr[1]][0]].remove(name)
	print(block_list)

#Function to receive file from user
def fileReceive(conn, addr):
	print ("Receiving File")

	filename = conn.recv(2048).decode('utf-8')
	f = open(filename, "wb")

	while True:
		data = conn.recv(4096)
		if not data:
			break
		
		#Checking for EOF and writing the rest of the data
		if "\\End" in data:
			f.write(data[:-4])
			break
		f.write(data)
	f.close()

	print ("File received\n")
	
	#Broadcasting file to all other clients
	fileSend(filename, conn, addr)

#Function to broadcast file to all clients
def fileSend(filename, conn, addr):
	print ("Sending file to all clients")

	#Informing all clients that server is going to transmit a file
	broadcast("\\file".encode('utf-8'), conn, addr)

	#Waiting for clients to get ready
	time.sleep(2)

	#Sending clients filename
	broadcast(filename.encode('utf-8'), conn, addr)

	#Waiting for clients to open file and be ready to write
	time.sleep(2)

	try:
		#Sending file data
		with open(filename , "rb") as f:
			data = f.read()
			broadcast_file(data, conn, addr)

			#informing clients of EOF
			broadcast("\\End", conn, addr)

			print("File sent to all clients\n")

		f.close()
	except:
		print("Failed to open file")
		broadcast("\\End", conn, addr)
	
#Main loop for server
while True:
	#Accepting a client tring to connect to server
	conn, addr = server.accept()
	username = conn.recv(2048).decode('utf-8')

	#Adding client to list of clients
	list_of_clients[addr[1]] = [username, conn]

	print (username + " connected")

	#Creating a new thread for every user that connects
	start_new_thread(clientthread,(conn,addr))

conn.close()
server.close()
