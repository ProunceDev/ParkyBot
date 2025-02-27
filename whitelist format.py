# Example custom format file (whitelist.txt)
# [Discord ID               |Discord Username         |Minecraft UUID           |Minecraft Username       ]
# [-------------------------|-------------------------|-------------------------|-------------------------]
# |123456789                |ExampleUser              |abcdef123456             |Steve                    |
# |987654321                |AnotherUser              |654321abcdef             |Alex                     |

# Python parser for the custom format

def load_users(filename="whitelist.txt"):
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

def save_users(users, filename="whitelist.txt"):
	with open(filename, 'w') as file:
		file.write(f"[{"Discord ID":<40}|{"Discord Username":<40}|{"Minecraft UUID":<40}|{"Minecraft Username":<40}]\n")
		file.write("[----------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------]\n")
		for user in users:
			file.write(f"|{user[0]:<40}|{user[1]:<40}|{user[2]:<40}|{user[3]:<40}|\n")

def add_user(user, filename="whitelist.txt"):
	users = load_users(filename)
	if user not in users:
		users.append(user)
		save_users(users, filename)

def remove_user(user, filename="whitelist.txt"):
	users = load_users(filename)
	if user in users:
		users.remove(user)
		save_users(filename, users)

# Example usage
if __name__ == "__main__":
	users_data = [
		["123456789", "ExampleUser", "abcdef123456", "Steve"],
		["987654321", "AnotherUser", "654321abcdef", "Alex"]
	]

	save_users(users_data)
	loaded_users = load_users()
	print(loaded_users)