from telethon import TelegramClient
from datetime import datetime

class ClientWrapper:
    def __init__(self, phone_number, api_id, api_hash):
        self.client = TelegramClient(phone_number, api_id, api_hash)
        self.created_at = datetime.now()
        self.id = 0
        self.logged_in = False

    def get_client(self):
        return self.client

    def get_creation_time(self):
        return self.created_at

    def get_id(self):
        return self.id

    def get_logged_in(self):
        return self.logged_in

    def set_id(self, new_id):
        self.id = new_id
    
    def set_logged_in(self, state):
        self.logged_in = state
    