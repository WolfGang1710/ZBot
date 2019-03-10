import discord, re
from discord.ext import commands

class tempdelta(commands.converter.IDConverter):
    def __init__(self):
        pass
    
    async def convert(self,ctx,argument):
        d = 0
        found = False
        # ctx.invoked_with
        for x in [('y',3.154e+7),('d',86400),('h',3600),('m',60)]:
            r = re.search(r'(\d+)'+x[0],argument)
            if r!= None:
                d += int(r.group(1))*x[1]
                found = True
        if not found:
            raise commands.errors.BadArgument('Invalid duration: '+argument)
        return d

class user(commands.converter.IDConverter):
    def __init__(self):
        pass
    
    async def convert(self,ctx,argument):
        if argument.isnumeric():
            res = ctx.bot.get_user(int(argument))
            if res == None:
                try:
                    res = await ctx.bot.get_user_info(int(argument))
                except:
                    pass
            return res
        return await commands.UserConverter().convert(ctx,argument)

class infoType(commands.converter.IDConverter):
    def __init__(self):
        pass
    
    async def convert(self,ctx,argument):
        if argument in ['member','role','user','textchannel','channel','invite','voicechannel','emoji','category','guild','server']:
            return argument
        else:
            raise commands.errors.BadArgument('Invalid type: '+argument)