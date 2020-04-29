# Virtual-ChatRoom
Computer Networking Project - Virtual Chat


The project here implements a virtual chat room that incorporates two roles, a chat server and a client interacting to lead a conversation.
The server in this chat room acts pretty much like a moderator in real life conferences, handling almost all of the functionality implemented. 
The chat room enables a one to many relationship, allowing multiple clients to connect to a single server and converse with each other. 
The conversation includes sending of text messages along with all kinds of digital data in the form of files, over the chat room network.


The conversation in this chat room begins by invoking a TCP connection among all available clients and the server. 
The clients, identified by unique port numbers, send messages to the server which are then broadcasted to all of the unblocked clients for the original sender. 
The server thus maintains a record of all the connected clients and clients blocked by each client, to ensure message transmission to only those clients the original sender wants to send to.  
All of the required functionality has been implemented at the server side through a modular approach by defining functions and invoking them at the required time.
The functions defined include functions for:
1.	Change of client’s name
2.	Blocking a client
3.	Unblocking a client
4.	Sleep time
5.	Quit chat 
6.	Sending any type of file


All of the functions defined are invoked by another function that reads the format of the message received by the server and identifies the command issued.
After the identification of the command, respective function is then called, and command is processed.
