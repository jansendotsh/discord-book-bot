import os, discord, mysql.connector, socket, time, asyncio
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
    upvote = '👍'
    downvote = '👎'
    emojis = [upvote, downvote]

    embed = discord.Embed(
        description = "   ",
        color = 9425531
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
    msg = await ctx.message.channel.send(content=None, embed=embed)

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
            await msg.edit(embed=embed)
            await msg.add_reaction(upvote)
            await msg.add_reaction(downvote)

        except:
            embed.clear_fields()
            embed.add_field(
                name="Search results:",
                value="No results found. Please try your search again.\n\n**Tip:** Make sure your search works on [Goodreads](https://www.goodreads.com/) as that's the source for books."
            )
            await msg.edit(embed=embed)
    
    await grSearch(b)

    def check(reaction, user):
        return user == ctx.message.author

    while emojis:
        try:
            res = await client.wait_for(event='reaction_add', timeout=60.0, check=lambda reaction, user: user == ctx.message.author)
            if res:
                reaction, user = res
                emojis = [e for e in emojis if e != reaction]
                if reaction.emoji == upvote:                    
                    embed.clear_fields()
                    embed.add_field(
                        name="Added to upcoming books",
                        value="You can view upcoming books here..."
                    )
                    await msg.edit(embed=embed)
                    await msg.clear_reactions()
                    break
                if reaction.emoji == downvote:                    
                    b += 1
                    await grSearch(b)
                    await msg.remove_reaction(downvote, ctx.message.author)

        except asyncio.TimeoutError:
            embed.clear_fields()
            embed.add_field(
                name="Search results:",
                value="*Search timed out awaiting your response. Please try again.*"
            )
            await msg.edit(embed=embed)
            await msg.clear_reactions()
    
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