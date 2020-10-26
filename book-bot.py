import os, discord, gspread
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

# Discord env
discordToken = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = 'b!')
client.remove_command('help')

# Google Sheets env
gc = gspread.service_account(filename='key.json')
sheet = gc.open_by_key("1VoR6d3Vwbhk5sxh18jUwtSZP3hr_hBjUn2CDSmBQzus")

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
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )
    embed.add_field(
        name="**Commands:**",
        value='''
        `b!help`
        Prints this help field
        
        `b!current`
        See the current book along with information and related links
        
        `b!next`
        Displays the next book along with information for calling a vote if not accurate
        
        `b!past`
        Shows the past books read, requires a number of books to show
        _Example:_ `b!past 3`

        `b!add`
        Add a book to the upcoming list for consideration, requires a title and author
        If longer than a single word, wrap in quotes to keep clean
        _Example:_ `b!add "Cujo" "Stephen King"`
        '''
    )
    await ctx.message.channel.send(content=None, embed=embed)

@client.command()
@commands.check(checkChannel)
async def current(ctx):
    curBook = sheet.get_worksheet(1).get_all_records()
    embed = discord.Embed(
        description = "The current book is **{}** by **{}**. Information and downloads are available here:\n\n**Goodreads:** {}\n**eBook Link:** {}\n**Audiobook Link:** {}".format(curBook[0]['Title'],curBook[0]['Author'],curBook[0]['Goodreads Link'],curBook[0]['eBook Link'],curBook[0]['Audiobook Link']),
        color = 9425531
    )
    embed.set_author(
        name="Current Book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

@client.command()
@commands.check(checkChannel)
async def past(ctx, length: int):
    pastBook = sheet.get_worksheet(1).get_all_records()
    embed = discord.Embed(
        description = "These were the most recent (including current) books from outer space:",
        color = 9425531
    )
    if len(pastBook) >= length:
        for i in range(0,length,1):
            embed.add_field(
                name = "{} by {}".format(pastBook[i]['Title'],pastBook[i]['Author']),
                value = "Goodreads Link: {}\neBook Link: {}\nAudiobook Link: {}".format(pastBook[0]['Goodreads Link'],pastBook[0]['eBook Link'],pastBook[0]['Audiobook Link'])
            )
    else:
        for i in range(0,len(pastBook),1):
            embed.add_field(
                name = "{} by {}".format(pastBook[i]['Title'],pastBook[i]['Author']),
                value = "Goodreads Link: {}\neBook Link: {}\nAudiobook Link: {}".format(pastBook[0]['Goodreads Link'],pastBook[0]['eBook Link'],pastBook[0]['Audiobook Link'])
            )
    embed.set_author(
        name="Past Books",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

@client.command()
@commands.check(checkChannel)
async def next(ctx):
    upcoming = sheet.get_worksheet(0).get_all_records()
    embed = discord.Embed(
        description = "The next book is **{}** by **{}**.\n\nIf this is incorrect, review the spreadsheet and call a vote. Spreadsheet available here:\n\nhttps://jnsn.link/bookclub".format(upcoming[0]['Title'],upcoming[0]['Author']),
        color = 9425531
    )
    embed.set_author(
        name="Next Book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

@client.command()
@commands.check(checkChannel)
async def add(ctx, title: str, author: str):
    sheet.get_worksheet(0).append_row([title, author])
    embed = discord.Embed(
        description = "The following book has been added:\n\n**{}** by **{}**\n\nThis can be verified here: https://jnsn.link/bookclub".format(title, author),
        color = 9425531
    )
    embed.set_author(
        name="Added Book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

client.run(discordToken)
