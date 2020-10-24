import os
import discord

discordToken = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# Insert events here

client.run(discordToken)