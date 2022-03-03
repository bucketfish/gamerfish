from discord.ext import commands

#from keep_alive import keep_alive

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

from cogs.gofish import CogGofish

bot = commands.Bot(command_prefix="/")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        print("* {}".format(guild.name))


if __name__ == "__main__":
    bot.add_cog(CogGofish(bot))
    #keep_alive()
    bot.run(TOKEN, reconnect=True)
