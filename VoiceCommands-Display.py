# Imports
import sys
import os
import socketlib

# Setup
port = int(sys.argv[2])
server = socketlib.server()

# Functions
def renderCommandList():
    os.system('cls') # Clear console
    for i in command_list:
        print (i)
def serverCallback(conn, data):
    try:
        print ('Recieved data')
        data = data.decode('UTF-8')
        global command_list
        if data[0] == '⌘':
            if data.startswith('⌘delete_') and len(command_list) > 0:
                if data == '⌘delete_last':
                    command_list.pop()
                elif data == '⌘delete_first':
                    command_list.pop(0)
            elif data == '⌘stop_server':
                conn.sendall(bytes('recieved', 'UTF-8'))
                return False
            elif data == '⌘fix':
                print ('FIX')
                conn.sendall(bytes('recieved', 'UTF-8'))
        else:
            command_list.append(data)
        conn.sendall(bytes('recieved', 'UTF-8'))
        renderCommandList()
    except Exception as e:
        print (e)
    return True

# Start server
print ('Starting server on port '+str(port)+'...')
server.createHost('', port)

# Main
command_list = []
print ('Waiting for commands')
server.listen(runOnRecieved=serverCallback)
