import os, discord, mysql.connector, socket, time
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

# Goodreads API
gc = gcclient.GoodreadsClient(os.getenv('GOODREADS_KEY'), os.getenv('GOODREADS_SECRET'))

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

# Commands
## Help 
@client.command()
async def help(ctx):
    embed = discord.Embed(
        description = "This is a help page that includes available commands.\n",
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
This is a very incomplete beta and will be expanded upon in the future. 

• `b!past`
  See the current book along with information and related links
        '''
    )

    await ctx.message.channel.send(content=None, embed=embed)

## Search
@client.command(name='search')
async def search(ctx, *, term):
    bookSearch = gc.search_books(term)
    author = ""
    title = bookSearch[0]._book_dict['title']
    grid = bookSearch[0]._book_dict['id']
    pageCount = bookSearch[0]._book_dict['num_pages']

    if isinstance(bookSearch[0]._book_dict['authors']['author'], list):
        for i in bookSearch[0]._book_dict['authors']['author']:
            if i['role'] == None:
                author += "{}, ".format(i['name'])
            if i['role'] != None:
                author += "{} ({}), ".format(i['name'], i['role'])

        author = author[:-2]

    elif isinstance(bookSearch[0]._book_dict['authors']['author'], dict):
        author = bookSearch[0]._book_dict['authors']['author']['name']

    embed = discord.Embed(
        description = "   ",
        color = 9425531
    )
    embed.add_field(
        name="Search results...",
        value="Here is what you sent:\n{}\n\nHere is what we found:\n**Author:** {}\n**Title:** {}\n**Goodreads ID:** {}\n**Page count:** {}\n\n**[Goodreads](https://www.goodreads.com/book/show/{})** \n**[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})** ".format(term, author, title, grid, pageCount, grid, grid)
    )
    embed.set_author(
        name="This is a beta search with Goodreads API",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)
    
## Past books
@client.command(name='past')
async def past(ctx):
    query = ("SELECT * FROM past ORDER BY title desc limit 1")
    cursor.execute(query)
    pastBook = cursor.fetchone()

    embed = discord.Embed(
        description = "These were the most recent books from outer space:",
        color = 9425531
    )

    embed.add_field(
        name = "Last book:",
        value = "{}".format(pastBook)
    )
    embed.set_author(
        name="Past Books",
        icon_url="https://s.jnsn.link/book/book.png"
    )
    embed.set_thumbnail(
        url="https://s.jnsn.link/book/bookmark.png"
    )

    await ctx.message.channel.send(content=None, embed=embed)

# Starting Discord listener
client.run(discordToken)