import os, discord, mysql.connector, socket, time, csv, asyncio
from discord.ext import commands
from oauth2client.service_account import ServiceAccountCredentials
from goodreads import client as gcclient

# Wait for database response
def isOpen(ip,port):
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   try:
      s.connect((ip, int(port)))
      s.shutdown(2)
      return True
   except:
      return False

while isOpen("db",3306) == False:
    print("Database unavailable")
    time.sleep(1)

# MySQL data source
bookdb = mysql.connector.connect(
    host="db",
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE')
)

cursor = bookdb.cursor()

# Discord env
discordToken = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = 'beta!')
client.remove_command('help')
adminList = [176108473958924289]
bookChan = 764982805427912705
upvote = '👍'
downvote = '👎'

# Goodreads API
gc = gcclient.GoodreadsClient(os.getenv('GOODREADS_KEY'), os.getenv('GOODREADS_SECRET'))

# Starting log
@client.event
async def on_ready():
    print('Book Bot has started')

# Checks
## this first check has been reduced to a lambda, doesn't take additional lines and isn't complex. delete this
def check(reaction, user):
    return user == ctx.message.author

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

# Commands
## Help 
@client.command()
async def help(ctx):
    embed = discord.Embed(
        description = "This is a help page that includes available commands.\n",
        color = discord.Color.red()
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
This is a very incomplete beta and will be expanded upon in the future. 

• `b!past`
  See the current book along with information and related links
        '''
    )

    await ctx.message.channel.send(content=None, embed=embed, delete_after=60)

## Add
@client.command(name='add')
async def add(ctx, *, term):

    emojis = [upvote, downvote]

    embed = discord.Embed(
        description = "   ",
        color = discord.Color.red()
    )
    embed.set_author(
        name="This is a beta search with Goodreads API",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )
    embed.add_field(
        name="Search results:",
        value="*Currently searching for \"{}\". The search can take a moment.*".format(term)
    )
    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)

    b = 0
    bookSearch = gc.search_books(term)

    async def grSearch(b):
        try:
            title = bookSearch[b]._book_dict['title']
            grid = bookSearch[b]._book_dict['id']
            pageCount = bookSearch[b]._book_dict['num_pages']
            author = ""

            if isinstance(bookSearch[b]._book_dict['authors']['author'], list):
                for i in bookSearch[b]._book_dict['authors']['author']:
                    if i['role'] == None:
                        author += "{}, ".format(i['name'])
                    if i['role'] != None:
                        author += "{} ({}), ".format(i['name'], i['role'])

                author = author[:-2]

            elif isinstance(bookSearch[b]._book_dict['authors']['author'], dict):
                author = bookSearch[b]._book_dict['authors']['author']['name']

            embed.clear_fields()
            embed.add_field(
                name="Search results:",
                value="Here is what you sent:\n{}\n\nHere is what we found:\n**Author:** {}\n**Title:** {}\n**Goodreads ID:** {}\n**Page count:** {}\n\n**[Goodreads](https://www.goodreads.com/book/show/{})** \n**[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})** ".format(term, author, title, grid, pageCount, grid, grid)
            )
            await msg.edit(embed=embed, delete_after=60)
            await msg.add_reaction(upvote)
            await msg.add_reaction(downvote)

        except:
            embed.clear_fields()
            embed.add_field(
                name="Search results:",
                value="No results found. Please try your search again.\n\n**Tip:** Make sure your search works on [Goodreads](https://www.goodreads.com/) as that's the source for books."
            )
            await msg.edit(embed=embed, delete_after=60)
            await msg.clear_reactions()
    
    await grSearch(b)

    while emojis:
        res = await client.wait_for(event='reaction_add', check=lambda reaction, user: user == ctx.message.author)
        if res:
            reaction, user = res
            emojis = [e for e in emojis if e != reaction]
            if reaction.emoji == upvote:                    
                embed.clear_fields()
                embed.add_field(
                    name="Added to upcoming books",
                    value="You can view upcoming books here..."
                )
                await msg.edit(embed=embed, delete_after=60)
                await msg.clear_reactions()
                break
            if reaction.emoji == downvote:                    
                b += 1
                await grSearch(b)
                await msg.remove_reaction(downvote, ctx.message.author)
   
## Past books
@client.command(name='last')
async def last(ctx):
    emojis = [upvote]

    query = ("SELECT * FROM past ORDER BY id desc")
    cursor.execute(query)
    pastBook = cursor.fetchall()

    embed = discord.Embed(
        description = "This is the most recent book that have been read and discussed:",
        color = discord.Color.red()
    )
    embed.add_field(
        name = "**{}** by **{}**".format(pastBook[0][1],pastBook[0][2]),
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*\n\nDo you want a list of all previous books read and discussed?".format(pastBook[0][4],pastBook[0][4],pastBook[0][4],pastBook[0][5],pastBook[0][6])
    )
    embed.set_author(
        name="Most recent book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)
    await msg.add_reaction(upvote)

    while emojis:
        res = await client.wait_for(event='reaction_add', check=lambda reaction, user: user == ctx.message.author)
        if res:
            reaction, user = res
            emojis = [e for e in emojis if e != reaction]
            if reaction.emoji == upvote:                    
                fields = ["id","title","author","pages","goodreads_id","ebook_link","audiobook_link"]

                with open('past.csv', 'w') as f: 
                    write = csv.writer(f) 
                    write.writerow(fields)
                    write.writerows(pastBook)

                file = discord.File('past.csv', filename="past.csv")

                await ctx.message.author.send(content="Here's that spreadsheet with all previously read and discussed books", file=file)
                break

## Next book
@client.command(name='next')
async def next(ctx):
    emojis = [upvote]

    nextQuery = ("SELECT * FROM next")
    cursor.execute(nextQuery)
    nextBook = cursor.fetchall()

    embed = discord.Embed(
        description = "This is the most recent book that have been read and discussed:",
        color = discord.Color.red()
    )
    embed.add_field(
        name = "**{}** by **{}**".format(nextBook[0][1],nextBook[0][2]),
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*\n\nDo you want a list of all upcoming books?".format(nextBook[0][4],nextBook[0][4],nextBook[0][4],nextBook[0][5],nextBook[0][6])
    )
    embed.set_author(
        name="Most recent book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)
    await msg.add_reaction(upvote)

    while emojis:
        res = await client.wait_for(event='reaction_add', check=lambda reaction, user: user == ctx.message.author)
        if res:
            reaction, user = res
            emojis = [e for e in emojis if e != reaction]
            if reaction.emoji == upvote:                    
                poolQuery = ("SELECT * FROM pool")
                cursor.execute(poolQuery)
                poolBook = cursor.fetchall()

                fields = ["id","title","author","pages","goodreads_id","ebook_link","audiobook_link"]

                with open('upcoming.csv', 'w') as f: 
                    write = csv.writer(f) 
                    write.writerow(fields)
                    write.writerows(poolBook)

                file = discord.File('upcoming.csv', filename="upcoming.csv")

                await ctx.message.author.send(content="Here's that spreadsheet with all books already added to our upcoming pool for reading and discussion:", file=file)
                break

## Current book
@client.command(name='current')
async def current(ctx):
    query = ("SELECT * FROM current WHERE id = 1")
    cursor.execute(query)
    curBook = cursor.fetchall()

    embed = discord.Embed(
        description = "This is the book that we're currently reading:",
        color = discord.Color.red()
    )
    embed.add_field(
        name = "**{}** by **{}**".format(curBook[0][1],curBook[0][2]),
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*".format(curBook[0][4],curBook[0][4],curBook[0][4],curBook[0][5],curBook[0][6])
    )
    embed.set_author(
        name="Current book",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)

# Starting Discord listener
client.run(discordToken)