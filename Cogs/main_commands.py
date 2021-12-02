import asyncio
import sqlite3
import discord
from main import bot
from discord.ext import commands

class VoteModeration(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def multiply(self, ctx, a: int, b: int):
        await ctx.send(a*b)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(str(round(bot.latency * 1000, 2)) + ' ms')

    @commands.command()
    async def voteban(self, ctx, user: discord.Member, time: int, *, reason):
        reacts = [0, 0]
        e = discord.Embed(
            title=f'Голосование за бан!',
            description=f'Пользователь {ctx.message.author.mention} предложил забанить пользователя {user.mention}',
            colour=discord.Colour.random()
        )
        e.add_field(name='Причина:', value=f'{reason}', inline=True)
        poll_message = await ctx.send(embed=e)

        await poll_message.add_reaction('👍')
        await poll_message.add_reaction('👎')
        await asyncio.sleep(time)

        message = await ctx.channel.fetch_message(poll_message.id)
        for react, i in zip(message.reactions, range(2)):
            reacts[i] = react.count

        if ((reacts[0] / reacts[1]) * 100) > 50:
            if reacts[0] == reacts[1]:
                e = discord.Embed(description='Голоса разделились поровну')
                await ctx.send(embed=e)
                return

            db_connect = sqlite3.connect('banlist.sqlite')
            cursor = db_connect.cursor()
            cursor.execute(f'INSERT INTO banlist(guild_id, user_id) VALUES'
                           f'(\'{ctx.guild.id}\', \'{user.id}\')')
            db_connect.commit()
            cursor.close()

            await user.ban(reason=reason)
            e = discord.Embed(description=f'Время голосования подошло к концу. Пользователь {user} был выгнан с сервера!')

            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                description=f'Время голосования подошло к концу. Процент голосов за бан составляет всего {round((reacts[0] / reacts[1]) * 100, 2)}%'
            )
            await ctx.send(embed = e)
            return


    @commands.command()
    async def voteunban(self, ctx, user_id: int):
        reacts = [0, 0]

        db = sqlite3.connect('banlist.sqlite')
        cursor = db.cursor()
        info = cursor.execute('SELECT * FROM banlist WHERE user_id=?', (user_id,))
        print(info.fetchone())
        print(user_id)

        if info.fetchone() is None:
            await ctx.send(embed=discord.Embed(description='Пользователя нет в бан-листе (в базе данных)'))
            return
        else:
            user = await bot.fetch_user(user_id)

        e = discord.Embed(
            title=f'Голосование за разбан!',
            description=f'Пользователь {ctx.message.author.mention} предложил разбанить пользователя {user}!',
            colour=discord.Colour.random()
        )
        poll_message = await ctx.send(embed=e)

        await poll_message.add_reaction('👍')
        await poll_message.add_reaction('👎')
        await asyncio.sleep(10)

        message = await ctx.channel.fetch_message(poll_message.id)
        for react, i in zip(message.reactions, range(2)):
            reacts[i] = react.count

        if ((reacts[0] / reacts[1]) * 100) > 50:
            if reacts[0] == reacts[1]:

                e = discord.Embed(description='Голоса разделились поровну!')
                await ctx.send(embed=e)
                return

            await ctx.guild.unban(user)
            e = discord.Embed(description=f'Время голосования подошло к концу. Пользователь {user} был разбанен!')

            await ctx.send(embed=e)
        else:
            e = discord.Embed(
                description=f'Время голосования подошло к концу. Процент голосов за бан составляет всего {round((reacts[0] / reacts[1]) * 100, 2)}%'
            )
            await ctx.send(embed = e)
            return

    @commands.command()
    async def morgen(self, ctx):
        await ctx.send(file=discord.File('morgen.jpg'))

    @commands.command()
    async def poll(self, ctx, string, time: float):
        reacts = [0, 0]
        e = discord.Embed(
            title=f'Голосование!',
            description=string,
            colour=discord.Colour.random()
        )
        poll_message = await ctx.send(embed=e)

        await poll_message.add_reaction('👍')
        await poll_message.add_reaction('👎')
        await asyncio.sleep(time)

        message = await ctx.channel.fetch_message(poll_message.id)
        for react, i in zip(message.reactions, range(2)):
            reacts[i] = react.count

        await ctx.send(f"Процент голосов \"за\" равен {round((reacts[0] / reacts[1]) * 100, 2)}%")

    @commands.command(aliases=['a', 'useravatar'], brief='Gets user\'s avatar')
    async def avatar(self, ctx, *, user: discord.Member = None):
        if user == None:
            e = discord.Embed(colour=0xB22222, title='Not enough arguments! Mention the user!')
            await ctx.send(embed=e)
            return
        else:
            avatar = user.avatar_url
            await ctx.send(avatar)


def setup(client):
    client.add_cog(VoteModeration(client))