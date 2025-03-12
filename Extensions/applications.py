from interactions import *
from Extensions.utilities import config
import aiosqlite
import json

class Applications(Extension):
	async def init_db(self):
		async with aiosqlite.connect("applications.db") as db:
			await db.execute("""
				CREATE TABLE IF NOT EXISTS applications (
					id INTEGER PRIMARY KEY AUTOINCREMENT,
					data TEXT
				)
			""")
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
			
	@slash_command(
		name="apply",
		description="Apply for access to the latest event."
	)
	async def apply(self, ctx: SlashContext):
		temp_modal = Modal(
			ShortText(
				label=f"MC Username",
				custom_id="mc_username",
				placeholder="eg. Prounce, ParkyParks, etc",
			),
			ShortText(
				label=f"Age",
				custom_id="irl_age",
				placeholder="Must be 16 or older.",
			),
			title="Event Application",
			custom_id="application_submit"
		)	
			
		await ctx.send_modal(temp_modal)

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

				config.set_setting("current_application_id", str(current_id))

				data = dict(json.loads(data))
				embed = Embed(
					title="Application Viewer",
					description=f"Reviewing application #{current_id}",
					color=0x3498db
				)

				embed.add_field("Minecraft Username", data.get("mc_username", "N/A"))
				embed.add_field("Discord Username", data.get("discord_username", "N/A"))
				embed.add_field("IRL Age", data.get("irl_age", "N/A"))

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

	@modal_callback("application_submit")
	async def application_modal_answer(self, ctx: ModalContext, mc_username: str, irl_age: str):
		await ctx.defer(ephemeral=True)

		await self.init_db()

		async with aiosqlite.connect("applications.db") as db:
			await db.execute(
				"INSERT INTO applications (data) VALUES (?)", (json.dumps({"mc_username": mc_username, "irl_age": irl_age, "discord_username": ctx.user.username, "discord_id": ctx.user.id}), )
			)
			await db.commit()

		await ctx.send("Your application has been submitted!", ephemeral=True)

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

				embed.add_field("Minecraft Username", data.get("mc_username", "N/A"))
				embed.add_field("Discord Username", data.get("discord_username", "N/A"))
				embed.add_field("IRL Age", data.get("irl_age", "N/A"))

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

				application_member = await ctx.guild.fetch_member(data.get("discord_id", "1170232393752387696"))

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

					embed.add_field("Minecraft Username", data.get("mc_username", "N/A"))
					embed.add_field("Discord Username", data.get("discord_username", "N/A"))
					embed.add_field("IRL Age", data.get("irl_age", "N/A"))

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