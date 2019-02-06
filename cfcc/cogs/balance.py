import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing, checks

#result_set = database response with parameters from query
#db_bal = nomenclature for result_set["balance"]
#snowflake = snowflake from message context, identical to user in database
#wallet_bal = nomenclature for wallet reponse

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Balance:

    def __init__(self, bot):
        self.bot = bot
        config = parsing.parse_json('config.json')
        self.currency_symbol = config["currency_symbol"]
        self.stake_id = config["stake_bal"]
        self.donate = config["donation"]
        self.coin_name = config["currency_name"]
        self.bot_name = config["description"]
        #parse the embed section of the config file
        embed_config = parsing.parse_json('config.json')["embed_msg"]
        self.thumb_embed = embed_config["thumb_embed_url"]
        self.footer_text = embed_config["footer_msg_text"]
        self.embed_color = int(embed_config["color"], 16)

    #private balance view
    async def do_embed(self, name, server, db_bal, db_bal_unconfirmed, stake_total, donate_total):
        # Simple embed function for displaying username and balance
        embed=discord.Embed(title="You requested your **Balance**", color=self.embed_color)
        embed.set_author(name=self.bot_name)
        embed.add_field(name="User", value=name.mention, inline=False)
        embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(db_bal), 8),self.currency_symbol))
        embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        if float(db_bal_unconfirmed) != 0.0:
            embed.add_field(name="Unconfirmed Deposits", value="{:.8f} {}".format(round(float(db_bal_unconfirmed), 8),self.currency_symbol))
        if float(stake_total) != 0.0:
            embed.add_field(name="Your Total Staking Rewards", value="{:.8f} {}".format(round(float(stake_total), 8),self.currency_symbol))
        if float(donate_total) != 0.0:
            embed.add_field(name="Your Total Donations", value="{:.8f} {}".format(round(float(donate_total), 8),self.currency_symbol))
        embed.set_footer(text=self.footer_text)
        try:
            await self.bot.send_message(name, embed=embed)
            if server is not None:
                await self.bot.say("{}, I PMed you your **Balance**! Make sure to double check that it is from me!".format(name.mention))
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    #public balance view
    async def do_showembed(self, name, db_bal, db_bal_unconfirmed, stake_total, donate_total):
        # Simple embed function for displaying username and balance
        embed=discord.Embed(title="You requested your **Balance**", color=self.embed_color)
        embed.set_author(name=self.bot_name)
        embed.add_field(name="User", value=name.mention, inline=False)
        embed.add_field(name="Balance", value="{:.8f} {}".format(round(float(db_bal), 8),self.currency_symbol))
        embed.set_thumbnail(url="http://{}".format(self.thumb_embed))
        if float(db_bal_unconfirmed) != 0.0:
            embed.add_field(name="Unconfirmed Deposits", value="{:.8f} {}".format(round(float(db_bal_unconfirmed), 8),self.currency_symbol))
        if float(stake_total) != 0.0:
            embed.add_field(name="Your Total Staking Rewards", value="{:.8f} {}".format(round(float(stake_total), 8),self.currency_symbol))
        if float(donate_total) != 0.0:
            embed.add_field(name="Your Total Donations", value="{:.8f} {}".format(round(float(donate_total), 8),self.currency_symbol))
        embed.set_footer(text=self.footer_text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    @commands.command(pass_context=True)
    async def balance(self, ctx):
        """Display your balance"""
        # Set important variables
        snowflake = ctx.message.author.id

        # Check if user exists in db
        mysql.check_for_user(snowflake)

        balance = mysql.get_balance(snowflake, check_update=True)
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        # get the users staking rewards
        stakes =  mysql.get_tip_amounts_from_id(self.stake_id, snowflake)

        # get the users donated amount
        donations = mysql.get_tip_amounts_from_id(snowflake, self.donate)

        # Execute and return SQL Query
        await self.do_embed(ctx.message.author, ctx.message.server, balance, balance_unconfirmed, sum(stakes), sum(donations))

    @commands.command(pass_context=True)
    async def bal(self, ctx):
        """Display your balance"""
        # Set important variables
        snowflake = ctx.message.author.id

        # Check if user exists in db
        mysql.check_for_user(snowflake)

        balance = mysql.get_balance(snowflake, check_update=True)
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        # get the users staking rewards
        stakes =  mysql.get_tip_amounts_from_id(self.stake_id, snowflake)

        # get the users donated amount
        donations = mysql.get_tip_amounts_from_id(snowflake, self.donate)

        # Execute and return SQL Query
        await self.do_embed(ctx.message.author, ctx.message.server, balance, balance_unconfirmed, sum(stakes), sum(donations))

    @commands.command(pass_context=True)
    async def showbal(self, ctx):
        """Display your balance"""
        # Set important variables
        snowflake = ctx.message.author.id

        # Check if user exists in db
        mysql.check_for_user(snowflake)

        balance = mysql.get_balance(snowflake, check_update=True)
        balance_unconfirmed = mysql.get_balance(snowflake, check_unconfirmed = True)

        # get the users staking rewards
        stakes =  mysql.get_tip_amounts_from_id(self.stake_id, snowflake)

        # get the users donated amount
        donations = mysql.get_tip_amounts_from_id(snowflake, self.donate)

        # Execute and return SQL Query
        await self.do_showembed(ctx.message.author, balance, balance_unconfirmed, sum(stakes), sum(donations))

def setup(bot):
    bot.add_cog(Balance(bot))
