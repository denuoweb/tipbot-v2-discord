import discord
from discord.ext import commands
from utils import checks, parsing

class Help:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot        
        bot.remove_command('help')
        config = parsing.parse_json('config.json')        
        self.prefix = config["prefix"]
        self.bot_descr = config["description"]

    @commands.command(pass_context=True)
    async def help(self, ctx):
        """
        Displays a useful list of commands.
        """
        desc = ""
        for key in self.bot.commands.keys():
            command = self.bot.get_command(key)
            if command.hidden and not checks.is_owner(ctx):
                continue

            if command.aliases:
                desc += "`{}{}`".format(self.prefix, command.name)+" - {}\nAliases: `{}`\n".format(command.short_doc,
                ",".join(command.aliases))
                desc += "\n"

            elif command.short_doc:
                desc += "`{}{}`".format(self.prefix, command.name)+" - {}\n".format(command.short_doc)
                desc += "\n"

            else:
                desc += "`{}{}`\n".format(self.prefix, command.name)
                desc += "\n"

        embed = discord.Embed(description=desc)
        bot_name="{} commands!".format(self.bot_descr)
        embed.set_author(icon_url=self.bot.user.avatar_url, name=bot_name)
        try:
            await self.bot.send_message(ctx.message.author, embed=embed)
            if ctx.message.server is not None:
                await self.bot.say("{}, I PMed you some helpful info! Make sure to double check that it is from me!".format(ctx.message.author.mention))
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(Help(bot))