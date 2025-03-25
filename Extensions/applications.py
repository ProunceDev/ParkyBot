from interactions import *
from Extensions.utilities import config
import aiosqlite
import json

applications_in_progress = {}
application_temp = {}

class Applications(Extension):
	async def init_db(self):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("""
				CREATE TABLE IF NOT EXISTS applications (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					data TEXT
				)
			""")

			await db.execute("""
				CREATE TABLE IF NOT EXISTS applicants (
					user_id INTEGER PRIMARY KEY
				)
			""")

			await db.commit()

	async def has_applied(self, user_id: int) -> bool:
		async with aiosqlite.connect("applications.db") as db:
			cursor = await db.execute("SELECT 1 FROM applicants WHERE user_id = ?", (user_id,))
			row = await cursor.fetchone()
			return row is not None

	async def set_as_applied(self, user_id: int):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("INSERT OR IGNORE INTO applicants (user_id) VALUES (?)", (user_id,))
			await db.commit()

	async def get_next_application(self, current_id: int):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT id, data FROM applications WHERE id > ? ORDER BY id ASC LIMIT 1", (current_id,)) as cursor:
				row = await cursor.fetchone()
				return row if row else None
			
	async def get_application_by_id(self, app_id: int):
		async with aiosqlite.connect("applications.db") as db:
			async with db.execute("SELECT id, data FROM applications WHERE id = ?", (app_id,)) as cursor:
				row = await cursor.fetchone()
				return row if row else None
	
	def build_application_embed(self, data: dict, username: str, id: str) -> Embed:
		questions = [
			"Will you be able to attend the Cave Event on March 29th at 4 PM EST?",
			"Do you accept the rules detailed in #event-signup and understand that breaking them will result in instant death and a ban from the event?",
			"Have you read the entire post in the #event-signup channel?",
			"Will you be able to accept payment via PayPal only?",
			"Do you understand that if you cannot accept payment through PayPal, you may still participate but will forfeit any prize money if you win?",
			"Do you understand that all event players must watch Parky’s stream on the day of the event to follow along as it starts?",
			"Can your PC and internet reliably run Minecraft without significant lag or crashes?",
			"Will you be a good sport if anything goes wrong during the event—whether on the player side or server side? (Issues happen often.)",
			"How old are you? (Not a dealbreaker.)",
			"Do you have a microphone? If so, do you agree to be respectful and polite to all players in the event so that Parky can use the footage?",
			"Will you accept in-game challenges or avoid them?",
			"What are you most looking forward to if you are accepted to play in the event?",
			"Do you have any PvP or survival experience that could give you an advantage in this event?"
		]

		embed = Embed(title=f"{username}'s Application", description=f"Reviewing application #{id}", color=0x00ff99)

		for i, question in enumerate(questions, start=1):
			answer = data.get(str(i), "N/A")
			embed.add_field(name=f"{i}. {question}", value=str(answer), inline=False)

		return embed
	
	@slash_command(
		name="view_applications",
		description="Send the application viewer embed."
	)
	async def view_applications(self, ctx: SlashContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		if role in ctx.author.roles:
			current_id = int(config.get_setting("current_application_id", "0"))

			next_app = await self.get_next_application(current_id)

			if next_app:
				current_id, data = next_app

				data = dict(json.loads(data))
				
				embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

				buttons = [
					Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
					Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept")
				]

				await ctx.send(embed=embed, components=buttons)

			else:
				await ctx.send(
					embed=Embed(
						"No more applications to view!",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@component_callback("application_deny")
	async def deny_button(self, ctx: ComponentContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		if role in ctx.author.roles:
			application_id = int(ctx.message.embeds[0].description.split("#")[1])

			await ctx.channel.send(embed=Embed(f"Denied application #{application_id}", "Sending next application", 0xFF0000))
			await ctx.message.delete()
			current_id = int(config.get_setting("current_application_id", "0"))

			next_app = await self.get_next_application(current_id)

			if next_app:
				current_id, data = next_app

				config.set_setting("current_application_id", str(current_id))

				data = dict(json.loads(data))
				embed = Embed(
					title="Application Viewer",
					description=f"Reviewing application #{current_id}",
					color=0x3498db
				)

				embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

				buttons = [
					Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
					Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept")
				]

				await ctx.channel.send(embed=embed, components=buttons)

			else:
				await ctx.channel.send(
					embed=Embed(
						"No more applications to view!",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@component_callback("application_accept")
	async def accept_button(self, ctx: ComponentContext):
		await ctx.defer()
		role = ctx.guild.get_role(config.get_setting("staff_role_id", ""))
		if role in ctx.author.roles:
			application_id = int(ctx.message.embeds[0].description.split("#")[1])

			await ctx.channel.send(embed=Embed(f"Accepted application #{application_id}", "Sending next application", 0x00FF00))
			await ctx.message.delete()

			current_app = await self.get_application_by_id(application_id)

			if current_app:
				current_id, data = current_app

				data = dict(json.loads(data))

				current_event_role_id = int(config.get_setting("current_event_role_id"))

				current_event_role = await ctx.guild.fetch_role(current_event_role_id)

				application_member = await ctx.guild.fetch_member(data.get("0", {"id":1170232393752387696})["id"])

				try:
					await application_member.add_role(current_event_role)

					embed = Embed(
							title="Application Accepted!",
							description=f"Your application in Parky Community was accepted! Make sure to check out https://discord.com/channels/1082410307474968577/1342522355884490774 for information regarding the event.",
							color=0x3498db
						)

					await application_member.send(embed=embed)
				except:
					pass

				current_id = int(config.get_setting("current_application_id", "0"))

				next_app = await self.get_next_application(current_id)

				if next_app:
					current_id, data = next_app

					config.set_setting("current_application_id", str(current_id))

					data = dict(json.loads(data))
					embed = Embed(
						title="Application Viewer",
						description=f"Reviewing application #{current_id}",
						color=0x3498db
					)

					embed = self.build_application_embed(data, data.get("0", {"name":"N/A"})["name"], str(current_id))

					buttons = [
						Button(style=ButtonStyle.DANGER, label="Deny", custom_id="application_deny"),
						Button(style=ButtonStyle.SUCCESS, label="Accept", custom_id="application_accept")
					]

					await ctx.channel.send(embed=embed, components=buttons)

				else:
					await ctx.channel.send(
						embed=Embed(
							"No more applications to view!",
							"",
							0xFF0000
						)
					)
			
			else:
				await ctx.channel.send(
					embed=Embed(
						"Invalid application.",
						"",
						0xFF0000
					)
				)
		else:
			await ctx.send(
				embed=Embed(
					"No permission!",
					"You can't run this command without the Staff role.",
					0xFF0000
				)
				, ephemeral=True
			)

	@listen()
	async def on_message_create(self, event):
		message: Message = event.message

		if message.author.bot:
			return

		if message.guild is not None:
			return
		
		application_progress_index = applications_in_progress.get(message.author.id, 0)
		if message.content == "!cancel":
			if application_progress_index > 0:
				await message.channel.send("Application canceled.")
				applications_in_progress[message.author.id] = 0
				return
			else:
				await message.channel.send("You are not actively applying.")
				return
		if message.content != "!apply" and application_progress_index < 1:
			if await self.has_applied(message.author.id):
				await message.channel.send("You've already applied for this event, we will contact you if you are accepted. ( Make sure your dm’s are open. )")
				return
			else:
				await message.channel.send("If you are trying to apply for an event, type **!apply** to start, and **!cancel** at any time to cancel.")
				return
		
		if message.content == "!apply" and application_progress_index > 0:
			await message.channel.send("You've already applied for this event.")
			return
		
		if message.content == "!apply" and application_progress_index == 0:
			if await self.has_applied(message.author.id):
				await message.channel.send("You've already applied for this event, we will contact you if you are accepted. ( Make sure your dm’s are open. )")
				return
			else:
				await message.channel.send('The application process has started, it should take about 10 minutes, say "Ready", when you are ready to start, then be ready to answer each question as they come.')
				application_temp[message.author.id] = {0: {"name": message.author.display_name, "id": message.author.id}}
				applications_in_progress[message.author.id] = 1
				return
		
		if message.content.lower() != "ready" and application_progress_index == 1:
			await message.channel.send("Not ready, canceling...")
			return
		
		elif message.content.lower() == "ready" and application_progress_index == 1:
			await message.channel.send("**( 1 / 13 )** Will you be able to attend the Cave Event on <t:1743278400:F>?")
			applications_in_progress[message.author.id] = 2
			return
		
		if application_progress_index == 2:
			application_temp[message.author.id][1] = message.content
			await message.channel.send("**( 2 / 13 )** Do you accept the rules detailed in https://discord.com/channels/1082410307474968577/1333108418256310363 and understand that breaking them will result in instant death and a ban from the event?")
			applications_in_progress[message.author.id] = 3

		if application_progress_index == 3:
			application_temp[message.author.id][2] = message.content
			await message.channel.send("**( 3 / 13 )** Have you read the entire post in the https://discord.com/channels/1082410307474968577/1333108418256310363 channel?")
			applications_in_progress[message.author.id] = 4
			return

		if application_progress_index == 4:
			application_temp[message.author.id][3] = message.content
			await message.channel.send("**( 4 / 13 )** Will you be able to accept payment via PayPal only?")
			applications_in_progress[message.author.id] = 5
			return

		if application_progress_index == 5:
			application_temp[message.author.id][4] = message.content
			await message.channel.send("**( 5 / 13 )** Do you understand that if you cannot accept payment through PayPal, you may still participate but will forfeit any prize money if you win?")
			applications_in_progress[message.author.id] = 6
			return

		if application_progress_index == 6:
			application_temp[message.author.id][5] = message.content
			await message.channel.send("**( 6 / 13 )** Do you understand that all event players must watch Parky’s stream on the day of the event to follow along as it starts?")
			applications_in_progress[message.author.id] = 7
			return

		if application_progress_index == 7:
			application_temp[message.author.id][6] = message.content
			await message.channel.send("**( 7 / 13 )** Can your PC and internet reliably run Minecraft without significant lag or crashes?")
			applications_in_progress[message.author.id] = 8
			return

		if application_progress_index == 8:
			application_temp[message.author.id][7] = message.content
			await message.channel.send("**( 8 / 13 )** Will you be a good sport if anything goes wrong during the event—whether on the player side or server side? (Issues happen often.)")
			applications_in_progress[message.author.id] = 9
			return

		if application_progress_index == 9:
			application_temp[message.author.id][8] = message.content
			await message.channel.send("**( 9 / 13 )** How old are you? (Not a dealbreaker.)")
			applications_in_progress[message.author.id] = 10
			return

		if application_progress_index == 10:
			application_temp[message.author.id][9] = message.content
			await message.channel.send("**( 10 / 13 )** Do you have a microphone? If so, do you agree to be respectful and polite to all players in the event so that Parky can use the footage?")
			applications_in_progress[message.author.id] = 11
			return

		if application_progress_index == 11:
			application_temp[message.author.id][10] = message.content
			await message.channel.send("**( 11 / 13 )** Will you accept in-game challenges or avoid them?")
			applications_in_progress[message.author.id] = 12
			return

		if application_progress_index == 12:
			application_temp[message.author.id][11] = message.content
			await message.channel.send("**( 12 / 13 )** What are you most looking forward to if you are accepted to play in the event?")
			applications_in_progress[message.author.id] = 13
			return

		if application_progress_index == 13:
			application_temp[message.author.id][12] = message.content
			await message.channel.send("**( 13 / 13 )** Do you have any PvP or survival experience that could give you an advantage in this event?")
			applications_in_progress[message.author.id] = 14
			return

		if application_progress_index == 14:
			application_temp[message.author.id][13] = message.content
			await message.channel.send("✅ Thanks! Your application has been submitted. We’ll reach out if you're selected to participate. ( Make sure your dm’s are open. )")
			applications_in_progress[message.author.id] = 0
			await self.init_db()

			async with aiosqlite.connect("applications.db") as db:
				await db.execute(
					"INSERT INTO applications (data) VALUES (?)", (json.dumps(application_temp[message.author.id]), )
				)
				await db.commit()

			await self.set_as_applied(message.author.id)
			return

