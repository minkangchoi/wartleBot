from discord.ext import commands

class Setup(commands.Cog):

    """
    debug_mode: If True, set guild and channel to only test server
    """
    debug_mode = False
    debug_channel = -1

    def __init__(self, bot, debug_mode, debug_guild, debug_channel):
        self.bot = bot
        self.debug_mode = debug_mode
        self.debug_guild = debug_guild
        self.debug_channel = debug_channel
        self.wartleBot = self.bot.get_cog('WartleBot')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')
        if self.debug_mode:
            print("Debug Mode activated")
            self.wartleBot.channels = {int(self.debug_guild): self.bot.get_channel(int(self.debug_channel))}
        # Else populate channels dict defaulted to None
        else:
            for guild in self.bot.guilds:
                self.wartleBot.channels[guild.id] = None

    @commands.command(aliases=["set"])
    async def set_channel(self, ctx):
        self.wartleBot.channels[ctx.guild.id] = ctx.channel
        await ctx.channel.send("I live here now")

    @commands.command()
    async def help(self, ctx):
        await ctx.channel.send(
            "Use at `!rules` and `!coms` for more info!"
        )
