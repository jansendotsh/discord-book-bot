import os, discord, gspread
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials

# Discord env
discordToken = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = 'b!')
client.remove_command('help')
adminList = [176108473958924289]
bookChan = 764982805427912705

# Google Sheets env
gc = gspread.service_account(filename='key.json')
sheet = gc.open_by_key("1VoR6d3Vwbhk5sxh18jUwtSZP3hr_hBjUn2CDSmBQzus")

# Starting log
@client.event
async def on_ready():
    print('Book Bot has started')

# Checks
class wrongChannel(commands.CheckFailure):
    pass

def chanCheck():
    async def predicate(ctx):
        if ctx.message.channel.id != bookChan:
            raise wrongChannel("Wrong channel <:dabguy:742894389935997070> Go to <#764982805427912705>")
        return True
    return commands.check(predicate)

class notAdmin(commands.CheckFailure):
    pass

def adminCheck():
    async def predicate(ctx):
        if ctx.author.id not in adminList:
            raise notAdmin("You shouldn't be running this!")
        return True
    return commands.check(predicate)

# Insert events here
@client.command()
@chanCheck()
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

        `b!update`
        Updates your progress so we can track when we're all done with the book, requires either page count or percentage as argument
        _Example:_ `b!update 42%`

        `b!progress`
        Shows the progress shared by readers of the current book

        `b!access`
        Requests viewing and edit access to the Google Sheet and admin access to bot, requires a Google email address
        _Example:_ `b!add garrett@shakethedisea.se` 
        '''
    )

    await ctx.message.channel.send(content=None, embed=embed)

@help.error
async def helpErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command()
@chanCheck()
async def current(ctx):
    curBook = sheet.get_worksheet(1).get_all_records()
    embed = discord.Embed(
        description = "The current book is **{}** by **{}**. Information and downloads are available here:\n\n_Goodreads:_ \n{}\n_BookShop:_ \n{}\n_eBook Link:_ \n{}\n_Audiobook Link:_ \n{}".format(curBook[0]['Title'],curBook[0]['Author'],curBook[0]['Goodreads Link'],curBook[0]['BookShop Link'],curBook[0]['eBook Link'],curBook[0]['Audiobook Link']),
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

@current.error
async def currentErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command(name='past')
@chanCheck()
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
                value = "_Goodreads Link:_ \n{}\n_BookShop:_ \n{}\n_eBook Link:_ \n{}\n_Audiobook Link:_ \n{}".format(pastBook[i]['Goodreads Link'],pastBook[i]['BookShop Link'],pastBook[i]['eBook Link'],pastBook[i]['Audiobook Link'])
            )
    else:
        for i in range(0,len(pastBook),1):
            embed.add_field(
                name = "{} by {}".format(pastBook[i]['Title'],pastBook[i]['Author']),
                value = "_Goodreads Link:_ \n{}\n_BookShop:_ \n{}\n_eBook Link:_ \n{}\n_Audiobook Link:_ \n{}".format(pastBook[i]['Goodreads Link'],pastBook[i]['BookShop Link'],pastBook[i]['eBook Link'],pastBook[i]['Audiobook Link'])
            )
    embed.set_author(
        name="Past Books",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

@past.error
async def pastErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command()
@chanCheck()
async def next(ctx):
    upcoming = sheet.get_worksheet(0).get_all_records()
    embed = discord.Embed(
        description = "The next book is **{}** by **{}**.\n\nLinks related to this titled are available here:\n\n_Goodreads Link:_ \n{}\n_BookShop:_ \n{}\n_eBook Link:_ \n{}\n_Audiobook Link:_ \n{}\n\nIf this is incorrect, review the spreadsheet and call a vote. Spreadsheet available here:\n\nhttps://jnsn.link/bookclub".format(upcoming[0]['Title'],upcoming[0]['Author'],upcoming[0]['Goodreads Link'],upcoming[0]['BookShop Link'],upcoming[0]['eBook Link'],upcoming[0]['Audiobook Link']),
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

@next.error
async def nextErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command()
@chanCheck()
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

@add.error
async def addErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command()
@chanCheck()
@adminCheck()
async def swap(ctx):
    nextUp = sheet.get_worksheet(0).row_values(2)
    sheet.get_worksheet(1).insert_row(nextUp,2)
    sheet.get_worksheet(0).delete_rows(2)
    curBook = sheet.get_worksheet(1).get_all_records()
    progSheet = sheet.get_worksheet(2)
    progSheet.delete_rows(2,len(progSheet.get_all_records())+1)

    embed = discord.Embed(
        description = "<@&773619465811263538> It's time to start the next book!\n\nWe're now reading **{}** by **{}**. Links for this book are available here:\n\n_Goodreads Link:_ \n{}\n_BookShop:_ \n{}\n_eBook Link:_ \n{}\n_Audiobook Link:_ \n{}".format(curBook[0]['Title'],curBook[0]['Author'],curBook[0]['Goodreads Link'],curBook[0]['BookShop Link'],curBook[0]['eBook Link'],curBook[0]['Audiobook Link']),
        color = 9425531
    )
    embed.set_author(
        name="New Book Started",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )
    
    await ctx.message.channel.send(content=None, embed=embed)

@swap.error
async def swapErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)
    elif isinstance(error, notAdmin):
        await ctx.send(error)

@client.command()
@chanCheck()
async def update(ctx, progress: str):
    progSheet = sheet.get_worksheet(2)
    curBook = sheet.get_worksheet(1).get_all_records()
    pageCount = int(curBook[0]['Pages'])

    try:
        curEntry = progSheet.find(ctx.message.author.name)
        progCell = curEntry.col + 1

        if progress[-1] == "%":
            progSheet.update_cell(curEntry.row, progCell, progress)
        else:
            progress = int(progress)
            progress = str(int((progress/pageCount)*100))
            progSheet.update_cell(curEntry.row, progCell, progress+"%")

    except gspread.exceptions.CellNotFound:
        if progress[-1] == "%":
            progSheet.append_row([ctx.message.author.name, progress])
        else:
            progress = int(progress)
            progress = str(int((progress/pageCount)*100))
            progSheet.append_row([ctx.message.author.name, progress+"%"])

    embed = discord.Embed(
        description = "Congrats, {}. Your progress for **{}** by **{}** has been recorded. Everyone's progress can be viewed with `b!progress`".format(ctx.message.author.name, curBook[0]['Title'],curBook[0]['Author']),
        color = 9425531
    )
    embed.set_author(
        name="Progress Update",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

@update.error
async def updateErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

@client.command()
@chanCheck()
async def progress(ctx):
    progSheet = sheet.get_worksheet(2).get_all_records()
    curBook = sheet.get_worksheet(1).get_all_records()
    progBar = 0
    progLeft = 10

    progGroup = ""

    for i in range(0,len(progSheet),1):
        percentage = int(progSheet[i]['Progress'][:-1])
        progBar = int(percentage/10)
        progLeft = 10-progBar
        progGroup += "*{}:*\n{}{} {}\n\n".format(progSheet[i]['Username'],progBar*"█",progLeft*"░", progSheet[i]['Progress'])

    embed = discord.Embed(
        description = "Hey there :wave: Here is the progress for those reading **{}** by **{}**.".format(curBook[0]['Title'],curBook[0]['Author']),
        color = 9425531
    )
    embed.set_author(
        name="Book Progress",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )
    embed.add_field(
        name="**Current readers:**",
        value=progGroup
    )

    await ctx.message.channel.send(content=None, embed=embed)

@progress.error
async def progErr(ctx, error):
    if isinstance(error, wrongChannel):
        await ctx.send(error)

client.run(discordToken)