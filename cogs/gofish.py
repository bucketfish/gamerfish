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

from discord import context

from defines import text
from defines import colors
import jasima

import random
import asyncio

games = {}
cards = ["A♦","A♣","A♥","A♠","2♦","2♣","2♥","2♠","3♦","3♣","3♥","3♠","4♦","4♣","4♥","4♠","5♦","5♣","5♥","5♠","6♦","6♣","6♥","6♠","7♦","7♣","7♥","7♠","8♦","8♣","8♥","8♠","9♦","9♣","9♥","9♠","10♦","10♣","10♥","10♠","J♦","J♣","J♥","J♠","Q♦","Q♣","Q♥","Q♠","K♦","K♣","K♥","K♠"]

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
            await begingofish(ctx)
        elif action == "leave":
            await leavegofish(ctx)
        elif action == "stop":
            await stopgame(ctx)

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

    if isinstance(ctx, context.ApplicationContext):
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
            games[ctx.channel]["players"][ctx.author]["cards"] = []
            games[ctx.channel]["players"][ctx.author]["completed"] = []
            embed = embed_playerjoin(ctx.author.mention, len(games[ctx.channel]["players"].keys()))

    else:
        embed = embed_nogameyet()
        ephemeral = True

    if isinstance(ctx, context.ApplicationContext):
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

    if isinstance(ctx, context.ApplicationContext):
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

        if playercount == 2:
            cardspp = 7

        for i in curgame["players"].keys():
            curgame["players"][i]["cards"] = shufflesort(random.sample(carddeck, cardspp))
            carddeck = [item for item in carddeck if item not in curgame["players"][i]["cards"]]

            embed = embed_playercards(curgame["players"][i]["cards"])
            await i.send("", embed=embed)

        while won == False:
            await gamescreen.edit_original_message(embed=embed_round(curgame, playerlist[curplayerc], len(carddeck)))

            nextmove = False

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








    # ADD SOME WAY TO LIKE. LOOK AT COMPLETED PILES OF CARDS. JESUS CHRIST YOU FOOL
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
        playerset = [item.name for item in playerlist if item.name != curplayer.name]

        for i in playerset:
            button = personbutton(style=ButtonStyle.primary,
                                label= i,
                                curplayer=curplayer)
            self.add_item(button)

class personbutton(Button):
    def __init__(self, style, label: int, curplayer: Member):
        super().__init__(style=style, label=label)
        self.curplayer = curplayer

    async def callback(self, interaction):
        self.view.value = self.curplayer
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

    if isinstance(ctx, context.ApplicationContext):
        await ctx.respond(message, embed=embed, ephemeral=ephemeral)
    else:
        await ctx.send(message, embed=embed, ephemeral=ephemeral)

async def stopgame(ctx):
    pass

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

def embed_startgame():
    embed = Embed()
    embed.title = "go fish: current game"
    embed.colour = colors["flavor"]
    embed.description="shuffling cards..."
    return embed

def embed_round(curgame, curplayer, cardsleft):
    embed = Embed()
    embed.title = "go fish: current game"
    embed.colour = colors["flavor"]
    embed.description="it's now " + curplayer.mention + "'s turn!"

    for i in curgame["players"]:
        embed.add_field(name=i.name, value=":blue_square: " * len(curgame["players"][i]["cards"]))


    footer = str(cardsleft) + " cards left in the draw pile."
    embed.set_footer(text=footer)
    return embed

def embed_rounddm(curgame, curplayer):
    embed = Embed()
    embed.title = "go fish: it's your turn :)"
    embed.colour = colors["flavor2"]
    embed.description = "which card do you want to ask someone for?\nyour cards: "
    for i in curgame["players"][curplayer]["cards"]:
        embed.description += carde[i[0]] + " "

    for i in curgame["players"]:
        if i == curplayer:
            continue
        embed.add_field(name=i.name, value=":blue_square: " * len(curgame["players"][i]["cards"]))

    return embed

def embed_rounddm_ask(curgame, curplayer, card):
    embed = Embed()
    embed.title = "go fish: asking for cards"
    embed.colour = colors["flavor2"]
    embed.description = "who do you want to ask for a " + carde[card[0]] + " from?"

    for i in curgame["players"]:
        if i == curplayer:
            continue
        embed.add_field(name=i.name, value=":blue_square: " * len(curgame["players"][i]["cards"]))
    return embed

def embed_playercards(cards):
    global carde

    embed = Embed()
    embed.title = "go fish: here are your cards!"
    embed.colour = colors["flavor"]
    embed.description = ""
    for i in cards:
        embed.description += carde[i[0]] + " "
    return embed

def shufflesort(cardlist):
    global cards
    return sorted(cardlist, key=lambda x: cards.index(x))

def shufflesortstripped(cardlist):
    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    return sorted(cardlist, key=lambda x: cards.index(x))

def cardstrip(card):
    return card[:-1]





# for i in response["def"].keys():
#     embed.add_field(name=i, value=response["def"][i])

#     sentence = input.split()
#     embeds = []
#     message_response = ""
#
#     for word in sentence:
#         word = parse_word(word)
#         response = jasima.get_word_entry(word)
#         if isinstance(response, str):
#             message_response += response
#             continue
#
#         embeds.append(embed_response(word, response))
#
#     if isinstance(ctx, context.ApplicationContext):
#         await ctx.respond(message_response, embeds=embeds)
#     else:
#         await ctx.send(message_response, embeds=embeds)
#
# def embed_response(word, response):
#     embed = Embed()
#     embed.title = response["word"]
#     embed.colour = Colour.from_rgb(247,168,184)
#     for i in response["def"].keys():
#         embed.add_field(name=i, value=response["def"][i])
#
#     return embed
