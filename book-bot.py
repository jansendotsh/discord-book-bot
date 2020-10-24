import os
import discord

discordToken = os.getenv('DISCORD_TOKEN')

client = discord.client()

# Insert events here

client.run(discordToken)