from discord.ext import commands

class Help(commands.Cog):

    """
    Lists all commands with descriptions
    """
    @commands.command()
    async def coms(self, ctx):
        await ctx.channel.send(
            "**Setup Commands:**\n" +
            "`!set_channel`, `!set`: The text channel you send this command on will become the one that hosts the game\n\n" +
            "**Game Commands**\n" +
            "`!start_game <word length>`, `!start <word length>`: Start the Wartle game with a random word with size <word length>\n" +
            "`!join`, `!j`: Join the current Wartle\n" +
            "`!guess <word>`, `!g <word>`: Guess a word, carrots are not included\n" +
            "`!remaining`, `!r`: Check number of remaining guesses\n" +
            "`!correct`, `!c`: View the word comprised of green letters from all previous guess\n" +
            "`!history`, `!h`: View all previous guesses\n" +
            "`!letters`, `!l`: View letters with corresponding colors"
        )
    
    @commands.command()
    async def rules(self, ctx):
        await ctx.channel.send(
            "**Objective**\n" +
            "Guess the word given a certain amount of tries. For each guess, colors will show for each corresponding letters giving you clues to the correct word.\n\n" +
            "**Letter Colors**\n" +
            ":green_square:: Letter is in the word and **is** in the correct spot\n" +
            ":yellow_square:: Letter is in the word but **is not** in the correct spot\n" +
            ":white_large_square:: Letter is not in the word\n" +
            ":black_large_square:: Letter has not been guessed yet\n\n"
            "For list of commands, use `!coms`."
        )
