import discord, random, operator, string, importlib, re, typing, datetime, subprocess, json, geocoder, time, aiohttp, copy
import emoji as emojilib
from discord.ext import commands
from tzwhere import tzwhere
from pytz import timezone

from fcts import emojis, checks, args
importlib.reload(emojis)
importlib.reload(checks)
importlib.reload(args)
from fcts.checks import is_fun_enabled

cmds_list = ['count_msg','ragequit','pong','run','nope','blame','party','bigtext','shrug','gg','money','pibkac','osekour','me','kill','cat','rekt','thanos','nuke','pikachu','pizza','google','loading','piece','roll','afk']


async def can_say(ctx):
    if not ctx.bot.database_online:
        return ctx.channel.permissions_for(ctx.author).administrator
    else:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"say")

async def can_use_cookie(ctx):
#                            Z_runner           neil3000            Awhikax           Adri526         Theventreur         Catastrophix        Platon_Neutron      megat69            Aragorn1202
    return ctx.author.id in [279568324260528128,278611007952257034,281404141841022976,409470110131027979,229194747862843392,438372385293336577,286827468445319168,517762101859844106,375598088850505728]

class FunCog(commands.Cog):
    """Add some fun commands, no obvious use. You can disable this module with the 'enable_fun' option (command 'config')"""

    def __init__(self,bot):
        self.bot = bot
        self.fun_opt = dict()
        self.file = "fun"
        self.tz = tzwhere.tzwhere(forceTZ=True)
        self.last_roll = None
        self.afk_guys = dict()
        try:
            self.translate = self.bot.cogs["LangCog"].tr
        except:
            pass
        try:
            self.utilities = self.bot.cogs["UtilitiesCog"]
        except:
            pass

    async def cache_update(self,id,value):
        self.fun_opt[str(id)] = value

    @commands.Cog.listener()
    async def on_ready(self):
            self.translate = self.bot.cogs["LangCog"].tr
            self.utilities = self.bot.cogs["UtilitiesCog"]

    async def is_on_guild(self,user,guild):
        if self.bot.user.id == 436835675304755200:
            return True
        if user.id in [279568324260528128,392766377078816789,281404141841022976]:
            return True
        server = self.bot.get_guild(guild)
        if server != None:
            return user in server.members
        return False
    
    

    @commands.command(name='fun')
    async def main(self,ctx):
        """Get a list of all fun commands"""
        if not await is_fun_enabled(ctx):
            if ctx.bot.database_online:
                await ctx.send(await self.translate(ctx.channel,"fun","no-fun"))
            else:
                await ctx.send(await self.translate(ctx.channel,"fun","no-database"))
            return
        title = await self.translate(ctx.channel,"fun","fun-list")
        if self.bot.current_event=="fish":
            title = ":fish: "+title
        text = str()
        for cmd in sorted(self.get_commands(),key=operator.attrgetter('name')):
            if cmd.name in cmds_list and cmd.enabled:
                if cmd.help != None:
                    text+="\n- {} *({})*".format(cmd.name,cmd.help.split('\n')[0])
                else:
                    text+="\n- {}".format(cmd.name)
                if type(cmd)==commands.core.Group:
                    for cmds in cmd.commands:
                        text+="\n    - {} *({})*".format(cmds.name,cmds.help)
        if ctx.guild==None or ctx.channel.permissions_for(ctx.guild.me).embed_links:
            emb = await ctx.bot.cogs['EmbedCog'].Embed(title=title,desc=text,color=ctx.bot.cogs['HelpCog'].help_color,time=ctx.message.created_at).create_footer(ctx)
            return await ctx.send(embed=emb.discord_embed())
        await ctx.send(title+text)

    @commands.command(name='roll',hidden=True)
    @commands.check(is_fun_enabled)
    async def roll(self,ctx,*,options):
        """Selects an option at random from a given list
        The options must be separated by a semicolon `;`"""
        liste = [x for x in [x.strip() for x in options.split(';')] if len(x)>0]
        if len(liste)==0:
            return await ctx.send(await self.translate(ctx.channel,"fun","no-roll"))
        choosen = None
        while choosen==self.last_roll:
            choosen = random.choice(liste).replace('@everyone','@​everyone').replace('@here','@​here')
        await ctx.send(choosen)

    @commands.command(name="cookie",aliases=['cookies'],hidden=True)
    @commands.check(can_use_cookie)
    @commands.check(is_fun_enabled)
    async def cookie(self,ctx):
        """COOKIE !!!"""
        if ctx.author.id == 375598088850505728:
            await ctx.send(file=await self.utilities.find_img("cookie-target.gif"))
        else:
            await ctx.send(str(await self.translate(ctx.guild,"fun","cookie")).format(ctx.author.mention,self.bot.cogs['EmojiCog'].customEmojis['cookies_eat']))


    @commands.command(name="count_msg",hidden=True)
    @commands.check(is_fun_enabled)
    @commands.cooldown(5, 30, type=commands.BucketType.channel)
    async def count(self,ctx,limit:typing.Optional[int]=1000,user:typing.Optional[discord.User]=None,channel:typing.Optional[discord.TextChannel]=None):
        """Count the number of messages sent by the user
You can specify a verification limit by adding a number in argument (up to 1.000.000)"""
        l = 1000000
        if channel==None:
            channel = ctx.channel
        if not channel.permissions_for(ctx.author).read_message_history:
            await ctx.send(await self.translate(ctx.channel,'fun','count-5'))
            return
        if user!=None and user.name.isnumeric() and limit==1000:
            limit = int(user.name)
            user = None
        if limit > l:
            await ctx.send(await self.translate(ctx.channel,"fun","count-2",l=l,e=self.bot.cogs['EmojiCog'].customEmojis['wat']))
            return
        if ctx.guild!=None and not channel.permissions_for(ctx.guild.me).read_message_history:
            await ctx.send(await self.translate(channel,"fun","count-3"))
            return
        if user==None:
            user = ctx.author
        counter = 0
        tmp = await ctx.send(await self.translate(ctx.channel,'fun','count-0'))
        m = 0
        async for log in channel.history(limit=limit):
            m += 1
            if log.author == user:
                counter += 1
        r = round(counter*100/m,2)
        if user==ctx.author:
            await tmp.edit(content = await self.translate(ctx.channel,'fun','count-1',limit=m,x=counter,p=r))
        else:
            await tmp.edit(content = await self.translate(ctx.channel,'fun','count-4', limit=m,user=user.display_name,x=counter,p=r))

    @commands.command(name="ragequit",hidden=True)
    @commands.check(is_fun_enabled)
    async def ragequit(self,ctx):
        """To use when you get angry - limited to certain members"""
        await ctx.send(file=await self.utilities.find_img('ragequit{0}.gif'.format(random.randint(1,6))))

    @commands.command(name="run",hidden=True)
    @commands.check(is_fun_enabled)
    async def run(self,ctx):
        """"Just... run... very... fast"""
        await ctx.send("ε=ε=ε=┏( >_<)┛")

    @commands.command(name="pong",hidden=True)
    @commands.check(is_fun_enabled)
    async def pong(self,ctx):
        """Ping !"""
        await ctx.send("Ping !")

    @commands.command(name="nope",hidden=True)
    @commands.check(is_fun_enabled)
    async def nope(self,ctx):
        """Use this when you do not agree with someone else"""
        await ctx.send(file=await self.utilities.find_img('nope.png'))
        if self.bot.database_online:
            if await self.bot.cogs["ServerCog"].staff_finder(ctx.author,'say'):
                await self.utilities.suppr(ctx.message)

    @commands.command(name="blame",hidden=True)
    @commands.check(is_fun_enabled)
    async def blame(self,ctx,name):
        """Blame someone
        Use 'blame list' command to see every available name *for you*"""
        l1 = ['discord','mojang','zbot','google','youtube'] # tout le monde
        l2 = ['tronics','patate','neil','reddemoon','aragorn1202','platon'] # frm
        l3 = ['awhikax','aragorn','adri','zrunner'] # zbot
        name = name.lower()
        if name in l1:
            await ctx.send(file=await self.utilities.find_img('blame-{}.png'.format(name)))
        elif name in l2:
            if await self.is_on_guild(ctx.author,391968999098810388): # fr-minecraft
                await ctx.send(file=await self.utilities.find_img('blame-{}.png'.format(name)))
        elif name in l3:
            if await self.is_on_guild(ctx.author,356067272730607628): # Zbot server
                await ctx.send(file=await self.utilities.find_img('blame-{}.png'.format(name)))
        elif name in ['help','list']:
            liste = l1
            if await self.is_on_guild(ctx.author,391968999098810388): # fr-minecraft
                liste += l2
            if await self.is_on_guild(ctx.author,356067272730607628): # Zbot server
                liste += l3
            txt = "- "+"\n- ".join(sorted(liste))
            title = str(await self.translate(ctx.channel,"fun","blame-0")).format(ctx.author)
            if ctx.guild==None or ctx.channel.permissions_for(ctx.guild.me).embed_links:
                emb = self.bot.cogs["EmbedCog"].Embed(title=title,desc=txt,color=self.bot.cogs["HelpCog"].help_color).update_timestamp()
                await ctx.send(embed=emb.discord_embed())
            else:
                await ctx.send("__{}:__\n\n{}".format(title,txt))

    @commands.command(name="kill",hidden=True)
    @commands.guild_only()
    @commands.check(is_fun_enabled)
    async def kill(self,ctx,*,name=None):
        if name == None:
            victime = ctx.author.display_name
            ex = ctx.author.display_name.replace(" ","_")
        else:
            victime = name.replace('@everyone','@​everyone').replace('@here','@​here')
            ex = name.replace(" ","_")
        author = ctx.author.mention
        liste = await self.translate(ctx.channel,"kill","list")
        msg = random.choice(liste)
        tries = 0
        while '{0}' in msg and name == None and tries<50:
            msg = random.choice(liste)
            tries += 1
        await ctx.send(msg.format(author,victime,ex))

    @commands.command(name="arapproved",aliases=['arapprouved'],hidden=True)
    @commands.check(lambda ctx: ctx.author.id in [375598088850505728,279568324260528128])
    async def arapproved(self,ctx):
        await ctx.send(file=await self.utilities.find_img("arapproved.png"))

    @commands.command(name='party',hidden=True)
    @commands.check(is_fun_enabled)
    async def party(self,ctx):
        """Sends a random image to make the server happier"""
        r = random.randrange(5)+1
        if r == 1:
            await ctx.send(file=await self.utilities.find_img('cameleon.gif'))
        elif r == 2:
            await ctx.send(file=await self.utilities.find_img('discord_party.gif'))
        elif r == 3:
            await ctx.send(file=await self.utilities.find_img('parrot.gif'))
        elif r == 4:
            e = self.bot.cogs['EmojiCog'].customEmojis['blob_dance']
            await ctx.send(e*5)
        elif r == 5:
            await ctx.send(file=await self.utilities.find_img('cameleon.gif'))

    @commands.command(name="cat",hidden=True)
    @commands.check(is_fun_enabled)
    async def cat_gif(self,ctx):
        """Wow... So cuuuute !"""
        await ctx.send(random.choice(['http://images6.fanpop.com/image/photos/40800000/tummy-rub-kitten-animated-gif-cute-kittens-40838484-380-227.gif',
        'http://25.media.tumblr.com/7774fd7794d99b5998318ebd5438ba21/tumblr_n2r7h35U211rudcwro1_400.gif',
        'https://www.2tout2rien.fr/wp-content/uploads/2014/10/37-pestes-de-chats-mes-bonbons.gif',
        'https://snowchvojnica.eu/assets/cat.gif',
        'http://coquelico.c.o.pic.centerblog.net/chat-peur.gif',
        'https://tenor.com/view/nope-bye-cat-leave-done-gif-12387359']))
    
    @commands.command(name="bigtext",hidden=True)
    @commands.check(is_fun_enabled)
    async def big_text(self,ctx,*,text):
        """If you wish to write bigger"""
        contenu = await self.bot.cogs['UtilitiesCog'].clear_msg(text,ctx=ctx)
        text = ""
        Em = self.bot.cogs['EmojiCog']
        mentions = [x.group(1) for x in re.finditer(r'(<(?:@!?&?|#|a?:[a-zA-Z0-9]+:)\d+>)',ctx.message.content)]
        content = "¬¬".join(contenu.split("\n"))
        for x in mentions:
            content = content.replace(x,'¤¤')
        for l in content:
            l = l.lower()
            if l in string.ascii_letters:
                item = discord.utils.get(ctx.bot.emojis,id=Em.alphabet[string.ascii_letters.index(l)])
            elif l in string.digits:
                item = discord.utils.get(ctx.bot.emojis,id=Em.numbers[int(l)])
            else:
                try:
                    item = discord.utils.get(ctx.bot.emojis,id=Em.chars[l])
                except KeyError:
                    item = l
            text += str(item)+'¬'
        text = text.replace("¬¬","\n")
        for m in mentions:
            text = text.replace('¤¬¤',m,1)
        text = text.split('¬')[:-1]
        text1 = list()
        for line in text:
            text1.append(line)
            caract = len("".join(text1))
            if caract>1970:
                await ctx.channel.send("".join(text1))
                text1 = []
        if text1 != []:
            await ctx.channel.send(''.join(text1))
        if ctx.bot.database_online and await self.bot.cogs["ServerCog"].staff_finder(ctx.author,'say'):
            await self.bot.cogs["UtilitiesCog"].suppr(ctx.message)
        self.bot.log.debug("{} used bigtext to say {}".format(ctx.author.id,text))
    
    @commands.command(name="shrug",hidden=True)
    @commands.check(is_fun_enabled)
    async def shrug(self,ctx):
        """Don't you know? Neither do I"""
        await ctx.send(file=await self.utilities.find_img('shrug.gif'))
    
    @commands.command(name="rekt",hidden=True)
    @commands.check(is_fun_enabled)
    async def rekt(self,ctx):
        await ctx.send(file=await self.utilities.find_img('rekt.jpg'))

    @commands.command(name="gg",hidden=True)
    @commands.check(is_fun_enabled)
    async def gg(self,ctx):
        """Congrats! You just found something!"""
        await ctx.send(file=await self.utilities.find_img('gg.gif'))
    
    @commands.command(name="money",hidden=True)
    @commands.check(is_fun_enabled)
    async def money(self,ctx):
        await ctx.send(file=await self.utilities.find_img('money.gif'))
    
    @commands.command(name="pibkac",hidden=True)
    @commands.check(is_fun_enabled)
    async def pibkac(self,ctx):
        await ctx.send(file=await self.utilities.find_img('pibkac.png'))
    
    @commands.command(name="osekour",hidden=True,aliases=['helpme','ohmygod'])
    @commands.check(is_fun_enabled)
    async def osekour(self,ctx):
        """Does anyone need help?"""
        l = await self.translate(ctx.channel,"fun","osekour")
        await ctx.send(random.choice(l))

    @commands.command(name="say")
    @commands.guild_only()
    @commands.check(can_say)
    async def say(self,ctx:commands.Context,channel:typing.Optional[discord.TextChannel] = None,*,text):
        """Let the bot say something for you
        You can specify a channel where the bot must send this message. If channel is None, the current channel will be used"""
        if channel==None:
            channel = ctx.channel
        elif not (channel.permissions_for(ctx.author).read_messages and channel.permissions_for(ctx.author).send_messages):
            await ctx.send(await self.translate(ctx.guild,'fun','say-no-perm',channel=channel.mention))
            return
        await self.say_function(ctx,channel,text)
    
    async def say_function(self,ctx:commands.Context,channel:discord.TextChannel,text:str):
        try:
            text = await self.bot.cogs["UtilitiesCog"].clear_msg(text,everyone = not ctx.channel.permissions_for(ctx.author).mention_everyone, ctx=ctx)
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,ctx)
            return
        try:
            if not channel.permissions_for(ctx.guild.me).send_messages:
                return await ctx.send(str(await self.translate(ctx.guild.id,'fun','no-say'))+random.choice([' :confused:','','','']))
            await channel.send(text)
            await self.bot.cogs["UtilitiesCog"].suppr(ctx.message)
        except:
            pass

    @say.error
    async def say_error(self,ctx,error):
        if str(error)!='The check functions for command say failed.':
            await self.say_function(ctx,None,ctx.view.buffer.replace(ctx.prefix+ctx.invoked_with,"",1))

    @commands.command(name="me",hidden=True)
    @commands.check(is_fun_enabled)
    async def me(self,ctx,*,text):
        """No U"""
        text = await self.bot.cogs["UtilitiesCog"].clear_msg(text,everyone=ctx.message.mention_everyone,ctx=ctx)
        await ctx.send("*{} {}*".format(ctx.author.display_name,text))
        if self.bot.database_online and await self.bot.cogs["ServerCog"].staff_finder(ctx.author,"say"):
            await self.bot.cogs["UtilitiesCog"].suppr(ctx.message)
    
    @commands.command(name="react")
    @commands.check(can_say)
    async def react(self,ctx,message:args.guildMessage,*,reactions):
        """Add reaction(s) to a message. Server emojis also work."""
        #try:
        #    msg = await ctx.channel.fetch_message(ID)
        #except discord.errors.HTTPException as e:
        #    await ctx.send(await self.translate(ctx.channel,"fun",'react-0'))
        #    return
        for r in reactions.split():
            try:
                e = await commands.EmojiConverter().convert(ctx,r)
                await msg.add_reaction(e)
            except:
                try:
                    await message.add_reaction(r)
                except discord.errors.HTTPException:
                    await ctx.send(await self.translate(ctx.channel,'fun','no-emoji'))
                    return
                except Exception as e:
                    await self.bot.cogs["ErrorsCog"].on_error(e,ctx)
                    continue
        await self.bot.cogs["UtilitiesCog"].suppr(ctx.message)
    
    @commands.command(name="nuke",hidden=True)
    @commands.check(is_fun_enabled)
    async def nuke(self,ctx):
        """BOOOM"""
        await ctx.send(file=await self.utilities.find_img('nuke.gif'))
    
    @commands.command(name="pikachu",hidden=True)
    @commands.check(is_fun_enabled)
    async def pikachu(self,ctx):
        """Pika-pika ?"""
        await ctx.send(file=await self.utilities.find_img(random.choice(['cookie-pikachu.gif','pika1.gif'])))
    
    @commands.command(name="pizza",hidden=True)
    @commands.check(is_fun_enabled)
    async def pizza(self,ctx):
        """Hey, do U want some pizza?"""
        await ctx.send(file=await self.utilities.find_img('pizza.gif'))
    
    @commands.command(name="google",hidden=True)
    @commands.check(is_fun_enabled)
    async def lmgtfy(self,ctx,*,search):
        """How to use Google"""
        link = "http://lmgtfy.com/?q="+search.replace("\n","+").replace(" ","+").replace('@eveyrone','@+everyone').replace('@here','@+here')
        await ctx.send(link)
        await self.bot.cogs['UtilitiesCog'].suppr(ctx.message)
    
    @commands.command(name="loading",hidden=True)
    @commands.check(is_fun_enabled)
    async def loading(self,ctx):
        """time goes by soooo slowly..."""
        await ctx.send(file=await self.utilities.find_img('loading.gif'))
    
    @commands.command(name="thanos",hidden=True)
    @commands.check(is_fun_enabled)
    async def thanos(self,ctx):
        await ctx.send(random.choice(await self.translate(ctx.channel,"fun","thanos")).format(ctx.author.mention))
    
    @commands.command(name="piece",hidden=True,aliases=['coin','flip'])
    @commands.check(is_fun_enabled)
    async def piece(self,ctx):
        """Heads or tails?"""
        if random.random() < 0.04:
            await ctx.send(await self.translate(ctx.channel,"fun","piece-1"))
        else:
            await ctx.send(random.choice(await self.translate(ctx.channel,"fun","piece-0")))
    
    @commands.command(name="weather",aliases=['météo'])
    @commands.cooldown(4, 30, type=commands.BucketType.guild)
    async def weather(self,ctx,*,city:str):
        """Get the weather of a city
        You need to provide the city name in english"""
        city = city.replace(" ","%20")
        async with aiohttp.ClientSession() as session:
            async with session.get("https://welcomer.glitch.me/weather?city="+city) as r:
                if r.status == 200:
                    if r.content_type == 'image/png':
                        if ctx.channel.permissions_for(ctx.me).embed_links:
                            emb = self.bot.cogs['EmbedCog'].Embed(image="https://welcomer.glitch.me/weather?city="+city,footer_text="From https://welcomer.glitch.me/weather")
                            return await ctx.send(embed=emb.discord_embed())
                        else:
                            return await ctx.send("https://welcomer.glitch.me/weather?city="+city)
                    #except Exception as e:
                    #    await self.bot.cogs['ErrorsCog'].on_error(e,ctx)
        await ctx.send(await self.translate(ctx.channel,"fun","invalid-city"))

    @commands.command(name="hour")
    @commands.cooldown(4, 50, type=commands.BucketType.guild)
    async def hour(self,ctx,*,city:str):
        """Get the hour of a city"""
        if city.lower() in ['mee6','mee6land']:
            return await ctx.send('**Mee6Land/MEE6**:\nEverytime (NoWhere)\n (Mee6Land - lat: unknown - long: unknown)')
        g = geocoder.arcgis(city)
        if not g.ok:
            return await ctx.send(await self.translate(ctx.channel,"fun","invalid-city"))
        timeZoneStr = self.tz.tzNameAt(g.json['lat'],g.json['lng'],forceTZ=True)
        if timeZoneStr=='uninhabited':
            return await ctx.send(await self.translate(ctx.channel,"fun","uninhabited-city"))
        timeZoneObj = timezone(timeZoneStr)
        d = datetime.datetime.now(timeZoneObj)
        format_d = await self.bot.cogs['TimeCog'].date(d,lang=await self.translate(ctx.channel,"current_lang","current"))
        await ctx.send("**{}**:\n{} ({})\n ({} - lat: {} - long: {})".format(timeZoneStr,format_d,d.tzname(),g.current_result.address,round(g.json['lat'],2),round(g.json['lng'],2)))

    @commands.command(name="tip")
    async def tip(self,ctx:commands.Context):
        """Send a tip, a fun fact or something else"""
        await ctx.send(random.choice(await self.translate(ctx.guild,"fun","tip-list")))

    @commands.command(name='afk')
    @commands.check(is_fun_enabled)
    @commands.guild_only()
    async def afk(self,ctx,*,reason=""):
        """Make you AFK
        You'll get a nice nickname, because nicknames are cool, aren't they?"""
        try:
            reason = await self.bot.cogs['UtilitiesCog'].clear_msg(reason,ctx.message.mention_everyone,ctx)
            self.afk_guys[ctx.author.id] = reason
            if (not ctx.author.display_name.endswith(' [AFK]')) and len(ctx.author.display_name)<26:
                await ctx.author.edit(nick=ctx.author.display_name+" [AFK]")
            await ctx.send(await self.translate(ctx.guild.id,"fun","afk-done"))
        except discord.errors.Forbidden:
            return await ctx.send(await self.translate(ctx.guild.id,"fun","afk-no-perm"))
    
    @commands.command(name='unafk')
    @commands.check(is_fun_enabled)
    @commands.guild_only()
    async def unafk(self,ctx):
        """Remove you from the AFK system
        Welcome back dude"""
        if ctx.author.id in self.afk_guys.keys():
            del self.afk_guys[ctx.author.id]
            await ctx.send(await self.translate(ctx.guild.id,"fun","unafk-done"))
            try:
                await ctx.author.edit(nick=ctx.author.display_name.replace(" [AFK]",''))                
            except discord.errors.Forbidden:
                pass
    
    async def check_afk(self,msg:discord.Message):
        """Check if someone pinged is afk"""
        ctx = await self.bot.get_context(msg)
        for member in msg.mentions:
            c = member.display_name.endswith(' [AFK]') or member.id in self.afk_guys.keys()
            if c and member!=msg.author:
                if member.id not in self.afk_guys or len(self.afk_guys[member.id])==0:
                    await msg.channel.send(await self.translate(msg.guild.id,"fun","afk-user-2"))
                else:
                    reason = await self.bot.cogs['UtilitiesCog'].clear_msg(str(await self.translate(msg.guild.id,"fun","afk-user-1")).format(self.afk_guys[member.id]),everyone=True,ctx=ctx)
                    await msg.channel.send(reason)
        if (not await checks.is_a_cmd(msg, self.bot)) and (ctx.author.display_name.endswith(' [AFK]') or ctx.author.id in self.afk_guys.keys()):
            user_config = await self.bot.cogs['UtilitiesCog'].get_db_userinfo(["auto_unafk"],[f'`userID`={ctx.author.id}'])
            if not user_config['auto_unafk']:
                return
            msg = copy.copy(msg)
            msg.content = (await self.bot.get_prefix(msg))[-1] + 'unafk'
            new_ctx = await self.bot.get_context(msg)
            await self.bot.invoke(new_ctx)


    @commands.command(name='embed',hidden=False)
    @commands.check(checks.has_embed_links)
    async def send_embed(self,ctx,*,arguments:args.arguments):
        """Send an embed
        Syntax: !embed key1=\"value 1\" key2=\"value 2\"

        Available keys:
            - title: the title of the embed [256 characters]
            - content: the text inside the box [2048 characters]
            - url: a well-formed url clickable via the title
            - footer: a little text at the bottom of the box [90 characters]
            - image: a well-formed url redirects to an image
            - color: the color of the embed bar (#hex or int)

        If you want to use quotation marks in the texts, it is possible to escape them thanks to the backslash (`\\"`)
        """
        if ctx.guild!=None and not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(await self.translate(ctx.channel,"fun","no-embed-perm"))
        k = {'title':"",'content':"",'url':'','footer':"",'image':'','color':ctx.bot.cogs['ServerCog'].embed_color}
        for key,value in arguments.items():
            if key=='title':
                k['title'] = value[:255]
            elif key=='content' or key=='url' or key=='image':
                k[key] = value.replace("\\n","\n")
            elif key=='footer':
                k['footer'] = value[:90]
            elif key=='color' or key=="colour":
                c = await args.Color().convert(ctx,value)
                if c!=None:
                    k['color'] = c
        emb = ctx.bot.cogs["EmbedCog"].Embed(title=k['title'], desc=k['content'], url=k['url'],footer_text=k['footer'],thumbnail=k['image'],color=k['color']).update_timestamp().set_author(ctx.author)
        try:
            await ctx.send(embed=emb.discord_embed())
        except Exception as e:
            if isinstance(e,discord.errors.HTTPException) and "In embed.thumbnail.url: Not a well formed URL" in str(e):
                return await ctx.send("invalid image")
            await ctx.send(str(await self.translate(ctx.channel,"fun","embed-error")).format(e))


    async def add_vote(self,msg):
        if self.bot.database_online and msg.guild!=None:
            emojiz = await self.bot.cogs["ServerCog"].find_staff(msg.guild,'vote_emojis')
        else:
            emojiz = None
        if emojiz == None or len(emojiz) == 0:
            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            return
        count = 0
        for r in emojiz.split(';'):
            if r.isnumeric():
                d_em = discord.utils.get(self.bot.emojis, id=int(r))
                if d_em != None:
                    await msg.add_reaction(d_em)
                    count +=1
            else:
                await msg.add_reaction(emojilib.emojize(r, use_aliases=True))
                count +=1
            if count==0:
                await msg.add_reaction('👍')
                await msg.add_reaction('👎')

    @commands.command(name="markdown")
    async def markdown(self,ctx):
        """Get help about markdown in Discord"""
        await ctx.send(await self.translate(ctx.channel,'fun','markdown'))
    
    @commands.command(name="remindme", aliases=["remind", "reminds"])
    @commands.cooldown(5,30,commands.BucketType.channel)
    @commands.cooldown(5,60,commands.BucketType.user)
    async def remindme(self, ctx:commands.Context, duration:commands.Greedy[args.tempdelta], *, message):
        """Ask the bot to remind you of something later
Please use the following format:
`XXm` : XX minutes
`XXh` : XX hours
`XXd` : XX days
`XXw` : XX weeks

..Example remindme 49d Think about doing my homework"""
        duration = sum(duration)
        if duration < 1:
            await ctx.send(await self.translate(ctx.channel, "fun", "reminds-too-short"))
            return
        if duration > 60*60*24*365*2:
            await ctx.send(await self.translate(ctx.channel, "fun", "reminds-too-long"))
            return
        if not self.bot.database_online:
            await ctx.send(await self.translate(ctx.channel, "rss", "no-db"))
            return
        f_duration = await ctx.bot.get_cog('TimeCog').time_delta(duration,lang=await self.translate(ctx.guild,'current_lang','current'), year=True, form='developed', precision=0)
        try:
            await ctx.bot.get_cog('Events').add_task("timer", duration, ctx.author.id, ctx.guild.id if ctx.guild else None, ctx.channel.id, message)
        except Exception as e:
            await ctx.send(await self.translate(ctx.channel, "server", "change-1"))
            await ctx.bot.get_cog("ErrorsCog").on_cmd_error(ctx,e)
        else:
            await ctx.send(await self.translate(ctx.channel, "fun", "reminds-saved", duration=f_duration))

        

    @commands.command(name="vote")
    @commands.cooldown(4, 30, type=commands.BucketType.guild)
    async def vote(self,ctx,number:typing.Optional[int] = 0,*,text):
        """Send a message on which anyone can vote through reactions. 
        A big thank to Adri526 for his emojis specially designed for the bot!
        
        If no number of choices is given, the emojis will be 👍 and 👎. Otherwise, it will be a series of numbers.
        The text sent by the bot is EXACTLY the one you give, without any more formatting."""
        text = await ctx.bot.cogs['UtilitiesCog'].clear_msg(text,ctx=ctx)
        if ctx.guild != None:
            if not (ctx.channel.permissions_for(ctx.guild.me).read_message_history and ctx.channel.permissions_for(ctx.guild.me).add_reactions):
                return await ctx.send(await self.translate(ctx.channel,"fun","cant-react"))
        if number==0:
            m = await ctx.send(text)
            try:
                await self.add_vote(m)
            except:
                await ctx.send(await self.translate(ctx.channel,"fun","no-reaction"))
                return
        else:
            liste = self.bot.cogs['EmojiCog'].numbEmojis
            if number>20 or number<0:
                await ctx.send(await self.translate(ctx.channel,"fun","vote-0"))
                return
            m = await ctx.send(text)
            for x in range(1,number+1):
                try:
                    await m.add_reaction(liste[x])
                except discord.errors.NotFound:
                    return
                except Exception as e:
                    await self.bot.cogs['ErrorsCog'].on_error(e,ctx)
        await self.bot.cogs['UtilitiesCog'].suppr(ctx.message)
        self.bot.log.debug(await self.bot.cogs['TimeCog'].date(datetime.datetime.now(),digital=True)+" Vote de {} : {}".format(ctx.author,ctx.message.content))


    async def check_suggestion(self,message):
        if message.guild==None or not self.bot.is_ready() or not self.bot.database_online:
            return
        try:
            channels = await self.bot.cogs['ServerCog'].find_staff(message.guild.id,'poll_channels')
            if channels==None or len(channels)==0:
                return
            if str(message.channel.id) in channels.split(';') and not message.author.bot:
                try:
                    await self.add_vote(message)
                except:
                    pass
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,message)

def setup(bot):
    bot.add_cog(FunCog(bot))
