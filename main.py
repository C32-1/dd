import discord
from dbot_manipulations import Manipulator
from discord.ext import commands
import os
import sqlite3

command_list = 'voteban voteunban multiply ping help'.split()

def _load_cogs_void():
    for name in os.listdir('./Cogs'):
        if name.endswith('.py'):
            bot.load_extension(f'Cogs.{name[:-3]}')

def _find_commands(cmds, command):
    iterator = iter(cmds)
    d = {'voteban': 0, 'voteunban': 0, 'multiply': 0, 'ping': 0, 'help': 0}

    def cycle_next(iterate):
        word = next(iterate)
        ind = cmds.index(word)

        for let in command:
            if let in cmds[ind]:
                d[word] += word.count(let)

    for i in range(len(cmds)):
        cycle_next(iterator)

    return d


config = Manipulator('config.json')
main_data = config.get_data()
load_cogs = main_data['main'][0]['cogs_load']
del config

class DBot(commands.AutoShardedBot):

    async def on_ready(self):
        print(f'Bot started with name {bot.user}')
        await bot.change_presence(activity=discord.Game(name='Born to die'))

    async def on_command_error(self, ctx, exception):
        command = str(exception).split()[1].replace('"', '')

        if isinstance(exception, commands.CommandNotFound):
            if len(command) >= 10 or len(command) <= 2:
                await ctx.send('Похоже, такой команды не существует!')
                return

            dct = _find_commands(command_list, command=command)
            if 0 >= dct[max(dct)] <= 3:

                await ctx.send('Похоже, такой команды не существует!')
                return
            await ctx.send(f'Команда не найдена! Может имели ввиду "{max(dct, key=dct.get)}"?')


bot = DBot(command_prefix=main_data['main'][0]['default_pref'], case_insensitive = False)


if __name__ == '__main__':
    if load_cogs:
        try:
            _load_cogs_void()
            print('Cogs was loaded correctly!')
        except Exception:
            print('Error!')

    bot.run(main_data['main'][0]['token'])
