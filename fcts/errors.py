import discord, sys, traceback, random, re
from discord.ext import commands


class ErrorsCog(commands.Cog):
    """General cog for error management."""

    def __init__(self,bot):
        self.bot = bot
        self.file = "errors"
        try:
            self.translate = self.bot.cogs["LangCog"].tr
        except:
            pass
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.translate = self.bot.cogs["LangCog"].tr

    async def search_err(self,form:list,sentence:str):
        for x in form:
            r = re.search(x,sentence)
            if r!= None:
                return r

    async def on_cmd_error(self,ctx,error):
        """The event triggered when an error is raised while invoking a command."""
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return
        
        ignored = (commands.errors.CommandNotFound,commands.errors.CheckFailure,commands.errors.ConversionError,discord.errors.Forbidden)
        actually_not_ignored = (commands.errors.NoPrivateMessage)
        
        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored) and not isinstance(error,actually_not_ignored):
            if self.bot.beta:
                c = str(type(error)).replace("<class '",'').replace("'>",'')
                await ctx.send('`Ignored error:` [{}] {}'.format(c,error))
            return
        elif isinstance(error,commands.errors.CommandOnCooldown):
            if await self.bot.cogs['AdminCog'].check_if_admin(ctx):
                await ctx.reinvoke()
                return
            await ctx.send(await self.translate(ctx.channel,'errors','cooldown',d=round(error.retry_after,2)))
            return
        elif isinstance(error,(commands.BadArgument,commands.BadUnionArgument)):
            raw_error = str(error).replace('@eveyrone','@​everyone').replace('@here','@​here')
            # Could not convert "limit" into int. OR Converting to "int" failed for parameter "number".
            r = re.search(r'Could not convert \"(?P<arg>[^\"]+)\" into (?P<type>[^.\n]+)',raw_error)
            if r==None:
                r = re.search(r'Converting to \"(?P<type>[^\"]+)\" failed for parameter \"(?P<arg>[^.\n]+)\"',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','badarguments',p=r.group('arg'),t=r.group('type')))
            # zzz is not a recognised boolean option
            r = re.search(r'(?P<arg>[^\"]+) is not a recognised (?P<type>[^.\n]+) option',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','badarguments-2',p=r.group('arg'),t=r.group('type')))
            # Member "Z_runner" not found
            r = re.search(r'Member \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','membernotfound',m=r.group(1)))
            # User "Z_runner" not found
            r = re.search(r'User \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','usernotfound',u=r.group(1)))
            # Role "Admin" not found
            r = re.search(r'Role \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','rolenotfound',r=r.group(1)))
            # Emoji ":shock:" not found
            r = re.search(r'Emoji \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','emojinotfound',e=r.group(1)))
             # Colour "blue" is invalid
            r = re.search(r'Colour \"([^\"]+)\" is invalid',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidcolor',c=r.group(1)))
            # Channel "twitter" not found.
            r = re.search(r'Channel \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','channotfound',c=r.group(1)))
            # Message "1243" not found.
            r = re.search(r'Message \"([^\"]+)\" not found',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','msgnotfound',msg=r.group(1)))
            # Too many text channels
            if raw_error=='Too many text channels':
                return await ctx.send(await self.translate(ctx.channel,'errors','toomanytxtchan'))
            # Invalid duration: 2d
            r = re.search(r'Invalid duration: ([^\" ]+)',raw_error)
            if r != None:
                return await ctx.send(await self.translate(ctx.channel,'errors','duration',d=r.group(1)))
            # Invalid invite: nope
            r = re.search(r'Invalid invite: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidinvite',i=r.group(1)))
            # Invalid guild: test
            r = re.search(r'Invalid guild: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidguild',g=r.group(1)))
            # Invalid url: nou
            r = re.search(r'Invalid url: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidurl',u=r.group(1)))
            # Invalid leaderboard type: lol
            r = re.search(r'Invalid leaderboard type: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidleaderboard'))
            # Invalid ISBN: lol
            r = re.search(r'Invalid ISBN: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidisbn'))
            # Invalid emoji: lmao
            r = re.search(r'Invalid emoji: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidemoji'))
            # Invalid message ID: 007
            r = re.search(r'Invalid message ID: (\S+)',raw_error)
            if r!=None:
                return await ctx.send(await self.translate(ctx.channel,'errors','invalidmsgid'))
            print('errors -',error)
        elif isinstance(error,commands.MissingRequiredArgument):
            await ctx.send(await self.translate(ctx.channel,'errors','missingargument',a=error.param.name,e=random.choice([':eyes:','',':confused:',':thinking:',''])))
            return
        elif isinstance(error,commands.DisabledCommand):
            await ctx.send(await self.translate(ctx.channel,'errors','disabled',c=ctx.invoked_with))
            return
        elif isinstance(error,commands.errors.NoPrivateMessage):
            await ctx.send(await self.translate(ctx.channel,'errors','DM'))
            return
        else:
            try:
                raw_error = str(error).replace('@eveyrone','@​everyone').replace('@here','@​here')
                await ctx.send("`ERROR:` {}".format(raw_error))
            except Exception as newerror:
                self.bot.log.info("[on_cmd_error] Can't send error on channel {}: {}".format(ctx.channel.id,newerror))
        # All other Errors not returned come here... And we can just print the default TraceBack.
        self.bot.log.warning('Ignoring exception in command {}:'.format(ctx.message.content))      
        await self.on_error(error,ctx)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await self.on_cmd_error(ctx,error)

    @commands.Cog.listener()
    async def on_error(self,error,ctx=None):
        try:
            if isinstance(ctx,discord.Message):
                ctx = await self.bot.get_context(ctx)
            tr = traceback.format_exception(type(error), error, error.__traceback__)
            msg = "```python\n{}\n```".format(" ".join(tr))
            if ctx == None:
                await self.senf_err_msg(f"Internal Error\n{msg}")
            elif ctx.guild == None:
                await self.senf_err_msg(f"DM | {ctx.channel.recipient.name}\n{msg}")
            elif ctx.channel.id==625319425465384960:
                return await ctx.send(ctx.guild.name+" | "+ctx.channel.name+"\n"+msg)
            else:
                await self.senf_err_msg(ctx.guild.name+" | "+ctx.channel.name+"\n"+msg)
        except Exception as e:
            self.bot.log.warn(f"[on_error] {e}", exc_info=True)
        try:
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
        except Exception as e:
            self.bot.log.warning(f"[on_error] {e}", exc_info=True)


    async def senf_err_msg(self,msg):
        """Envoie un message dans le salon d'erreur"""
        salon = self.bot.get_channel(626039503714254858)
        if salon == None:
            return False
        if len(msg)>2000:
            if msg.endswith("```"):
                msg = msg[:1997]+"```"
            else:
                msg = msg[:2000]
        await salon.send(msg)
        return True


def setup(bot):
    bot.add_cog(ErrorsCog(bot))
