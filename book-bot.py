import os
import discord

discordToken = os.getenv('DISCORD_TOKEN')

client = discord.Client()

# Insert events here
@client.event
async def on_message(message):
    if message.content == "fuck":
        await message.channel.send("NOT INDOORS!")

client.run(discordToken)
