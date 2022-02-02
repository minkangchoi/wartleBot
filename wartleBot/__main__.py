#!/usr/bin/env python3
from distutils.log import debug
import os
import argparse
import discord

from dotenv import load_dotenv

from .wartleBot import WartleBot
from .cogs.command_err_handler import CommandErrHandler
from .cogs.setup import Setup
from .cogs.help import Help

def main():
    # Command line args for debug mode
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    debug_mode = args.debug

    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    TENOR_TOKEN = os.getenv('TENOR_TOKEN')
    DEBUG_GUILD = os.getenv('DEBUG_GUILD')
    DEBUG_CHANNEL = os.getenv('DEBUG_CHANNEL')

    intents = discord.Intents.default()

    bot = discord.ext.commands.Bot(
        command_prefix='!',
        intents=intents,
        help_command=None
    )
    bot.TENOR_TOKEN = TENOR_TOKEN

    # Add neccesary cogs to bot
    bot.add_cog(WartleBot(bot))
    bot.add_cog(Setup(bot, debug_mode, DEBUG_GUILD, DEBUG_CHANNEL))
    bot.add_cog(Help())
    bot.add_cog(CommandErrHandler(bot))



    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    main()
