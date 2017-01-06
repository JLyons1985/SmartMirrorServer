#!/usr/bin/python3

#*************************************************************************
# Copyright 2016 Joshua Lyons
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Project File: MasterServer.py
# Project Description: Creates a threaded master server that listens for
#   requests from the smart mirror, dial server, and more.
# @author Joshua Lyons (josh@lyonsdensoftware.com)
# @version 0.0.1
#*************************************************************************/

### Imports
import socket
import sys
from UDPHandler import *
import serverConfig
import cv2

# Load the model data for recog
print("Loading Model data")
model = cv2.face.createFisherFaceRecognizer()
model.load(serverConfig.TRAINING_FILE)

# Server
print("Starting server")
HOST = serverConfig.MASTER_SERVER_IP
PORT = serverConfig.MASTER_SERVER_PORT

# Create the UDP Socket
try:
    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #socket.setblocking(false)
    print("Socket Created")
except:
    print("Failed to create socket.")
    sys.exit()

# Bind socket to local host and port
try:
    socket.bind((HOST, PORT))
except:
    print("Bind failed.")
    sys.exit()
    
print("Socket bind complete.")

# Now keep talking to clients

while 1:

    # Receive data from client (data, addr)
    d = socket.recvfrom(1024)
    data = str(d[0], "utf-8")
    addr = d[1]

    # Print to the server who made a connection.
    print("{} wrote:".format(addr))
    print(data)
        
    # Now have our UDP handler handle the data
    myUDPHandler = MyUDPHandler()
    myResponse = myUDPHandler.handle(data, model)

    # Respond back
    print(myResponse)
    socket.sendto(bytes(myResponse, 'utf-8'), addr)
    
socket.close()
