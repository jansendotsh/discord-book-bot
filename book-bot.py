import os, discord
from discord.ext import commands

discordToken = os.getenv('DISCORD_TOKEN')

client = commands.Bot(command_prefix = 'b!')
client.remove_command('help')

@client.event
async def on_ready():
    print('Bot is ready!')

async def checkChannel(ctx):
    if ctx.message.channel.id != 764982805427912705:
        await ctx.message.channel.send("Wrong channel <:dabguy:742894389935997070> Go to <#764982805427912705>")
    else:
        return ctx.message.channel.id == 764982805427912705

# Insert events here
@client.command()
@commands.check(checkChannel)
async def help(ctx):
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

        await ctx.message.channel.send(content=None, embed=embed)

client.run(discordToken)
