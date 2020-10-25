import os, discord, json
from discord.ext import commands

discordToken = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = 'b!')

@client.event
async def on_ready():
    print('Bot is ready!')

# Insert events here
@client.event
async def on_message(message):
    if message.content == "b!help" and message.channel.id == 764982805427912705:
        embed = discord.Embed(
            description = "This is a help page that includes available commands. Expect to see more added soon.\n",
            color = 9425531
        )
        embed.set_author(
            name="Help & Commands",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/embed/avatars/0.png"
        )
        embed.add_field(
            name="`b!help`",
            value="Prints this help field"
        )

        await message.channel.send(content=None, embed=embed)

client.run(discordToken)
