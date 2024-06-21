from telethon import TelegramClient
from datetime import datetime

class ClientWrapper:
    def __init__(self, phone_number, api_id, api_hash):
        self.client = TelegramClient(phone_number, api_id, api_hash)
        self.created_at = datetime.now()
        self.id = 0

    def get_client(self):
        return self.client

    def get_creation_time(self):
        return self.created_at

    def get_id(self):
        return self.id

    def set_id(self, new_id):
        self.id = new_id