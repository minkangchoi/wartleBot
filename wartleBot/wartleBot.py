import json
from discord.ext import commands
from .game.game import Game

class WartleBot(commands.Cog):

    """
    channels: A dict with {<guild_id>: <channel>} that stores which
        channel to send messages in for each guild. Initialized with
        all guilds the bot is a part of as key, and None type as value

    games: A dict with {<guild_id: <Game_object>} that keeps track of a
        game being played in each guild
    """
    channels = {}
    games = {}
    word_length = 9
    TENOR_TOKEN = -1

    @commands.command(aliases=["start"])
    async def start_game(self, ctx, arg):
        if not await self.passed_pre_checks(ctx):
            return
        # If game object doesnt already exist, create one
        if not self.games.get(ctx.guild.id):
            self.games[ctx.guild.id] = Game(ctx.guild.id, ctx.channel, self, self.TENOR_TOKEN)
        # If game is not already up
        if self.games[ctx.guild.id].game_over:
                

            await self.games[ctx.guild.id].start_game(arg)
        # Else dont start another game
        else:
            await self.channels[ctx.guild.id].send("A game is already running!")

    """
    Turn friendly mode on or off for the guild
    """
    @commands.command()
    async def friendly(self, ctx, arg):
        if self.game_exists(ctx):
            if arg == "on":
                self.games[ctx.guild.id].friendly_mode = True
                await ctx.channel.send("Friendly mode has been turned **on**")
            elif arg == "off":
                self.games[ctx.guild.id].friendly_mode = False
                await ctx.channel.send("Friendly mode has been turned **off**")
            else:
                await ctx.channel.send("Useage: `!friendly on` or `!friendly off`")
        else:
            await ctx.channel.send("Wait for a game to start first!")

    """
    Command to guess a word
    """
    @commands.command(aliases=["g"])
    async def guess(self, ctx, arg):
        if not await self.after_join_prechecks(ctx):
            return
        await self.games[ctx.guild.id].guess(ctx, arg)

    """
    Command to register users for the game
    """
    @commands.command(aliases=["j"])
    async def join(self, ctx):
        if not await self.passed_pre_checks(ctx):
            return
        if not self.game_exists(ctx):
            await self.channels[ctx.guild.id].send("The game hasn't started yet!")
            return
        await self.games[ctx.guild.id].join(ctx)

    """
    Command to return number of guesses remaining for user
    """
    @commands.command(aliases=["r"])
    async def remaining(self, ctx):
        if not await self.after_join_prechecks(ctx):
            return
        await self.games[ctx.guild.id].remaining(ctx)

    """
    Show correct letters in the right spot
    """
    @commands.command(aliases=["c"])
    async def correct(self, ctx):
        if not await self.after_join_prechecks(ctx):
            return
        await self.games[ctx.guild.id].correct(ctx)

    """
    Prints history of guessed words for the game
    """
    @commands.command(aliases=["h"])
    async def history(self, ctx):
        if not await self.after_join_prechecks(ctx):
            return
        await self.games[ctx.guild.id].history(ctx)

    """
    Lists Green, yellow, white, and black letters
    """
    @commands.command(aliases=["l"])
    async def letters(self, ctx):
        if not await self.after_join_prechecks(ctx):
            return
        await self.games[ctx.guild.id].letters(ctx)

    ########################## HELPER FUCNTIONS ##########################
    """
    Checks for commands that run during a game 
    """
    async def after_join_prechecks(self, ctx):
        if not await self.passed_pre_checks(ctx):
            return False
        if not self.game_exists(ctx):
            await self.channels[ctx.guild.id].send("The game hasn't started yet!")
            return False
        if await self.game_is_over(ctx, self.games[ctx.guild.id]):
            return False
        return True

    """
    Check if game object exists, if not return None
    """
    def game_exists(self, ctx):
        return self.games.get(ctx.guild.id)

    """
    Returns True if game is over
    """
    async def game_is_over(self, ctx, game):
        if game.game_over:
            await self.channels[ctx.guild.id].send("The game is over, please wait for the next one to start")
            return True
        return False

    """
    Verifies that the player has set up the bot in a channel and is
    writing to the set channel. This is run before every game function
    """
    async def passed_pre_checks(self, ctx):
        if not self.channels[ctx.guild.id]:
            await ctx.channel.send("Before you can do anything, assign me to a channel using `!set_channel` or `!set`")
            return False
        if ctx.channel.id != self.channels[ctx.guild.id].id:
            await ctx.channel.send("Wrong channel buddy")
            return False
        return True
