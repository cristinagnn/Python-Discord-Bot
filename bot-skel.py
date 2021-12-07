#!./.venv/bin/python3

import argparse
import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator
import pathlib
from discord.ext import commands    # Bot class and utils


parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", help="provide token as argument")
args = parser.parse_args()
 
################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################
 
# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }
 
    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }
 
    # get information about call site
    caller = inspect.stack()[1]
 
    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return
 
    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))
 
################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################
 
# bot instantiation
bot = commands.Bot(command_prefix='!')
 
# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')
 
# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return
 
    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')
 
    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)

#checking if he is left alone :'(

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    # Checking if the bot is connected to a channel and if there is only 1 member connected to it (the bot itself)
    if voice_state is not None and len(voice_state.channel.members) == 1:
        await voice_state.disconnect()

 
# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')
 
    await ctx.send(random.randint(1, max_val))
 
# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))

#starting the bot talent show

@bot.command(brief='Play a song')
async def play(ctx, name : str):
    user = ctx.message.author
    vc = user.voice.channel

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) # This allows for more functionality with voice channels

    if voice == None: # None being the default value if the bot isnt in a channel (which is why the is_connected() is returning errors)
        await vc.connect()
        await ctx.send(f"Joined **{vc}**")

    song = f"music/{name}.mp3"

    if not os.path.exists(song):
        await ctx.send(f"Song **{name}** does not exist.")
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio(song))

@play.error
async def play_error(ctx, error):
    await ctx.send(str(error))

#kindly telling the bot to shut up

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

@stop.error
async def stop_error(ctx, error):
    await ctx.send(str(error))

#checking what's on the menu

@bot.command(brief='list of songs')
async def list(ctx):
    for file in os.listdir("music"):
        if file.endswith(".mp3"):
            await ctx.send(pathlib.Path(file).stem)


@list.error
async def list_error(ctx, error):
    await ctx.send(str(error))

#nicely telling the bot to go away

@bot.command()
async def scram(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@scram.error
async def scram_error(ctx, error):
    await ctx.send(str(error))



 
if __name__ == '__main__':
    if args.token:
        bot.run(args.token)
    else:
        # check that token exists in environment
        if 'BOT_TOKEN' not in os.environ:
            log_msg('save your token in the BOT_TOKEN env variable!', 'error')
            exit(-1)
    
        # launch bot (blocking operation)
        bot.run(os.environ['BOT_TOKEN'])