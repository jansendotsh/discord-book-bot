import os, discord, sqlite3, time, csv, asyncio, random
from discord.ext import commands
from goodreads import client as gcclient

helpPrompt='''
• `b!current`
    See the current book along with information and related links
    
• `b!next`
    Displays the next book along with information for calling a vote if not accurate, offers a spreadsheet of all books in pool

• `b!last`
    Shows the last book as part of the book club and allows downloading a spreadsheet with all prior books

• `b!add`
    Allows adding a book to the pool of potential books. Can be general search terms.
    _Example:_ `b!add Stephen King Cujo`

• `b!update`
    Updates your progress so we can track when we're all done with the book, requires either page count or percentage as argument
    _Example:_ `b!update 42%` or `b!update 220`

• `b!progress`
    Shows the progress shared by readers of the current book
'''

# sqlite3 data source
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "db/bookbot.db")
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# Discord env
discordToken = os.getenv('DISCORD_TOKEN')
client = commands.Bot(command_prefix = 'beta!')
client.remove_command('help')
adminList = [176108473958924289]
bookChan = 764982805427912705
readerRole = 773619465811263538
upvote = '👍'
downvote = '👎'
authorImg = "https://s.jnsn.link/book/book.png"
thumbnailImg = "https://s.jnsn.link/book/bookmark.png"

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
        color = discord.Color.red()
    )
    embed.set_author(
        name="Help & Commands",
        icon_url=authorImg

    )
    embed.set_thumbnail(
        url=thumbnailImg
    )
    embed.add_field(
        name="**Commands:**",
        value=helpPrompt
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
        name="Beta search via Goodreads API",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=thumbnailImg
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
            global author
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
            embed.set_thumbnail(
                url=bookSearch[b]._book_dict['small_image_url']
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

        return author
    
    await grSearch(b)

    while emojis:
        res = await client.wait_for(event='reaction_add', check=lambda reaction, user: user == ctx.message.author)
        if res:
            reaction, user = res
            emojis = [e for e in emojis if e != reaction]

            if reaction.emoji == upvote:                    
                query = ("INSERT INTO pool(title, author, goodreads_id, thumbnail, pages) VALUES (?, ?, ?, ?, ?)")
                bookAdd = (bookSearch[b]._book_dict['title'], author, bookSearch[b]._book_dict['id'], bookSearch[b]._book_dict['small_image_url'], bookSearch[b]._book_dict['num_pages'])
                cursor.execute(query, bookAdd)
                connection.commit()

                embed.clear_fields()
                embed.add_field(
                    name="Book added!",
                    value="I've added **{}** by **{}** to our pool of books for selection. \n\nYou can see the next book and request a list of the full pool of books by running `b!next`.".format(bookSearch[b]._book_dict['title'], author)
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
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*\n\nDo you want a list of all previous books read and discussed?".format(pastBook[0][3],pastBook[0][3],pastBook[0][3],pastBook[0][6],pastBook[0][7])
    )
    embed.set_author(
        name="Most recent book",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=pastBook[0][4]
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)
    await msg.add_reaction(upvote)

    while emojis:
        res = await client.wait_for(event='reaction_add', check=lambda reaction, user: user == ctx.message.author)
        if res:
            reaction, user = res
            emojis = [e for e in emojis if e != reaction]
            if reaction.emoji == upvote:                    
                fields = ["id","title","author","goodreads_id","thumbnail","pages","ebook_link","audiobook_link"]

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
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*\n\nDo you want a list of all upcoming books?".format(nextBook[0][3],nextBook[0][3],nextBook[0][3],nextBook[0][6],nextBook[0][7])
    )
    embed.set_author(
        name="Most recent book",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=nextBook[0][4]
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

                fields = ["id","title","author","goodreads_id","thumbnail","pages","ebook_link","audiobook_link"]

                with open('upcoming.csv', 'w') as f: 
                    write = csv.writer(f) 
                    write.writerow(fields)
                    write.writerows(nextBook)
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
        value = "\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*".format(curBook[0][3],curBook[0][3],curBook[0][3],curBook[0][6],curBook[0][7])
    )
    embed.set_author(
        name="Current book",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=curBook[0][4]
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)

## Progress update
@client.command(name='update')
async def update(ctx, progress: str):
    cursor.execute("SELECT * FROM current WHERE id = 1")
    curBook = cursor.fetchall()
    pageCount = curBook[0][5]

    cursor.execute("SELECT EXISTS (SELECT 1 FROM progress WHERE user = ?)", (ctx.message.author.name, ))
    progCheck = cursor.fetchone()[0]

    try:
        if progress[-1] == "%" and int(progress[:-1])<=100:
            progress = int(progress[:-1])
            embDesc = "Your progress for **{}** by **{}** has been recorded 📚\n\nEveryone's progress can be viewed with `b!progress`".format(curBook[0][1],curBook[0][2])
        elif progress[-1] != "%" and int(progress) <= pageCount:
            progress = int(progress)
            progress = str(int((progress/pageCount)*100))
            embDesc = "Your progress for **{}** by **{}** has been recorded 📚\n\nEveryone's progress can be viewed with `b!progress`".format(curBook[0][1],curBook[0][2])
        else:
            embDesc = "That's an invalid value. Please try again with a percentage under 100 (i.e. `75%`) or a valid page count (i.e. `320`)."
    except:
        embDesc = "An error occurred while updating your progress. Please try again with a percentage (i.e. `75%`)."

    if progCheck > 0:
        query = ("UPDATE progress SET progress = ? WHERE USER = ?")
        progUpdate = (progress, ctx.message.author.name)

        cursor.execute(query, progUpdate)
        connection.commit()
    else:
        query = ("INSERT INTO progress(user,progress) VALUES (?, ?)")
        progUpdate = (ctx.message.author.name, progress)

        cursor.execute(query, progUpdate)
        connection.commit()

    embed = discord.Embed(
        description = embDesc,
        color = discord.Color.red()
    )
    embed.set_author(
        name="Progress update",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=thumbnailImg
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=60)

## Progress check
@client.command(name='progress')
async def progress(ctx):
    cursor.execute("SELECT * FROM current WHERE id = 1")
    curBook = cursor.fetchall()

    progBar = 0
    progLeft = 10 
    progGroup = "\n"

    cursor.execute("SELECT user,progress FROM progress")
    progStatus = cursor.fetchall()

    for i in progStatus:
        percentage = int(i[1])
        progBar = int(percentage/10)
        progLeft = 10-progBar
        progGroup += "*{}:*\n{}{} {}%\n\n".format(i[0], progBar*"█", progLeft*"░", i[1])

    embed = discord.Embed(
        description = "Hey there 👋 Here is the progress for those reading **{}** by **{}**".format(curBook[0][1], curBook[0][2]),
        color = discord.Color.red()
    )
    embed.set_author(
        name="Progress Status",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=thumbnailImg
    )
    embed.add_field(
        name="**Current readers:**",
        value=progGroup
    )

    msg = await ctx.message.channel.send(content=None, embed=embed, delete_after=120)

## Admin: Swap current book
@client.command(name='swap')
async def swap(ctx):
    # Current >> Past
    cursor.execute("SELECT * FROM current WHERE id = 1")
    curBook = cursor.fetchall()
    query = ("INSERT INTO past(title, author, goodreads_id, thumbnail, pages, ebook_link, abook_link) VALUES (?, ?, ?, ?, ?, ?, ?)")
    pastAdd = (curBook[0][1], curBook[0][2], curBook[0][3], curBook[0][4], curBook[0][5], curBook[0][6], curBook[0][7])
    cursor.execute(query, pastAdd)
    
    # Rebuild Past
    cursor.execute("DROP TABLE current");
    cursor.execute('CREATE TABLE "current" ("id" INTEGER NOT NULL, "title" TEXT NOT NULL, "author" TEXT NOT NULL, "goodreads_id" INTEGER NOT NULL, "thumbnail" TEXT NOT NULL, "pages" INTEGER, "ebook_link" TEXT, "abook_link" TEXT, PRIMARY KEY("id" AUTOINCREMENT))')

    # Next to current
    cursor.execute("SELECT * FROM next WHERE id = 1")
    nextBook = cursor.fetchall()
    query = ("INSERT INTO current(title, author, goodreads_id, thumbnail, pages, ebook_link, abook_link) VALUES (?, ?, ?, ?, ?, ?, ?)")
    curAdd = (nextBook[0][1], nextBook[0][2], nextBook[0][3], nextBook[0][4], nextBook[0][5], nextBook[0][6], nextBook[0][7]) 
    cursor.execute(query, curAdd)

    # Rebuild Next
    cursor.execute("DROP TABLE next");
    cursor.execute('CREATE TABLE "next" ("id" INTEGER NOT NULL, "title" TEXT NOT NULL, "author" TEXT NOT NULL, "goodreads_id" INTEGER NOT NULL, "thumbnail" TEXT NOT NULL, "pages" INTEGER, "ebook_link" TEXT, "abook_link" TEXT, PRIMARY KEY("id" AUTOINCREMENT))')

    # Pool cleaning
    cursor.execute("SELECT * FROM pool")
    bookPool = cursor.fetchall()
    randoBook = bookPool[random.randint(0, int(len(bookPool)-1))]
    query = ("INSERT INTO next(title, author, goodreads_id, thumbnail, pages, ebook_link, abook_link) VALUES (?, ?, ?, ?, ?, ?, ?)")
    nextAdd = (randoBook[1], randoBook[2], randoBook[3], randoBook[4], randoBook[5], randoBook[6], randoBook[7])
    cursor.execute(query, nextAdd)
    query = ("DELETE FROM pool WHERE id = ?")
    cursor.execute(query, (randoBook[0], ))
    
    # Clear progress
    cursor.execute("DROP TABLE progress")
    cursor.execute('CREATE TABLE "progress" ("user" TEXT NOT NULL, "progress" INTEGER NOT NULL)')

    connection.commit()

    embed = discord.Embed(
      description = "<@&{}> It's time for a new 📖 We're now reading **{}** by **{}**. Links for this are available here:\n\n*[Goodreads](https://www.goodreads.com/book/show/{})*\n*[Indiebound](https://www.goodreads.com/book_link/follow/7?book_id={})*\n*[Amazon](https://www.goodreads.com/buy_buttons/12/follow?book_id={})*\n*[eBook Link]({})*\n*[Audiobook Link]({})*".format(readerRole, nextBook[0][1], nextBook[0][2], nextBook[0][3], nextBook[0][3], nextBook[0][3], nextBook[0][6], nextBook[0][7]),
        color = discord.Color.red()
    )
    embed.set_author(
        name="Book Swap",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=thumbnailImg
    )

    msg = await ctx.message.channel.send(content=None, embed=embed)


## Admin: Add eBook link
@client.command(name='ebook')
async def ebook(ctx, id: int, ebookUrl: str):
    query = ("UPDATE pool SET ebook_link = ? WHERE id = ?")
    ebookUpd = (ebookUrl, id)
    cursor.execute(query, ebookUpd)
    connection.commit()

    query = ("SELECT * FROM pool WHERE id = ?")
    cursor.execute(query, (id, ))
    updBook = cursor.fetchone()

    embed = discord.Embed(
        description = "You've successfully updated the eBook link for **{}** by **{}**".format(updBook[1], updBook[2]),
        color = discord.Color.red()
    )
    embed.set_author(
        name="eBook Update",
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=updBook[4]
    )
    
    msg = await ctx.message.channel.send(content=None, embed=embed)
             
## Admin: Add Audiobook link
@client.command(name='abook')
async def ebook(ctx, id: int, abookUrl: str):
    query = ("UPDATE pool SET abook_link = ? WHERE id = ?")
    abookUpd = (abookUrl, id)
    cursor.execute(query, abookUpd)
    connection.commit()

    query = ("SELECT * FROM pool WHERE id = ?")
    cursor.execute(query, (id, ))
    updBook = cursor.fetchone()

    embed = discord.Embed(
        description = "You've successfully updated the audiobook link for **{}** by **{}**".format(updBook[1], updBook[2]),
        color = discord.Color.red()
    )
    embed.set_author(
        name="Audiobook Update",aB
        icon_url=authorImg
    )
    embed.set_thumbnail(
        url=updBook[4]
    )
    
    msg = await ctx.message.channel.send(content=None, embed=embed)

# Starting Discord listener
client.run(discordToken)
