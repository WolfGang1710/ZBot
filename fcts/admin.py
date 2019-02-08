import discord
from discord.ext import commands

import time, importlib, sys, traceback, datetime, os, shutil, asyncio, inspect, typing, io, textwrap, copy, operator, feedparser, requests, random
from contextlib import redirect_stdout
from fcts import reloads
importlib.reload(reloads)


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])
    # remove `foo`
    return content.strip('` \n')

class AdminCog:
    """Here are listed all commands related to the internal administration of the bot. Most of them are not accessible to users, but only to ZBot administrators."""
        
    def __init__(self, bot):
        self.bot = bot
        self.file = "admin"
        self.emergency_time = 5.0
        if self.bot.beta:
            self.update = {'fr':'Foo','en':'Bar'}
        else:
            self.update = {'fr':None,'en':None}
        try:
            self.translate = self.bot.cogs["LangCog"].tr
            self.print = self.bot.cogs["UtilitiesCog"].print2
            self.utilities = self.bot.cogs["UtilitiesCog"]
        except:
            pass
        self._last_result = None
        
    async def on_ready(self):
        self.translate = self.bot.cogs["LangCog"].tr
        self.print = self.bot.cogs["UtilitiesCog"].print2
        self.utilities = self.bot.cogs["UtilitiesCog"]

    async def check_if_admin(self,ctx):
        return await reloads.check_admin(ctx)

    
    @commands.command(name='admins')
    async def admin_list(self,ctx):
        """Get the list of ZBot administrators"""
        l  = list()
        for u in reloads.admins_id:
            l.append(str(self.bot.get_user(u)))
        await ctx.send(str(await self.translate(ctx.guild,"infos","admins-list")).format(", ".join(l)))

    @commands.command(name='spoil',hidden=True)
    @commands.check(reloads.check_admin)
    async def send_spoiler(self,ctx,*,text):
        """spoil spoil spoil"""
        spoil = lambda text: "||"+"||||".join(text)+"||"
        await ctx.send("```\n{}\n```".format(spoil(text)))

    @commands.command(name='msg',aliases=['tell'])
    @commands.check(reloads.check_admin)
    async def send_msg(self,ctx,user:discord.User,*,message):
        """Envoie un mp à un membre"""
        try:
            await user.send(message)
            await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(ctx.message)
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,ctx)

    @commands.group(name='admin',hidden=True)
    @commands.check(reloads.check_admin)
    async def main_msg(self,ctx):
        """Commandes réservées aux administrateurs de ZBot"""
        if ctx.invoked_subcommand is None:
            text = "Liste des commandes disponibles :"
            for cmd in self.main_msg.commands:
                text+="\n- {} *({})*".format(cmd.name,cmd.help)
                if type(cmd)==commands.core.Group:
                    for cmds in cmd.commands:
                        text+="\n        - {} *({})*".format(cmds.name,cmds.help)
            await ctx.send(text)

    @main_msg.command(name="faq",hidden=True)
    @commands.check(reloads.check_admin)
    async def send_faq(self,ctx):
        """Envoie les messages du salon <#541228784456695818> vers le salon <#508028818154323980>"""
        destination_fr = ctx.guild.get_channel(508028818154323980)
        destination_en = ctx.guild.get_channel(541599345972346881)
        chan_fr = ctx.guild.get_channel(541228784456695818)
        chan_en = ctx.guild.get_channel(541599226623426590)
        role_fr = ctx.guild.get_role(541224634087899146)
        role_en = ctx.guild.get_role(537597687801839617)
        await destination_fr.set_permissions(role_fr, read_messages=False)
        await destination_en.set_permissions(role_en, read_messages=False)
        await destination_fr.purge()
        await destination_en.purge()
        async for message in chan_fr.history(limit=200,reverse=True):
            await destination_fr.send(message.content)
        async for message in chan_en.history(limit=200,reverse=True):
            await destination_en.send(message.content)
        await destination_fr.set_permissions(role_fr, read_messages=True)
        await destination_en.set_permissions(role_en, read_messages=True)
        await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(ctx.message)


    @main_msg.command(name="update",hidden=True)
    @commands.check(reloads.check_admin)
    async def update_config(self,ctx,send=None):
        """Préparer/lancer un message de mise à jour
        Ajouter 'send' en argument déclenche la procédure pour l'envoyer à tous les serveurs"""
        if send!=None and send=='send':
            await self.send_updates(ctx)
            return
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        for x in self.update.keys():
            await ctx.send("Message en {} ?".format(x))
            try:
                msg = await ctx.bot.wait_for('message', check=check,timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send('Trop tard !')
            if msg.content.lower() in ['none','annuler','stop','oups']:
                return await ctx.send('Annulé !')
            self.update[x] = msg.content
        await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(msg)
    
    async def send_updates(self,ctx):
        """Lance un message de mise à jour"""
        if None in self.update.values():
            return await ctx.send("Les textes ne sont pas complets !")
        text = "Vos messages contiennent"
        if max([len(x) for x in self.update.values()]) > 1900//len(self.update.keys()):
            for k,v in self.update.items():
                text += "\n{}:``\n{}\n```".format(k,v)
                msg = await ctx.send(text)
                text = ''
        else:
            text += "\n"+"\n".join(["{}:\n```\n{}\n```".format(k,v) for k,v in self.update.items()])
            msg = await ctx.send(text)
        await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(msg)
        def check(reaction, user):
            return user == ctx.author and reaction.message.id==msg.id
        try:
            await self.bot.wait_for('reaction_add', timeout=20.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send('Trop long !')
        count = 0
        for guild in ctx.bot.guilds:
            channels = await ctx.bot.cogs["ServerCog"].find_staff(guild.id,'bot_news')
            if channels==None or len(channels)==0:
                continue
            channels = [guild.get_channel(int(x)) for x in channels.split(';') if len(x)>5 and x.isnumeric()]
            lang = await ctx.bot.cogs["ServerCog"].find_staff(guild.id,'language')
            if type(lang)!=int:
                lang = 0
            lang = ctx.bot.cogs['LangCog'].languages[lang]
            if lang not in self.update.keys():
                if lang=='lolcat':
                    lang = 'en'
            for chan in channels:
                try:
                    await chan.send(self.update[lang])
                except Exception as e:
                    await ctx.bot.cogs['ErrorsCog'].on_error(e,ctx)
                else:
                    count += 1
        for k in self.update.keys():
            self.update[k] = None
        await ctx.send("Message envoyé dans {} salons !".format(count))


    @main_msg.command(name="cogs",hidden=True)
    @commands.check(reloads.check_admin)
    async def cogs_list(self,ctx):
        """Voir la liste de tout les cogs"""
        text = str()
        for k,v in self.bot.cogs.items():
            text +="- {} ({}) \n".format(v.file,k)
        await ctx.send(text)

    @main_msg.command(name="guilds",aliases=['servers'],hidden=True)
    @commands.check(reloads.check_admin)
    async def send_guilds_list(self,ctx):
        """Obtenir la liste de tout les serveurs"""
        text = str()
        for x in sorted(ctx.bot.guilds, key=operator.attrgetter('me.joined_at')):
            text += "- {} (`{}` - {} membres)\n".format(x.name,x.owner,len(x.members))
            if len(text)>1900:
                await ctx.send(text)
                text = ""
        if len(text)>0:
            await ctx.send(text)

    @main_msg.command(name='shutdown')
    @commands.check(reloads.check_admin)
    async def shutdown(self,ctx,arg=""):
        """Eteint le bot"""
        for folderName, _, filenames in os.walk('.'):
            for filename in filenames:
                if filename.endswith('.pyc'):
                    os.unlink(folderName+'/'+filename)
            if  folderName.endswith('__pycache__'):
                os.rmdir(folderName)
        if arg != "no-backup":
            m = await ctx.send("Création de la sauvegarde...")
            #await backup_auto(client)
            await m.edit(content="Bot en voie d'extinction")
        else:
            await ctx.send("Bot en voie d'extinction")
        await self.bot.change_presence(status=discord.Status('offline'))
        await self.print("Bot en voie d'extinction")
        await self.bot.logout()
        await self.bot.close()

    @main_msg.command(name='reload')
    @commands.check(reloads.check_admin)
    async def cog_reload(self, ctx, *, cog: str):
        """Recharge un module"""
        cogs = cog.split(" ")
        await self.bot.cogs["ReloadsCog"].reload_cogs(ctx,cogs)
        
    @main_msg.command(name="check_tr")
    @commands.check(reloads.check_admin)
    async def check_tr(self,ctx,lang='en'):
        """Vérifie si un fichier de langue est complet"""
        await self.bot.cogs["LangCog"].check_tr(ctx.channel,lang)

    @main_msg.command(name="backup")
    @commands.check(reloads.check_admin)
    async def adm_backup(self,ctx):
        """Exécute une sauvegarde complète du code"""
        await self.backup_auto(ctx)

    @main_msg.command(name="membercounter")
    @commands.check(reloads.check_admin)
    async def membercounter(self,ctx):
        """Recharge tout ces salons qui contiennent le nombre de membres, pour tout les serveurs"""
        if self.bot.database_online:
            for x in self.bot.guilds:
                await self.bot.cogs["ServerCog"].update_memberChannel(x)
            await ctx.send(":ok_hand:")
        else:
            await ctx.send("Impossible de faire ceci, la base de donnée est inaccessible")

    @main_msg.command(name="get_invites",aliases=['invite'])
    @commands.check(reloads.check_admin)
    async def adm_invites(self,ctx,*,server=None):
        """Cherche une invitation pour un serveur, ou tous"""
        if server != None:
            guild = discord.utils.get(self.bot.guilds, name=server)
            if guild == None and server.isnumeric():
                guild = discord.utils.get(self.bot.guilds, id=int(server))
            await ctx.author.send(await self.search_invite(guild,server))
        else:
            liste = list()
            for guild in self.bot.guilds:
                liste.append(await self.search_invite(guild,guild))
                if len("\n".join(liste))>1900:
                    await ctx.author.send("\n".join(liste))
                    liste = []
            if len(liste)>0:
                await ctx.author.send("\n".join(liste))
        await self.bot.cogs['UtilitiesCog'].suppr(ctx.message)

    async def search_invite(self,guild,string):
        if guild==None:
            return "Le serveur `{}` n'a pas été trouvé".format(string)
        try:
            inv = await guild.invites()
            if len(inv)>0:
                msg = "`{}` - {} ({} membres) ".format(guild.name,inv[0],len(guild.members))
            else:
                msg = "`{}` - Le serveur ne possède pas d'invitation".format(guild.name)
        except discord.Forbidden:
            msg = "`{}` - Impossible de récupérer l'invitation du serveur (Forbidden)".format(guild.name)
        except Exception as e:
            msg = "`ERROR:` "+str(e)
            await self.bot.cogs['ErrorsCog'].on_error(e,None)
        return msg

    @main_msg.command(name="config")
    @commands.check(reloads.check_admin)
    async def admin_sconfig_see(self,ctx,*,server):
        """Affiche les options d'un serveur"""
        if not ctx.bot.database_online:
            await ctx.send("Impossible d'afficher cette commande, la base de donnée est hors ligne :confused:")
            return
        if server.isnumeric():
            guild = discord.utils.get(self.bot.guilds,id=int(server))
        else:
            guild = discord.utils.get(self.bot.guilds,name=server)
        if guild != None:
            try:
                await self.bot.cogs["ServerCog"].send_see(guild,ctx.channel,None,ctx.message,None)
            except Exception as e:
                await self.bot.cogs["Errors"].on_command_error(ctx,e)
        else:
            await ctx.send("Serveur introuvable")

    @main_msg.command(name="emergency")
    @commands.check(reloads.check_admin)
    async def emergency_cmd(self,ctx):
        """Déclenche la procédure d'urgence
        A N'UTILISER QU'EN CAS DE BESOIN ABSOLU ! Le bot quittera tout les serveurs après avoir envoyé un mp à chaque propriétaire"""
        await ctx.send(await self.emergency())

    async def emergency(self,level=100):
        for x in reloads.admins_id:
            try:
                user = self.bot.get_user(x)
                print(type(user),user)
                if user.dm_channel==None:
                    await user.create_dm()
                time = round(self.emergency_time - level/100,1)
                msg = await user.dm_channel.send("{} La procédure d'urgence vient d'être activée. Si vous souhaitez l'annuler, veuillez cliquer sur la réaction ci-dessous dans les {} secondes qui suivent l'envoi de ce message.".format(self.bot.cogs['EmojiCog'].customEmojis['red_warning'],time))
                await msg.add_reaction('🛑')
            except Exception as e:
                await self.bot.cogs['ErrorsCog'].on_error(e,None)

        def check(reaction, user):
            return user.id in reloads.admins_id
        try:
            await self.bot.wait_for('reaction_add', timeout=time, check=check)
        except asyncio.TimeoutError:
            owners = list()
            servers = 0
            for server in self.bot.guilds:
                if server.id==500648624204808193:
                    continue
                try:
                    if server.owner not in owners:
                        await server.owner.send(await self.translate(server,"admin","emergency"))
                        owners.append(server.owner)
                    await server.leave()
                    servers +=1
                except:
                    continue
            chan = await self.bot.get_channel(500674177548812306)
            await chan.send("{} Prodédure d'urgence déclenchée : {} serveurs quittés - {} propriétaires prévenus".format(self.bot.cogs['EmojiCog'].customEmojis['red_alert'],servers,len(owners)))
            return "{}  {} propriétaires de serveurs ont été prévenu ({} serveurs)".format(self.bot.cogs['EmojiCog'].customEmojis['red_alert'],len(owners),servers)
        for x in reloads.admins_id:
            try:
                user = self.bot.get_user(x)
                await user.send("La procédure a été annulée !")
            except Exception as e:
                await self.bot.cogs['ErrorsCog'].on_error(e,None)
        return "Qui a appuyé sur le bouton rouge ? :thinking:"

    @main_msg.command(name="code")
    async def show_code(self,ctx,cmd):
        cmds = self.bot.commands
        obj = await self.bot.cogs['UtilitiesCog'].set_find(cmds,cmd)
        if obj != None:
            await ctx.send("```py\n{}\n```".format(inspect.getsource(obj.callback)))
        else:
            await ctx.send("Commande `{}` introuvable".format(cmd))
    
    @main_msg.command(name="logs")
    @commands.check(reloads.check_admin)
    async def show_last_logs(self,ctx,lines:typing.Optional[int]=5,match=''):
        """Affiche les <lines> derniers logs ayant <match> dedans"""
        try:
            with open('debug.log','r',encoding='utf-8') as file:
                #try:
                    #file.seek(-300*lines,2)
                #except:
                    #pass
                text = file.read().split("\n")
            msg = str()
            liste = list()
            i = 1
            while len(liste)<=lines and i<min(2000,len(text)):
                i+=1
                if (not match in text[-i]) or ctx.message.content in text[-i]:
                    continue
                liste.append(text[-i].replace('`',''))
            for i in liste:
                if len(msg+i)>1900:
                    await ctx.send("```\n{}\n```".format(msg))
                    msg = ""
                if len(i)<1900:
                    msg += "\n"+i.replace('`','')
            await ctx.send("```\n{}\n```".format(msg))
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,ctx)

    @main_msg.group(name="server")
    @commands.check(reloads.check_admin)
    async def main_botserv(self,ctx):
        """Quelques commandes liées au serveur officiel"""
        if ctx.invoked_subcommand is None or ctx.invoked_subcommand==self.main_botserv:
            text = "Liste des commandes disponibles :"
            for cmd in self.main_botserv.commands:
                text+="\n- {} *({})*".format(cmd.name,cmd.help)
            await ctx.send(text)

    @main_botserv.command(name="owner_reload")
    @commands.check(reloads.check_admin)
    async def owner_reload(self,ctx):
        """Ajoute le rôle Owner à tout les membres possédant un serveur avec le bot
        Il est nécessaire d'avoir au moins 10 membres pour que le rôle soit ajouté"""
        server = self.bot.get_guild(356067272730607628)
        if server==None:
            await ctx.send("Serveur ZBot introuvable")
            return
        role = server.get_role(486905171738361876)
        if role==None:
            await ctx.send("Rôle Owners introuvable")
            return
        owner_list = list()
        for guild in self.bot.guilds:
            if len(guild.members)>9:
                owner_list.append(guild.owner.id)
        for member in server.members:
            if member.id in owner_list and role not in member.roles:
                await ctx.send("Rôle ajouté à "+str(member))
                await member.add_roles(role,reason="This user support me")
            elif (member.id not in owner_list) and role in member.roles:
                await ctx.send("Rôle supprimé à "+str(member))
                await member.remove_roles(role,reason="This user doesn't support me anymore")
        await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(ctx.message)

    @main_botserv.command(name="best_ideas")
    @commands.check(reloads.check_admin)
    async def best_ideas(self,ctx,number:int=10):
        """Donne la liste des 10 meilleures idées"""
        bot_msg = await ctx.send("Chargement des idées...")
        server = self.bot.get_guild(356067272730607628)
        if server==None:
            return await ctx.send("Serveur introuvable")
        channel = server.get_channel(488769306524385301)
        if channel == None:
            return await ctx.send("Salon introuvable")
        liste = list()
        async for msg in channel.history(limit=500):
            if len(msg.reactions) > 0:
                up = 0
                down = 0
                for x in msg.reactions:
                    users = await x.users().flatten()
                    if x.emoji == '👍':
                        up = x.count
                        if ctx.guild.me in users :
                            up -= 1
                    elif x.emoji == '👎':
                        down = x.count
                        if ctx.guild.me in users:
                            down -= 1
                liste.append((up-down,msg.content,up,down))
        liste.sort(reverse=True)
        count = len(liste)
        liste = liste[:number]
        text = "Liste des {} meilleures idées (sur {}) :".format(len(liste),count)
        for x in liste:
            text += "\n- {} ({} - {})".format(x[1],x[2],x[3])
        try:
            await bot_msg.edit(content=text)
        except discord.HTTPException:
            await ctx.send("Le message est trop long pour être envoyé !")

    @commands.command(name="activity")
    @commands.check(reloads.check_admin)
    async def change_activity(self,ctx, Type: str, * act: str):
        """Change l'activité du bot (play, watch, listen, stream)"""
        act = " ".join(act)
        if Type in ['game','play']:
            await self.bot.change_presence(activity=discord.Game(name=act))
        elif Type in ['watch','see']:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=act,timestamps={'start':time.time()}))
        elif Type in ['listen']:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=act,timestamps={'start':time.time()}))
        elif Type in ['stream']:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name=act,timestamps={'start':time.time()}))
        else:
            await ctx.send(await self.translate(ctx.guild.id,"admin","change_game-0"))
        await ctx.message.delete()
    

    @commands.command(name='eval')
    @commands.check(reloads.check_admin)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code
        Credits: Rapptz (https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py)"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }
        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        try:
            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,ctx)
            return
        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            await ctx.bot.cogs['UtilitiesCog'].add_check_reaction(ctx.message)

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')
    
    @commands.command(name='execute',hidden=True)
    @commands.check(reloads.check_admin)
    async def sudo(self, ctx, who: typing.Union[discord.Member, discord.User], *, command: str):
        """Run a command as another user
        Credits: Rapptz (https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py)"""
        msg = copy.copy(ctx.message)
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg)
        #new_ctx.db = ctx.db
        await self.bot.invoke(new_ctx)

    async def backup_auto(self,ctx=None):
        """Crée une backup du code"""
        t = time.time()
        await self.print("("+str(await self.bot.cogs['TimeCog'].date(datetime.datetime.now(),digital=True))+") Backup auto en cours")
        message = await ctx.send(":hourglass: Sauvegarde en cours...")
        try:
            os.remove('../backup.tar')
        except:
            pass
        try:
            archive = shutil.make_archive('backup','tar','..')
        except FileNotFoundError:
            await self.print("Impossible de trouver le dossier de sauvegarde")
            await message.edit("{} Impossible de trouver le dossier de sauvegarde".format(self.bot.cogs['EmojiCog'].customEmojis['red_cross']))
            return
        try:
            shutil.move(archive,'..')
        except shutil.Error:
            os.remove('../backup.tar')
            shutil.move(archive,'..')
        try:
            os.remove('backup.tar')
        except:
            pass
        msg = ":white_check_mark: Sauvegarde terminée en {} secondes !".format(round(time.time()-t,3))
        await self.print(msg)
        if ctx != None:
            await message.edit(content=msg)
            

def setup(bot):
    bot.add_cog(AdminCog(bot))
