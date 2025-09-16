from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json


class MyConsumer(WebsocketConsumer):


    def connect(self):
        self.room_name = "some_room"
        self.room_group_name = "some_group"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
  
        self.accept()
        self.send(text_data="You are connected!")

    def receive(self, text_data=None, bytes_data=None):
    
        self.send(text_data="Hello world!")

    def disconnect(self, close_code):
        pass
        