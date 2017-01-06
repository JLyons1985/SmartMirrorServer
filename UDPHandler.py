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
# Project File: ClientHandler.py
# Project Description: Handles the connections to the MasterServer.
#   sends the commands and requests to the appropriate place.
# @author Joshua Lyons (josh@lyonsdensoftware.com)
# @version 0.0.1
#*************************************************************************/

import select
import socket
import json
import sys
import threading
import serverConfig
import GoogleCalendar
import SpeechToText
import train
import capturepositives
import RecognizeFace
from forismatic import Forismatic

MIRROR_PORT = serverConfig.MIRROR_PORT
MIRROR_IP = serverConfig.MIRROR_IP

class MyUDPHandler:

    def send(self, msg, ip, port):
        # Create the socket
        try:
            sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                
        except sendSocket.error:
            print(" Error creating socket. Msg: {}")
            error = True
            Msg = 'Unable to send message to the mirror.'
            return Msg, error

        try:
            sendSocket.sendto(bytes(msg, 'utf-8'), (ip, port))
        except sendSocket.error:
            print(" Error sending message. Msg: {}")
            error = True
            Msg = 'Unable to send message to the mirror.'
            return Msg, error

        Msg = 'OK'
        error = False
        return Msg, error

    def handle(self, data, model):
        myData = json.loads(data)
        error = False
        Msg = ''

        print(json.dumps(myData))

        # Determine who we need to send
        if myData['To'] == 'YouTube':

            # Send the data to the mirror
            print(" Sending data to the mirror...")
            Msg, error = self.send(json.dumps(myData), MIRROR_IP, MIRROR_PORT)

        elif myData['To'] == 'Calendar':

            # Get the calendar request and send back
            calendarStr = GoogleCalendar.getCalendarItems(myData['ItemsToGet'])

            # Send the calendar items
            Msg, error = self.send(calendarStr, MIRROR_IP, MIRROR_PORT)

        elif myData['To'] == 'Speech':

            # Get the calendar request and send back
            speechStr = SpeechToText.get_speech_to_text()

            # Send the calendar items
            Msg, error = self.send(speechStr, MIRROR_IP, MIRROR_PORT)

        elif myData['To'] == 'FaceRecognition':

            # Check to see if we should train new images
            if myData['Command'] == 'Train':
                # Train the images
                train.train()
                # Send back saying training complete
                Msg, error = self.send(json.dumps({
                    'To': 'Mirror',
                    'From': 'FaceRecognition',
                    'Program': 'FaceRecognition',
                    'Msg': 'Face recognition has been trained.'
                }), MIRROR_IP, MIRROR_PORT)

            elif myData['Command'] == 'CaptureImage':

                # Capture a new image
                capturepositives.captureImage()
                # Send back saying training complete
                Msg, error = self.send(json.dumps({
                    'To': 'Mirror',
                    'From': 'FaceRecognition',
                    'Program': 'FaceRecognition',
                    'Msg': 'Image has been captured.'
                }), MIRROR_IP, MIRROR_PORT)

            elif myData['Command'] == 'RecognizeFace':
                # Grab the face
                print("About to grab an image capture...")
                face = RecognizeFace.recognizeFace(model)
                # Send back saying training complete
                Msg, error = self.send(json.dumps({
                    'To': 'Mirror',
                    'From': 'FaceRecognition',
                    'Program': 'FaceRecognition',
                    'Command': 'RecognizeFace',
                    'Msg': face
                }), MIRROR_IP, MIRROR_PORT)

        elif myData['To'] == 'Quotes':
            f = Forismatic()

            # Getting Quote object & printing quote and author
            q = f.get_quote()

            Msg, error = self.send(json.dumps({
                'To': 'Mirror',
                'From': 'Quotes',
                'Program': 'Quotes',
                'Msg': {'quote': q.quote, 'author': q.author}
            }), MIRROR_IP, MIRROR_PORT)

        else:

            # Nobody to send to print the data
            print(myData)
            error = True
            Msg = 'Do not know who to send the data to.'

        # Check if error recieved
        if error :
            ResponseStr = json.dumps({ 'Response': 'Error', 'Msg': Msg })
        else:
            ResponseStr = json.dumps({ 'Response': 'OK', 'Msg': Msg })
                                     
        response = ResponseStr
        
        return response
