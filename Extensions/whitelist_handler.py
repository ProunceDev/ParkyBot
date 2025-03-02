# Example custom format file (players.list)
# [Discord ID               |Discord Username         |Minecraft UUID           |Minecraft Username       ]
# [-------------------------|-------------------------|-------------------------|-------------------------]
# |123456789                |ExampleUser              |abcdef123456             |Steve                    |
# |987654321                |AnotherUser              |654321abcdef             |Alex                     |

# Python parser for the custom format

from interactions import *

class Whitelist(Extension):
	pass

def load_users(filename="players.list"):
	users = []
	with open(filename, 'r') as file:
		lines = file.readlines()
		for line in lines:
			if line.startswith("[") or "|" not in line:
				continue
			parts = [part.strip() for part in line.split("|") if part.strip()]
			if len(parts) == 4:
				users.append(parts)
	return users

def save_users(users, filename="players.list"):
	with open(filename, 'w') as file:
		file.write(f"[{"Discord ID":<40}|{"Discord Username":<40}|{"Minecraft UUID":<40}|{"Minecraft Username":<40}]\n")
		file.write("[----------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------]\n")
		for user in users:
			file.write(f"|{user[0]:<40}|{user[1]:<40}|{user[2]:<40}|{user[3]:<40}|\n")

def add_user(new_user, filename="players.list"):
    users = load_users(filename)
    for user in users:
        if user[2] == new_user[2]:
            return False  # UUID already exists
    users.append(new_user)
    save_users(users, filename)
    return True

def remove_user(minecraft_uuid, filename="players.list"):
    users = load_users(filename)
    users = [user for user in users if user[2].replace("-", "") != minecraft_uuid]
    save_users(users, filename)
    return True
	
def get_number_of_whitelisted_users(discord_id, filename="players.list"):
	total = 0
	users = load_users(filename)
	for user in users:
		if int(user[0]) == int(discord_id):
			total+=1
	return total

def create_user(discord_id, discord_username, minecraft_uuid, minecraft_username):
	return [str(discord_id), str(discord_username), str(minecraft_uuid), str(minecraft_username)]