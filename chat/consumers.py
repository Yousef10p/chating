from datetime import datetime
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'mywebsite.settings')
django.setup()


import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message
from django.contrib.auth.models import User



from channels.db import database_sync_to_async

# Create a method to save messages
@database_sync_to_async
def save_message(sender, receiver, content):
    print("saving to DB")
    return Message.objects.create(sender=sender, receiver=receiver, content=content)





class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.receiver = self.scope['url_route']['kwargs']['username']
        
        # Check if the user is authenticated
        if self.user.is_authenticated:
            sorted_users = sorted([self.user.username, self.receiver])
            self.room_group_name = f"chat_{sorted_users[0]}_{sorted_users[1]}"
            
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
            print("group created successfully", self.room_group_name)
        else:
            # Reject the connection if not authenticated
            self.close()
            print("Connection rejected, user is not authenticated.")
    
    
    #method is called whenever the server receives a message from the WebSocket client. It handles receiving and broadcasting the message to the appropriate group
    def receive(self, text_data):#text_data: This is the raw data received from the WebSocket client (typically in JSON format).
        data = json.loads(text_data)#converts the JSON-formatted string into a Python dictionary.
        message = data['message']#exteracting message from the dictonary
        print("messgae: ",message,"\ntrying to save")
        
        receiver_user = User.objects.get(username=self.receiver)
        async_to_sync(save_message)(self.user, receiver_user, message)


        async_to_sync(self.channel_layer.group_send)(#sending message to group
            self.room_group_name,
            {
                'type':'chat_message',#this trigger an event of type chat_message which must be defined in this file consumer.py
                'message':message,
                'sender':self.user.username
            }

        )
        
    
    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'timestamp':timestamp
            
        }))
        
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
    )
        
       