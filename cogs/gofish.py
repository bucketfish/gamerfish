from discord.ext import commands
from discord.commands import slash_command
from discord import Option
from discord import Embed
from discord import Colour
from discord import ButtonStyle
from discord import ui
from discord import Member
from discord.ui import View
from discord.ui import Button

from discord import ApplicationContext

from defines import text
from defines import colors

import random
import asyncio

games = {}
cards = ["A♦","A♣","A♥","A♠","2♦","2♣","2♥","2♠","3♦","3♣","3♥","3♠","4♦","4♣","4♥","4♠","5♦","5♣","5♥","5♠","6♦","6♣","6♥","6♠","7♦","7♣","7♥","7♠","8♦","8♣","8♥","8♠","9♦","9♣","9♥","9♠","10♦","10♣","10♥","10♠","J♦","J♣","J♥","J♠","Q♦","Q♣","Q♥","Q♠","K♦","K♣","K♥","K♠"]

#cards = ["A♦","A♣","A♥","A♠","2♦","2♣","2♥","2♠","3♦","3♣","3♥","3♠","4♦","4♣","4♥","4♠"]


carde = {
    "A": ":regional_indicator_a:",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
    "1": "🔟",
    "10": "🔟",
    "J": ":regional_indicator_j:",
    "Q": ":regional_indicator_q:",
    "K": " :regional_indicator_k:"
}

cardnum = {
    "A": "A",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "1": "10",
    "J": "J",
    "Q": "Q",
    "K": "K"
}

tasks = {}

class CogGofish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
      name='gofish',
      description=text["DESC_GOFISH"],
    )
    async def slash_gofish(self, ctx, action: Option(str,
                    "action",
                    choices=["create", "join", "leave", "start", "stop"],
                    required=True)):
        if action == "create":
            await gofish(ctx)
        elif action == "join":
            await joingofish(ctx)
        elif action == "start":
            task = asyncio.create_task(begingofish(ctx))
            tasks[ctx.channel] = task
            await task

        elif action == "leave":
            await leavegofish(ctx)
        elif action == "stop":
            embed = None
            ephemeral = False

            if games[ctx.channel]:
                if ctx.author == games[ctx.channel]["gamemaster"]:
                    if ctx.channel in tasks.keys():
                        if not tasks[ctx.channel].cancelled():
                            tasks[ctx.channel].cancel()
                        else:
                            tasks[ctx.channel] = None
                        del tasks[ctx.channel]

                        embed = embed_stopgame()
                        del games[ctx.channel]

                    else:
                        embed = embed_gamenotstarted()

                else:
                    embed = embed_notgamemaster_stop(games[ctx.channel]["gamemaster"].mention)
                    ephemeral = True

            else:
                embed = embed_nogameyet()
                ephemeral = True

            if isinstance(ctx, ApplicationContext):
                await ctx.respond("", embed=embed, ephemeral=ephemeral)
            else:
                await ctx.send("", embed=embed)




    @slash_command(
      name='test',
      description="test. the bot. yes."
    )
    async def slash_testfish(self, ctx):
        if ctx.author.id == 670962000964354049:
            games[ctx.channel] = {
                "gameon": False,
                "players": {ctx.author: {
                "cards": [],
                "completed": []
                }, await self.bot.fetch_user(948417931568611338): {
                "cards": [],
                "completed": []
                }
                },
                "gamemaster": ctx.author
            }
            await begingofish(ctx)

async def gofish(ctx):
    global games

    message_response = ""
    embeds = []
    ephemeral = False

    if ctx.channel in games.keys():
        embeds.append(embed_gamealreadyrunning())
        ephemeral = True

    else:
        games[ctx.channel] = {
            "gameon": False,
            "players": {ctx.author: {
                "cards": [],
                "completed": []
            }},
            "gamemaster": ctx.author
        }
        embeds.append(embed_gamecreate())
        embeds.append(embed_playerjoin(ctx.author.mention, len(games[ctx.channel]["players"].keys())))
        ephemeral = False

    if isinstance(ctx, ApplicationContext):
        await ctx.respond("", embeds=embeds, ephemeral=ephemeral)
    else:
        await ctx.send("", embeds=embeds, ephemeral=ephemeral)

async def joingofish(ctx):
    global games

    message_response = ""
    embed = None
    ephemeral = False

    if ctx.channel in games.keys():
        if len(games[ctx.channel]["players"].keys()) >= 10:
            embed = embed_toomanyplayers()
            ephemeral = True

        if ctx.author in games[ctx.channel]["players"].keys():
            embed = embed_alreadyin()
            ephemeral = True
        else:
            games[ctx.channel]["players"][ctx.author] = {
                "cards": [],
                "completed": []
            }
            embed = embed_playerjoin(ctx.author.mention, len(games[ctx.channel]["players"].keys()))

    else:
        embed = embed_nogameyet()
        ephemeral = True

    if isinstance(ctx, ApplicationContext):
        await ctx.respond("", embed=embed, ephemeral=ephemeral)
    else:
        await ctx.send(embed=embed, ephemeral=ephemeral)

async def begingofish(ctx):
    global games
    global cards

    message = ""
    embeds = []
    ephemeral = False
    playing = False
    gamescreen = None

    if not games[ctx.channel]:
        embeds.append(embed_nogameyet())
        ephemeral = True
    elif len(games[ctx.channel]["players"].keys()) < 2:
        embeds.append(embed_notenoughplayers())
        ephemeral = True
    elif ctx.author != games[ctx.channel]["gamemaster"]:
        embeds.append(embed_notgamemaster_start(games[ctx.channel]["gamemaster"].mention))
        ephemeral = True
    else:
        games[ctx.channel]["gameon"] = True
        embeds.append(embed_startgame())

    if isinstance(ctx, ApplicationContext):
        gamescreen = await ctx.respond(message, embeds=embeds, ephemeral=ephemeral)
    else:
        gamescreen = await ctx.send(message, embeds=embeds, ephemeral=ephemeral)


    if games[ctx.channel]["gameon"] == True:
        curgame = games[ctx.channel]
        won = False
        playercount = len(curgame["players"].keys())
        carddeck = random.sample(cards, len(cards))
        cardspp = 5
        curplayerc = 0
        playerlist = list(curgame["players"].keys())
        curplayer = playerlist[curplayerc]

        completeds = 0
        completecount = 13 #CHANGE THIS CHANGE THIS BANG BANG YAS!!!

        if playercount == 2:
            cardspp = 7

        for i in curgame["players"].keys():
            curgame["players"][i]["cards"] = shufflesort(random.sample(carddeck, cardspp))
            carddeck = [item for item in carddeck if item not in curgame["players"][i]["cards"]]


            for j in curgame["players"][i]["cards"]:
                askingfor = cardstrip(j)
                win, newlist = checkwin(curgame["players"][curplayer]["cards"], askingfor)

                if win:
                    curgame["players"][curplayer]["cards"] = newlist
                    curgame["players"][curplayer]["completed"].append(askingfor)
                    #embed player completed the x card
                    embed = embed_completed(curplayer, askingfor)
                    completeds += 1

                    await ctx.send("", embed=embed)

            embed = embed_playercards(curgame["players"][i]["cards"])
            await i.send("", embed=embed)


        await gamescreen.edit_original_message(embed=embed_doneshuffling())

        while won == False:
            gamescreen = await ctx.send(embed=embed_round(curgame, playerlist[curplayerc], len(carddeck)))

            nextmove = False if len(curgame["players"][curplayer]["cards"]) > 0 else True
            askingfor = None

            while nextmove == False:
                embed = embed_rounddm(curgame, curplayer)
                view = roundviewdm(curgame["players"][curplayer]["cards"], list(curgame["players"].keys()), curplayer)
                dmmsg = await curplayer.send("", embed=embed, view=view)

                await view.wait()

                askingfor = view.value
                embed = embed_rounddm_ask(curgame, curplayer, askingfor)

                view = roundviewdm_ask(curgame["players"][curplayer]["cards"], list(curgame["players"].keys()), curplayer)

                await dmmsg.edit(embed=embed, view=view)

                await view.wait()
                askedperson = view.value

                given, curgame["players"][askedperson]["cards"] = givecards(curgame["players"][askedperson]["cards"], askingfor)

                if len(given) != 0:

                    curgame["players"][curplayer]["cards"] += given #added cards to asking player
                    curgame["players"][curplayer]["cards"] = shufflesort(curgame["players"][curplayer]["cards"])

                    win, newlist = checkwin(curgame["players"][curplayer]["cards"], askingfor)

                    embed = embed_askresult(curplayer, askingfor, askedperson, given)
                    embed_dm = embed_askresult_dm(curplayer, askingfor, askedperson, given, curgame["players"][curplayer]["cards"])

                    await ctx.send("", embed=embed)
                    await dmmsg.edit(embed=embed_dm, view=None)

                    if win:
                        curgame["players"][curplayer]["cards"] = newlist
                        curgame["players"][curplayer]["completed"].append(askingfor)

                        embed = embed_completed(curplayer, askingfor)
                        completeds += 1

                        await ctx.send("", embed=embed)

                    #now you can do it again!

                else:
                    #opponent doesn't have card.
                    #cur asked target for card. they do not have

                    embed = embed_askresult(curplayer, askingfor, askedperson, given)
                    embed_dm = embed_askresult_dm(curplayer, askingfor, askedperson, given, curgame["players"][curplayer]["cards"])

                    await ctx.send(embed=embed)
                    await dmmsg.edit(embed=embed_dm, view=None)

                    nextmove = True

                if len(curgame["players"][curplayer]["cards"]) <= 0:
                    nextmove = True



            stilldrawing = True if len(carddeck) > 0 else False
            while stilldrawing:
                newcard = random.sample(carddeck, 1)[0]
                carddeck = [item for item in carddeck if item != newcard ]

                curgame["players"][curplayer]["cards"].append(newcard)
                curgame["players"][curplayer]["cards"] = shufflesort(curgame["players"][curplayer]["cards"])

                if cardstrip(newcard) == askingfor:
                    embed = embed_drewcardyes(curplayer, newcard)
                    #x drew card x.

                else:
                    embed = embed_drewcardno(curplayer)
                    stilldrawing = False

                embed_dm = embed_drewcard_dm(newcard)
                await ctx.send("", embed=embed)
                await curplayer.send("", embed=embed_dm)


                win, newlist = checkwin(curgame["players"][curplayer]["cards"], cardstrip(newcard))

                if win:
                    curgame["players"][curplayer]["cards"] = newlist
                    curgame["players"][curplayer]["completed"].append(cardstrip(newcard))
                    #embed player completed the x card
                    embed = embed_completed(curplayer, cardstrip(newcard))
                    completeds += 1

                    await ctx.send("", embed=embed)


            if completeds >= completecount:
                #GAME OVER. END IT.
                #all cards has been drawn. list finished player and list winner
                embed = embed_gameover(curgame["players"])
                await ctx.send("", embed=embed)
                won = True
                del games[ctx.channel]
            else:
                curplayerc += 1
                if curplayerc >= len(playerlist):
                    curplayerc = 0
                curplayer = playerlist[curplayerc]


    # game rounds!



class roundviewdm(View):
    global carde
    def __init__(self, values, playerlist, curplayer):
        super().__init__()
        self.value = None
        cardset = shufflesortstripped(list(set([cardstrip(item) for item in values])))

        for i in cardset:
            button = cardbutton(style=ButtonStyle.primary,
                                label= i,
                                custom_id=i)
            self.add_item(button)

class cardbutton(Button):
    async def callback(self, interaction):
        self.view.value = self.label
        self.view.stop()


class roundviewdm_ask(View):
    global carde
    def __init__(self, values, playerlist, curplayer):
        super().__init__()
        self.value = None
        playerset = [item for item in playerlist if item != curplayer]

        for i in playerset:
            button = personbutton(style=ButtonStyle.primary,
                                label= i.name,
                                player=i)
            self.add_item(button)

class personbutton(Button):
    def __init__(self, style, label: str, player: Member):
        super().__init__(style=style, label=label)
        self.player = player

    async def callback(self, interaction):
        self.view.value = self.player
        self.view.stop()



async def leavegofish(ctx):
    global games
    message = ""
    embed = None
    ephemeral = False

    if ctx.channel not in games.keys():
        embed = embed_nogameyet()
        ephemeral = True
    elif ctx.author not in games[ctx.channel]["players"].keys():
        embed = embed_notingame()
        ephemeral = True

    elif games[ctx.channel]["gameon"] == True:
        embed = embed_gamestarted(games[ctx.channel]["gamemaster"].mention)
        ephemeral = True

    elif ctx.author in games[ctx.channel]["players"].keys():
        embed = embed_playerleave(ctx.author.mention, len(games[ctx.channel]["players"].keys())-1)
        games[ctx.channel]["players"].pop(ctx.author)

    if isinstance(ctx, ApplicationContext):
        await ctx.respond(message, embed=embed, ephemeral=ephemeral)
    else:
        await ctx.send(message, embed=embed, ephemeral=ephemeral)


def embed_playerjoin(ping, count):
    embed = Embed()
    embed.description = ping + " joined the game! (" + str(count) + "/10)"
    embed.colour = colors["flavor2"]
    return embed

def embed_playerleave(ping, count):
    embed = Embed()
    embed.description = ping + " left the game. (" + str(count) + "/10)"
    embed.colour = colors["flavor2"]
    return embed

def embed_alreadyin():
    embed = Embed()
    embed.description = "you're already in the game! wait for the host to start it."
    embed.colour = colors["flavor2"]
    return embed

def embed_gamecreate():
    embed = Embed()
    embed.title = "go fish game created!"
    embed.colour = colors["flavor"]
    embed.description="type `/gofish join` to join :)"
    return embed

def embed_gamealreadyrunning():
    embed = Embed()
    embed.title = "there is already another go fish game in the channel."
    embed.colour = colors["warning"]
    embed.description="type `/gofish join` to join :)"
    return embed

def embed_nogameyet():
    embed = Embed()
    embed.title = "there's no game yet."
    embed.colour = colors["warning"]
    embed.description="type `/gofish create` to create one!"
    return embed

def embed_gamestarted(gamemaster):
    embed = Embed()
    embed.title = "the game has already started!"
    embed.colour = colors["warning"]
    embed.description="to leave, get " + gamemaster + " to stop the game by running `/gofish stop`. the game will also time out after 2 minutes of inactivity."
    return embed

def embed_notingame():
    embed = Embed()
    embed.title = "you're not in the game!"
    embed.colour = colors["warning"]
    embed.description="type `/gofish join` to join in."
    return embed

def embed_gamenotstarted():
    embed = Embed()
    embed.title = "the game's not started!"
    embed.colour = colors["warning"]
    embed.description="you can't stop a game without starting it."
    return embed

def embed_notenoughplayers():
    embed = Embed()
    embed.title = "there are not enough players!"
    embed.colour = colors["warning"]
    embed.description="you need at least 2 players to start the game."
    return embed

def embed_toomanyplayers():
    embed = Embed()
    embed.title = "there are too many players!"
    embed.colour = colors["warning"]
    embed.description="you can only have 10 players in the game."
    return embed

def embed_notgamemaster_start(ping):
    embed = Embed()
    embed.colour = colors["warning"]
    embed.description="only the gamemaster, " + ping + ", can start the game."
    return embed

def embed_notgamemaster_stop(ping):
    embed = Embed()
    embed.colour = colors["warning"]
    embed.description="only the gamemaster, " + ping + ", can stop the game."
    return embed

def embed_startgame():
    embed = Embed()
    embed.title = "go fish: current game"
    embed.colour = colors["flavor"]
    embed.description="shuffling cards..."
    return embed

def embed_doneshuffling():
    embed = Embed()
    embed.title = "go fish: current game"
    embed.colour = colors["flavor"]
    embed.description="game started! check your dms :)"
    return embed

def embed_round(curgame, curplayer, cardsleft):
    embed = Embed()
    embed.title = "go fish: current game"
    embed.colour = colors["flavor"]
    embed.description="it's now " + curplayer.mention + "'s turn!"

    for i in curgame["players"]:
        fieldvalue = ":blue_square: " * len(curgame["players"][i]["cards"])
        if len(curgame["players"][i]["cards"]) == 0:
            fieldvalue = "no cards."

        if len(curgame["players"][i]["completed"]) != 0:
            fieldvalue += "\n"
            for card in curgame["players"][i]["completed"]:
                fieldvalue += carde[cardstrip(card)] + " "

        embed.add_field(name=i.name, value = fieldvalue)

    footer = str(cardsleft) + " cards left in the draw pile."
    embed.set_footer(text=footer)
    return embed

def embed_rounddm(curgame, curplayer):
    embed = Embed()
    embed.title = "go fish: it's your turn :)"
    embed.colour = colors["action"]
    embed.description = "which card do you want to ask someone for?\nyour cards: "
    for i in curgame["players"][curplayer]["cards"]:
        embed.description += carde[cardstrip(i[0])] + " "

    for i in curgame["players"]:
        if i == curplayer:
            continue

        fieldvalue = ":blue_square: " * len(curgame["players"][i]["cards"])
        if len(curgame["players"][i]["cards"]) == 0:
            fieldvalue = "no cards."

        if len(curgame["players"][i]["completed"]) != 0:
            fieldvalue += "\n"
            for card in curgame["players"][i]["completed"]:
                fieldvalue += carde[cardstrip(card)] + " "

        embed.add_field(name=i.name, value = fieldvalue)


    return embed

def embed_rounddm_ask(curgame, curplayer, card):
    embed = Embed()
    embed.title = "go fish: asking for cards"
    embed.colour = colors["action"]
    embed.description = "who do you want to ask for a " + carde[cardstrip(card[0])] + " from?"

    for i in curgame["players"]:
        if i == curplayer:
            continue

        fieldvalue = ":blue_square: " * len(curgame["players"][i]["cards"])
        if len(curgame["players"][i]["cards"]) == 0:
            fieldvalue = "no cards."

        embed.add_field(name=i.name, value=fieldvalue)
    return embed

def embed_playercards(cards):
    global carde

    embed = Embed()
    embed.title = "go fish: here are your cards!"
    embed.colour = colors["flavor"]
    embed.description = ""
    for i in cards:
        embed.description += carde[cardstrip(i[0])] + " "
    return embed

def embed_askresult(curplayer, targetcard, targetplayer, given):
    embed = Embed()
    embed.title = curplayer.name + " has asked " + targetplayer.name + " for a " + carde[cardstrip(targetcard)] + "!"
    embed.colour = colors["flavor2"]
    if len(given) == 0:
        embed.colour = colors["warning"]
        embed.description = "go fish! " + targetplayer.name + " did not have any " + targetcard + "s."

    else:
        embed.description = targetplayer.mention + " → " + carde[cardstrip(targetcard)] * len(given) + " → " + curplayer.mention
        footer = "currently still " + curplayer.name + "'s turn."
        embed.set_footer(text=footer)

    return embed

def embed_askresult_dm(curplayer, targetcard, targetplayer, given, cardlist):
    embed = Embed()
    embed.title = "you asked " + targetplayer.name + " for a " + carde[cardstrip(targetcard)]
    embed.colour = colors["flavor2"]
    if len(given) == 0:
        embed.colour = colors["warning"]
        embed.description = "go fish! " + targetplayer.mention + " did not have any " + targetcard + "s."
    else:
        embed.description = targetplayer.mention + " → " + carde[cardstrip(targetcard)] * len(given) + " → " + curplayer.mention

    embed.description += "\nyour cards: "
    for i in cardlist:
        embed.description += carde[cardstrip(i[0])] + " "

    return embed

def embed_drewcardyes(curplayer, card):
    embed = Embed()
    embed.title = curplayer.name + " drew a " + carde[cardstrip(card)]
    embed.colour = colors["flavor2"]
    embed.description = "the same card they asked for!"
    footer = "currently still " + curplayer.name + "'s turn."
    embed.set_footer(text=footer)
    return embed

def embed_drewcardno(curplayer):
    embed = Embed()
    embed.title = curplayer.name + " drew a card"
    embed.colour = colors["flavor2"]
    embed.description = "now onto the next player :)"
    return embed

def embed_drewcard_dm(card):
    embed = Embed()
    embed.title = "you drew a card!"
    embed.colour = colors["flavor2"]
    embed.description = carde[cardstrip(card)]
    return embed

def embed_completed(curplayer, card):
    embed = Embed()
    embed.title = curplayer.name + " completed a set of " + carde[card]
    embed.colour = colors["flavor"]
    return embed

def embed_gameover(curp): #curgame["players"]
    embed = Embed()
    embed.title = "🎉 game over! 🎉"
    embed.colour = colors["action"]
    maxcount = 0
    winner = []

    for i in curp:
        fieldvalue = ""
        for card in curp[i]["completed"]:
            fieldvalue += carde[cardstrip(card)] + " "

        if len(curp[i]["completed"]) > maxcount:
            winner = [i]
            maxcount = len(curp[i]["completed"])
        elif len(curp[i]["completed"]) == maxcount:
            winner.append(i)

        embed.add_field(name=i.name, value = fieldvalue)

    if len(winner) == 1:
        embed.description = "the winner is " + winner[0].mention + " with " + str(len(curp[winner[0]]["completed"])) + " completed sets!"

    else:
        embed.description = "the winners are " + winner[0].mention
        for i in range(1, len(winner)):
            embed.description += " & " + winner[i].mention
        embed.description += " with " + str(len(curp[winner[0]]["completed"])) + " completed sets!"

    return embed

def embed_stopgame():
    embed = Embed()
    embed.title = "game stopped!"
    embed.description = "the game has been stopped. do `/gofish create` to create a new one."
    embed.colour = colors["warning"]
    return embed

def shufflesort(cardlist):
    global cards
    return sorted(cardlist, key=lambda x: cards.index(x))

def shufflesortstripped(cardlist):
    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    return sorted(cardlist, key=lambda x: cards.index(x))

def cardstrip(card):
    return card[:-1] if card[-1] in ["♦","♣","♥","♠"] else card

def stripcardlist(cardlist):
    return list(set([cardstrip(item) for item in cardlist]))

def givecards(cardlist, target):
    given = []
    newcardlist = []
    for i in cardlist:
        if cardstrip(i) == target:
            given.append(i)
        else:
            newcardlist.append(i)

    return (given, newcardlist)

def checkwin(cardlist, target):
    count = 0
    updatedlist = []
    for i in cardlist:
        if cardstrip(i) == target:
            count += 1
        else:
            updatedlist.append(i)

    if count >= 4:
        return True, updatedlist
    else:
        return False, cardlist
