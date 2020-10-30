import discord
import asyncio
import random
import secrets
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle
from bs4 import BeautifulSoup
import requests
import json

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

#----- Client Events ----------------------------------------------------------#

@client.event
async def on_ready():
    global peasants
    global roleChannel
    global gameRoleMessage
    global roleEmojis
    global roleNames

    for guild in client.guilds:
        for member in guild.members:
            peasants = get(member.guild.roles, id = 702258422535421972)
        for channel in guild.text_channels:
            if channel.name == 'role-selection':
                roleChannel = channel
                print('Channel found')
                async for message in channel.history():
                    for embed in message.embeds:
                        if embed.author.name == 'Game Role Selection':
                            gameRoleMessage = message
                            print('Game found')
        #Sets Game Role Names
        roleName = ''
        for emoji in guild.emojis:
            if emoji.name.startswith('game'):
                roleEmojis.append(emoji)
    for emoji in roleEmojis:
        emojiName = emoji.name[4 :]
        for x in range(len(emojiName)):
            if emojiName[x : x + 1].isupper() or emojiName[x : x + 1].isdigit():
                if emojiName[x + 1 : x + 2].isupper() or emojiName[x + 1 : x + 2].isdigit():
                    roleName += emojiName[x : x + 1]
                else:
                    roleName += ' ' + emojiName[x : x + 1]
            else:
                roleName += emojiName[x : x + 1]
        if roleName[0 : 1] == ' ':
            roleName = roleName[1 :]
        roleNames.append(roleName)
        roleName = ''

    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('The Gulag'))

    print('For the Motherland')

@client.event
async def on_member_join(member):
    role = get(member.guild.roles, id = 702290979549610009)
    await member.add_roles(role)

@client.command(pass_context = True)
async def test(ctx):
    return

@client.event
async def on_raw_reaction_add(payload):
    global classEmojis
    global gameRoleMessage
    global classRoleMessage
    global schedule_message
    global schedule_emojis
    global schedule
    global survey_message

    #Checks if the message is the role message
    if gameRoleMessage != None:
        if payload.message_id == gameRoleMessage.id:
            roleFound = False
            index = 0
            for x in range(len(roleEmojis)):
                if roleEmojis[x].id == payload.emoji.id:
                    index = x
            for role in payload.member.guild.roles:
                if role.name == roleNames[index]:
                    roleFound = True
                    await payload.member.add_roles(role)
                    break
            if roleFound == False:
                roleToAdd = await payload.member.guild.create_role(name = roleNames[index], color = discord.Color.blurple())
                await payload.member.add_roles(roleToAdd)

@client.event
async def on_raw_reaction_remove(payload):
    global classEmojis

    #Checks if the message is the role message
    if gameRoleMessage != None:
        if payload.message_id == gameRoleMessage.id:
            member = None
            #Find the member who removed the reaction
            for guild in client.guilds:
                for user in guild.members:
                    if user.id == payload.user_id:
                        member = user
            #Removes Gaming Roles
            index = 0
            for x in range(len(roleEmojis)):
                if roleEmojis[x].id == payload.emoji.id:
                    index = x
            for role in member.guild.roles:
                if role.name == roleNames[index]:
                    await member.remove_roles(role)

@client.event
async def on_message_delete(message):
    global gameRoleMessage

    if message.id == gameRoleMessage.id:
        gameRoleMessage = None

#----- Bot Commands -----------------------------------------------------------#

roleChannel = None
gameRoleMessage = None
roleEmojis = []
roleNames = []

gulagees = []
peasants = None

@client.command(pass_context = True)
async def summon(ctx):
    hasAccess = has_access(ctx.message.author)

    if hasAccess == True:
        channel = ctx.message.author.voice.channel
        if channel == None:
            await ctx.channel.send('ERROR: You are not in a voice channel to summon someone into')
        else:
            if ctx.message.mention_everyone:
                for member in ctx.message.channel.guild.members:
                    if member.voice != None:
                        await member.move_to(channel)
            else:
                if len(ctx.message.mentions) > 0:
                    for member in ctx.message.mentions:
                        if member.voice != None:
                            await member.move_to(channel)
                else:
                    await ctx.channel.send('ERROR: You must also include who you are summoning')
    else:
        await ctx.channel.send('ERROR: You do not have permission to run this command')

@client.command(pass_context = True)
async def gulag(ctx):
    hasAccess = has_access(ctx.message.author)

    if hasAccess == True:
        if len(ctx.message.mentions) > 0:
            for member in ctx.message.mentions:
                await member.add_roles(peasants)
                await ctx.channel.send(member.mention + ' has been sent to the Gulag')
                if member.voice != None:
                    await member.move_to(client.get_channel(702221783268458506))
        else:
            await ctx.channel.send('ERROR: You must also include who you are sending to the gulag')
    else:
        await ctx.channel.send('ERROR: You do not have permission to run this command')

@client.command(pass_context = True)
async def free(ctx, user):
    hasAccess = has_access(ctx.message.author)

    if hasAccess == True:
        if len(ctx.message.mentions) > 0:
            for member in ctx.message.mentions:
                for peasant in peasants.members:
                    if member == peasant:
                        await member.remove_roles(peasants)
                        await ctx.channel.send(member.mention + ' has been freed from the Gulag')
                        break
        else:
            await ctx.channel.send('ERROR: You must also include who you are freeing from the gulag')
    else:
        await ctx.channel.send('ERROR: You do not have permission to run this command')

@client.command(pass_context = True)
async def rr(ctx):
    global roleChannel
    global roleEmojis
    global roleNames
    global gameRoleMessage

    hasAccess = has_access(ctx.message.author)

    if hasAccess == True:
        #Game Role Selection
        roleName = ''
        roleEmojis = []
        for emoji in ctx.channel.guild.emojis:
            if emoji.name.startswith('game'):
                roleEmojis.append(emoji)

        roleNames = []
        for emoji in roleEmojis:
            emojiName = emoji.name[4 :]
            for x in range(len(emojiName)):
                if emojiName[x : x + 1].isupper() or emojiName[x : x + 1].isdigit():
                    if emojiName[x + 1 : x + 2].isupper() or emojiName[x + 1 : x + 2].isdigit():
                        roleName += emojiName[x : x + 1]
                    else:
                        roleName += ' ' + emojiName[x : x + 1]
                else:
                    roleName += emojiName[x : x + 1]
            if roleName[0 : 1] == ' ':
                roleName = roleName[1 :]
            roleNames.append(roleName)
            roleName = ''

        embedString = ''
        for x in range(len(roleEmojis)):
            embedString += '<:' + roleEmojis[x].name + ':' + str(roleEmojis[x].id) + '>'
            embedString += ' ' + roleNames[x] + ' \n'
        embed = discord.Embed(colour=discord.Colour(0xab0000), description="React to this message with the rank you would like to add. To remove a rank, just simply remove the reaction. Спасибо!")
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
        embed.set_author(name="Game Role Selection", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
        embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
        embed.add_field(name = "Roles", value = embedString)

        if gameRoleMessage != None:
            await gameRoleMessage.delete()

        gameRoleMessage = await roleChannel.send(embed = embed)
        for emoji in roleEmojis:
            await gameRoleMessage.add_reaction(emoji)

def has_access(user):
    global peasants

    for role in user.roles:
        if role == peasants:
            return False
    for role in user.roles:
        if role.id == 702858654663180298:
            return True

    return False

#----- Rainbow Six Commands ---------------------------------------------------#

@client.command(pass_context = True)
async def r6(ctx):
    closed = False
    voting = True
    random = 0
    captain = 0
    captains = True
    captain1 = None
    captain2 = None
    host = ctx.message.author
    que = [host]
    team1 = []
    team2 = []
    rSixRole = None
    selectionEmojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭']

    for role in ctx.channel.guild.roles:
        if role.id == 703222153318891521:
            rSixRole = role

    embed = discord.Embed(title=host.name + " has started a Siege Queue!", colour=discord.Colour(0xab0000), description="Type !q to join")
    embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_footer(text="Powered by the Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
    await ctx.channel.send(content = rSixRole.mention, embed=embed)

    while closed == False:
        message = await client.wait_for('message')
        if message.content.startswith('!q'):
            inQue = False
            for person in que:
                if person == message.author:
                    inQue = True
            if inQue == False:
                await message.channel.send(message.author.name + ' has joined the queue')
                que.append(message.author)
        if message.content.startswith('!leave'):
            inQue = False
            for person in que:
                if person == message.author:
                    inQue = True
            if inQue == True:
                await message.channel.send(message.author.name + ' has left the queue')
                que.remove(message.author)
        if message.content.startswith('!close') or len(que) == 10:
            if message.author == host:
                closed = True

    embedString = ''
    for player in que:
        embedString += player.mention
        embedString += ", "

    embed = discord.Embed(title="The Queue has been completed!", colour=discord.Colour(0xab0000), description="Voting has now started.")
    embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
    embed.add_field(name="Vote for random teams:", value="!r", inline=True)
    embed.add_field(name="Vote for captains:", value="!c", inline=True)
    await ctx.channel.send(content=embedString[: len(embedString) - 2], embed=embed)

    while voting == True:
        message = await client.wait_for('message')
        if message.content.startswith('!r'):
            inQue = False
            for person in que:
                if person == message.author:
                    inQue = True
            if inQue == True:
                random += 1
        elif message.content.startswith('!c'):
            inQue = False
            for person in que:
                if person == message.author:
                    inQue = True
            if inQue == True:
                captain += 1
        if random + captain == len(que):
            if captain > random:
                captains = True
            else:
                captains = False
            voting = False

    if captains == True:
        captain1 = secrets.choice(que)
        team1.append(captain1)
        que.remove(captain1)
        captain2 = secrets.choice(que)
        team2.append(captain2)
        que.remove(captain2)

        embed = discord.Embed(title="Captains have been selected", colour=discord.Colour(0xab0000), description="Check your DM's")
        embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
        embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
        embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
        embed.add_field(name="Blue Team Captain:", value=captain1.mention, inline=True)
        embed.add_field(name="Orange Team Captain:", value=captain2.mention, inline=True)
        await ctx.channel.send(embed=embed)

        captain1Channel = await captain1.create_dm()
        captain2Channel = await captain2.create_dm()

        pick = False

        while len(que) > 0:
            embedString = ''
            for x in range(len(que)):
                embedString += selectionEmojis[x]
                embedString += ' ' + que[x].name + ' \n'
            embed = discord.Embed(title="You have been chosen as Captain!", colour=discord.Colour(0xab0000), description="React with the player you would like to select")
            embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
            embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
            embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
            embed.add_field(name="Players", value=embedString)
            captain1Message = await captain1Channel.send(embed=embed)

            for x in range(len(que)):
                await captain1Message.add_reaction(selectionEmojis[x])

            def check1(reaction, user):
                return user == captain1 and reaction.emoji != '🇸'
            reaction, user = await client.wait_for('reaction_add', check = check1)
            for x in range(len(que)):
                if selectionEmojis[x] == reaction.emoji.name:
                    team1.append(que[x])
                    que.pop(x)

            if len(que) == 0:
                break

            embedString = ''
            for x in range(len(que)):
                embedString += selectionEmojis[x]
                embedString += ' ' + que[x].name + ' \n'
            embed = discord.Embed(title="You have been chosen as Captain!", colour=discord.Colour(0xab0000), description="React with the player you would like to select")
            embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
            embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
            embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
            embed.add_field(name="Players", value=embedString)
            captain2Message = await captain2Channel.send(embed=embed)

            for x in range(len(que)):
                await captain2Message.add_reaction(selectionEmojis[x])

            def check2(reaction, user):
                return user == captain2 and reaction.emoji != '🇸'
            reaction, user = await client.wait_for('reaction_add', check = check2)
            if payload.member == captain2:
                for x in range(len(que)):
                    if selectionEmojis[x] == reaction.emoji.name:
                        team2.append(que[x])
                        que.pop(x)

    else:
        for x in range(round(len(que) / 2)):
            player = secrets.choice(que)
            team1.append(player)
            que.remove(player)
        team2 = que

    team1String = ''
    for player in team1:
        team1String += player.mention
        team1String += ' \n'

    team2String = ''
    for player in team2:
        team2String += player.mention
        team2String += ' \n'

    embed = discord.Embed(title="Teams have been selected!", colour=discord.Colour(0xab0000), description="Sending you to proper VCs now")
    embed.set_thumbnail(url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_author(name="Rainbow Six Queue", icon_url="https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766")
    embed.set_footer(text="Powered by The Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
    embed.add_field(name="Blue Team:", value=team1String, inline=True)
    embed.add_field(name="Orange Team:", value=team2String, inline=True)
    await ctx.channel.send(embed=embed)

    for player in team1:
        if player.voice != None:
            await player.move_to(client.get_channel(702223061167898773))
    for player in team2:
        if player.voice != None:
            await player.move_to(client.get_channel(702223030910189669))

@client.command(pass_context = True)
async def stats(ctx, user = '', mode = 'general'):
    try:
        values = collect_stats(user, mode)
    except AttributeError:
        await ctx.channel.send("ERROR: You did something wrong")
    except:
        await ctx.channel.send("ERROR: Something went wrong")
    else:
        ranks = ['COPPER V',' COPPER IV', 'COPPER III', 'COPPER II', 'COPPER I', 'BRONZE V', 'BRONZE IV', 'BRONZE III', 'BRONZE II', 'BRONZE I', 'SILVER V', 'SILVER IV', 'SILVER III', 'SILVER II', 'SILVER I', 'GOLD III', 'GOLD II', 'GOLD I', 'PLATINUM III', 'PLATINUM II', 'PLATINUM I', 'DIAMOND', 'CHAMPION']
        rank_images = ['https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-copper-5-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-copper-4.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-copper-3.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-copper-2.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-copper-1.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-bronze-5-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-bronze-4.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-bronze-3.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-bronze-2.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-bronze-1.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-silver-5-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-silver-4.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-silver-3.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-silver-21.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-silver-1.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-gold-3.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-gold-2.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-gold-1.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-platinum-3-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-platinum-2-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-ranks-platinum-1.jpg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-diamond-rank.jpeg', 'https://www.theloadout.com/wp-content/uploads/2020/03/rainbow-six-siege-champion-rank.jpeg']
        rank_image = None

        for x in range(len(ranks)):
            if ranks[x] == values[11]:
                rank_image = rank_images[x]

        if mode == 'ranked':
            embed = discord.Embed(title=user, colour=discord.Colour(0xab0000), url=values[0], description="To see full statistics, click on the player's name")
            embed.set_thumbnail(url=rank_image)
            embed.set_author(name='Ranked Statistics', icon_url='https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766')
            embed.set_footer(text="Powered by the Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
            embed.add_field(name="WINS", value=values[1], inline=True)
            embed.add_field(name="LOSSES", value=values[2], inline=True)
            embed.add_field(name="WIN %", value=values[6], inline=True)
            embed.add_field(name="KILLS", value=values[5], inline=True)
            embed.add_field(name="DEATHS", value=values[4], inline=True)
            embed.add_field(name="K/D", value=values[7], inline=True)
            embed.add_field(name="MATCHES", value=values[3], inline=True)
            embed.add_field(name="KILLS/MATCH", value=values[8], inline=True)
            embed.add_field(name="KILLS/MIN", value=values[9], inline=True)
            embed.add_field(name="RANK", value=values[11], inline=True)
            embed.add_field(name="MMR", value=values[13], inline=True)
            embed.add_field(name="ABANDONS", value=values[10], inline=True)
            await ctx.channel.send(embed=embed)

        elif mode == 'general':
            embed = discord.Embed(title=user, colour=discord.Colour(0xab0000), url=values[0], description="To see full statistics, click on the player's name")
            embed.set_thumbnail(url='https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766')
            embed.set_author(name='General Statistics', icon_url='https://www.toornament.com/media/file/416658754800049348/logo_large?v=1484842766')
            embed.set_footer(text="Powered by the Brotherhood", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/State_Emblem_of_the_Soviet_Union.svg/1200px-State_Emblem_of_the_Soviet_Union.svg.png")
            embed.add_field(name="WINS", value=values[5], inline=True)
            embed.add_field(name="LOSSES", value=values[6], inline=True)
            embed.add_field(name="WIN %", value=values[7], inline=True)
            embed.add_field(name="KILLS", value=values[13], inline=True)
            embed.add_field(name="DEATHS", value=values[3], inline=True)
            embed.add_field(name="K/D", value=values[2], inline=True)
            embed.add_field(name="MELEE KILLS", value=values[11], inline=True)
            embed.add_field(name="BLIND KILLS", value=values[12], inline=True)
            embed.add_field(name="HEADSHOTS", value=values[4], inline=True)
            embed.add_field(name="MATCHES", value=values[9], inline=True)
            embed.add_field(name="TIME PLAYED", value=values[8], inline=True)
            embed.add_field(name="HEADSHOT %", value=values[1], inline=True)
            await ctx.channel.send(embed=embed)

def collect_stats(user, mode):
    site = f"https://r6.tracker.network/profile/pc/{user}"
    source = requests.get(site).text
    soup = BeautifulSoup(source, 'lxml')

    values = []
    values.append(site)

    statistics = soup.find('div', class_ = "trn-scont__content")

    if mode == "general":
        big_stats = statistics.find('div', class_ = "trn-card__content pb16")
        big_chunk_kills = big_stats.find_all('div', class_ = "trn-defstat trn-defstat--large")[2]

        general_stats = statistics.find_all('div', class_ = "trn-card")[1]
        stats = general_stats.find_all('div', class_ = "trn-defstat")
        for x in range(len(stats)):
            label = format_label(stats[x].find('div', class_ = "trn-defstat__name"))
            value = format_value(stats[x].find('div', class_ = "trn-defstat__value"), True)
            values.append(value)

        kills_label = format_label(big_chunk_kills.find('div', class_ = "trn-defstat__name"))
        kills_value = format_value(big_chunk_kills.find('div', class_ = "trn-defstat__value"), True)
        values.append(kills_value)
        return values
    elif mode == "casual" or mode == "ranked":
        casrank_stats = statistics.find('div', class_ = "r6-pvp-grid")
        chunks = casrank_stats.find_all('div', class_ = "trn-card")

        if mode == "casual":
            stats = chunks[0].find_all('div', class_ = "trn-defstat")
            for x in range(len(stats)):
                label = format_label(stats[x].find('div', class_ = "trn-defstat__name"))
                value = format_value(stats[x].find('div', class_ = "trn-defstat__value"), True)
                values.append(value)
            return values
        elif mode == "ranked":
            stats = chunks[1].find_all('div', class_ = "trn-defstat")[1:]
            for x in range(len(stats)):
                label = format_label(stats[x].find('div', class_ = "trn-defstat__name"))
                value = format_value(stats[x].find('div', class_ = "trn-defstat__value"), True)
                values.append(value)
            ranked_area = statistics.find_all('div', class_ = "trn-card")[4]
            chunk = ranked_area.find('div', class_ = "r6-season__stats")
            ranked_stats = chunk.find_all('div', class_ = "trn-defstat")[7:]
            for x in range(len(ranked_stats)):
                label = format_label(ranked_stats[x].find('div', class_ = "trn-defstat__name"))
                value = format_value(ranked_stats[x].find('div', class_ = "trn-defstat__value"), False)
                values.append(value)
            image_chunk = ranked_area.find('div', class_ = "r6-season__info")
            image = image_chunk.find('img', class_ = "r6-season-rank__image")['src']
            values.append(image)
            return values

def format_label(label):
    label = str(label).split(">")[1]
    label = label.split("<")[0].upper()
    return label

def format_value(value, chopped):
    value = str(value).split(">")[1]
    value = value.split("<")[0].upper()
    if chopped:
        if value.startswith(" "):
            return value[3:-1]
        elif value.endswith(" "):
            return value[1:-2]
        else:
            return value[1:-1]
    else:
        return value

#------------------------------------------------------------------------------#

client.run('NzAyMjI1MjAzOTc1MTU5ODY5.Xp88Lw.yv-SbfFJFRp8zAcHowWgkFoNsxY')
