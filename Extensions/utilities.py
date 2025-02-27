import os
import requests

from constants import *
from interactions import *

from settings import SettingsManager
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

config = SettingsManager("config.json")
bot = Client(debug_scope=config.get_setting("guild_id", ""), intents=Intents.ALL, token=TOKEN)

class Utilities(Extension):
	pass

def create_embed(title, description, color=0xFFFFFF):
		return Embed(title=title, description=description, color=color)
	
def get_minecraft_account(username):
	url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
	response = requests.get(url)

	if response.status_code == 200:
		data = response.json()
		return data.get("id"), data.get("name")
	else:
		return None, None

def is_valid_uuid(uuid):
	"""Check if the UUID is a valid 32-character hex string"""
	import re
	return bool(re.fullmatch(r"^[a-fA-F0-9]{32}$", uuid))