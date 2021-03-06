import discord, mysql.connector, importlib, typing
from discord.ext import commands

from fcts import args, reloads
importlib.reload(args)


async def can_edit_case(ctx):
        if await ctx.bot.cogs['AdminCog'].check_if_admin(ctx.author):
            return True
        if ctx.bot.database_online:
            return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"warn")
        else:
            return False

class CasesCog(commands.Cog):
    """This part of the bot allows you to manage all your members' cases, to delete or edit them"""

    def __init__(self,bot):
        self.bot = bot
        self.file = "cases"
        try:
            self.translate = self.bot.cogs["LangCog"].tr
        except:
            pass
        if bot.user != None:
            self.table = 'cases_beta' if bot.beta else 'cases'
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.translate = self.bot.cogs["LangCog"].tr
        self.table = 'cases_beta' if self.bot.beta else 'cases'

    class Case:
        def __init__(self,bot,guildID,memberID,Type,ModID,Reason,date,duration=None,caseID=None):
            self.bot = bot
            self.guild = guildID
            self.id = caseID
            self.user = memberID
            self.type = Type
            self.mod = ModID
            self.reason = Reason
            self.duration = duration
            if date == None:
                self.date = "Unknown"
            else:
                self.date = date
        
        def create_id(self,liste):
            if len(liste)==0:
                self.id = 1
            else:
                self.id = max(liste)+1
            return self

        async def display(self,bot,display_guild=False):
            u = bot.get_user(self.user)
            if u == None:
                u = self.user
            else:
                u = u.mention
            g = bot.get_guild(self.guild)
            if g == None:
                g = self.guild
            else:
                g = g.name
            text = "**Case {}**".format(self.id)
            if display_guild:
                text += "\n**Guild:** {}".format(g)
            text += """
**Type:** {}
**User:** {}
**Moderator:** {}
**Date:** {}
**Reason:** *{}*""".format(self.type,u,self.mod,self.date,self.reason)
            if self.duration!=None and self.duration>0:
                text += "\nDuration: {}".format(await self.bot.cogs['TimeCog'].time_delta(self.duration,lang='en',form='temp'))
            return text


    def connect(self):
        return mysql.connector.connect(user=self.bot.database_keys['user'],password=self.bot.database_keys['password'],host=self.bot.database_keys['host'],database=self.bot.database_keys['database'])


    async def get_ids(self):
        """Return the list of every ids"""
        if not self.bot.database_online:
            return None
        try:
            l = await self.get_case(columns=['ID'])
            liste = list()
            for x in l:
                liste.append(x['ID'])
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,None)
            return
        return liste

    async def get_case(self,columns=[],criters=["1"],relation="AND"):
        """return every cases"""
        if not self.bot.database_online:
            return None
        if type(columns)!=list or type(criters)!=list:
            raise ValueError
        cnx = self.bot.cnx_frm
        cursor = cnx.cursor(dictionary=True)
        if columns == []:
            cl = "*"
        else:
            cl = "`"+"`,`".join(columns)+"`"
        relation = " "+relation+" "
        query = ("SELECT {} FROM `{}` WHERE {}".format(cl,self.table,relation.join(criters)))
        cursor.execute(query)
        liste = list()
        if len(columns)==0:
            for x in cursor:
                liste.append(self.Case(bot=self.bot,guildID=x['guild'],caseID=x['ID'],memberID=x['user'],Type=x['type'],ModID=x['mod'],date=x['created_at'],Reason=x['reason'],duration=x['duration']))
        else:
            for x in cursor:
                liste.append(x)
        return liste
    
    async def get_nber(self,userID:int,guildID:int):
        """Get the number of users infractions"""
        try:
            cnx = self.bot.cnx_frm
            cursor = cnx.cursor(dictionary = False)
            query = ("SELECT COUNT(*) FROM `{}` WHERE `user`={} AND `guild`={} AND `type`!='unban'".format(self.table,userID,guildID))
            cursor.execute(query)
            liste = list()
            for x in cursor:
                liste.append(x)
            cursor.close()
            if liste!=None and len(liste)==1:
                return liste[0][0]
            return 0
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,None)

    async def delete_case(self,ID):
        """delete a case from the db"""
        if not self.bot.database_online:
            return None
        if type(ID)!=int:
            raise ValueError
        cnx = self.bot.cnx_frm
        cursor = cnx.cursor()
        query = ("DELETE FROM `{}` WHERE `ID`='{}'".format(self.table,ID))
        cursor.execute(query)
        cnx.commit()
        return True
    
    async def add_case(self,case):
        """add a new case to the db"""
        if not self.bot.database_online:
            return None
        if type(case) != self.Case:
            raise ValueError
        cnx = self.bot.cnx_frm
        cursor = cnx.cursor()
        query = ("""INSERT INTO `{}` (`ID`, `guild`, `user`, `type`, `mod`, `reason`,`duration`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}','{}')""".format(self.table,case.id,case.guild,case.user,case.type,case.mod,case.reason.replace("'","\\'"),case.duration))
        cursor.execute(query)
        cnx.commit()
        return True

    async def update_reason(self,case):
        if not self.bot.database_online:
            return None
        """update infos of a case"""
        if type(case) != self.Case:
            raise ValueError
        cnx = self.bot.cnx_frm
        cursor = cnx.cursor()
        query = ("UPDATE `{}` SET `reason` = '{}' WHERE `ID` = {}".format(self.table,case.reason.replace("'","\\'"),case.id))
        cursor.execute(query)
        cnx.commit()
        return True



    @commands.group(name="cases",aliases=['case', 'infractions'])
    @commands.guild_only()
    @commands.cooldown(5, 15, commands.BucketType.user)
    @commands.check(can_edit_case)
    async def case_main(self,ctx):
        """Do anything with any user cases"""
        return

    @case_main.command(name="list")
    @commands.guild_only()
    @commands.cooldown(5, 30, commands.BucketType.user)
    async def see_case(self,ctx,*,user:args.user):
        """Get every case of a user
        This user can have left the server"""
        if not self.bot.database_online:
            return await ctx.send(await self.translate(ctx.guild.id,'cases','no_database'))
        await self.see_case_main(ctx,ctx.guild.id,user.id)
    
    @case_main.command(name="glist")
    @commands.guild_only()
    @commands.check(reloads.is_support_staff)
    async def see_case_2(self,ctx,guild:typing.Optional[args.Guild],*,user:args.user):
        """Get every case of a user on a specific guild
        This user can have left the server"""
        if not self.bot.database_online:
            return await ctx.send(await self.translate(ctx.guild.id,'cases','no_database'))
        await self.see_case_main(ctx,guild,user.id)
        
    async def see_case_main(self,ctx,guild:discord.Guild,user:discord.User):
        if guild != None:
            criters = ["`user`='{}'".format(user),"guild='{}'".format(guild)]
            syntax = await self.translate(ctx.guild,'cases','list-0')  
        else:
            syntax = await self.translate(ctx.guild,'cases','list-1')
            criters = ["`user`='{}'".format(user)]
        try:
            cases = await self.get_case(criters=criters)
            cases.reverse()
            u = self.bot.get_user(user)
            last_case = 1 if len(cases)>0 else 0
            e = -1
            if ctx.channel.permissions_for(ctx.guild.me).embed_links:
                embed = discord.Embed(title="title", colour=self.bot.cogs['ServerCog'].embed_color, timestamp=ctx.message.created_at)
                if u == None:
                    embed.set_author(name=str(user))
                else:
                    embed.set_author(name="Cases from "+str(u), url=u.avatar_url_as(format='png'), icon_url=str(u.avatar_url_as(format='png')))
                embed.set_footer(text="Requested by {}".format(ctx.author), icon_url=str(ctx.author.avatar_url_as(format='png')))
                if len(cases)>0:
                    l = await self.translate(ctx.guild.id,"current_lang","current")
                    for e,x in enumerate(cases):
                        g = self.bot.get_guild(x.guild)
                        if g == None:
                            g = x.guild
                        else:
                            g = g.name
                        m = self.bot.get_user(x.mod)
                        if m == None:
                            m = x.mod
                        else:
                            m = m.mention
                        text = syntax.format(G=g,T=x.type,M=m,R=x.reason,D=await self.bot.cogs['TimeCog'].date(x.date,lang=l,year=True,digital=True))
                        if x.duration != None and x.duration>0:
                            text += await self.translate(ctx.guild.id,'cases','list-2', D = await self.bot.cogs['TimeCog'].time_delta(x.duration,lang=l,year=False,form='temp'))
                        embed.add_field(name="Case #{}".format(x.id),value=text,inline=False)
                        if len(embed.fields)>20:
                            embed.title = str(await self.translate(ctx.guild.id,"cases","cases-0")).format(len(cases),last_case,e+1)
                            await ctx.send(embed=embed)
                            embed.clear_fields()
                            last_case = e+2
                embed.title = str(await self.translate(ctx.guild.id,"cases","cases-0")).format(len(cases),last_case,e+1)
                await ctx.send(embed=embed)
            else:
                if len(cases)>0:
                    text = str(await self.translate(ctx.guild.id,"cases","cases-0")).format(len(cases),1,len(cases))+"\n"
                    for e,x in enumerate(cases):
                        text += "```{}\n```".format(await x.display(self.bot,True).replace('*',''))
                        if len(text)>1800:
                            await ctx.send(text)
                            last_case = e+2
                            text = ""
                    await ctx.send(text)
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,None)
    

    @case_main.command(name="reason",aliases=['edit'])
    @commands.guild_only()
    async def reason(self,ctx,case:int,*,reason):
        """Edit the reason of a case"""
        if not self.bot.database_online:
            return await ctx.send(await self.translate(ctx.guild.id,'cases','no_database'))
        try:
            c = ["ID="+str(case)]
            if not await self.bot.cogs['AdminCog'].check_if_admin(ctx.author):
                c.append("guild="+str(ctx.guild.id))
            cases = await self.get_case(criters=c)
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,None)
            return
        if len(cases)!=1:
            await ctx.send(await self.translate(ctx.guild.id,"cases","not-found"))
            return
        case = cases[0]
        old_reason = case.reason
        case.reason = reason
        await self.update_reason(case)
        await ctx.send(str(await self.translate(ctx.guild.id,"cases","reason-edited")).format(case.id))
        log = await self.translate(ctx.guild.id,"logs","case-reason",old=old_reason,new=case.reason,id=case.id)
        await self.bot.cogs["Events"].send_logs_per_server(ctx.guild,"case-edit",log,ctx.author)
    
    @case_main.command(name="search")
    @commands.guild_only()
    async def search_case(self,ctx,case:int):
        """Search for a specific case in your guild"""
        if not self.bot.database_online:
            return await ctx.send(await self.translate(ctx.guild.id,'cases','no_database'))
        try:
            isSupport = await self.bot.cogs['InfoCog'].is_support(ctx)
            c = ["ID="+str(case)]
            if not isSupport:
                c.append("guild="+str(ctx.guild.id))
            cases = await self.get_case(criters=c)
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,ctx)
            return
        if len(cases)!=1:
            await ctx.send(await self.translate(ctx.guild.id,"cases","not-found"))
            return
        if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
            await ctx.send(await self.translate(ctx.guild.id,"mc","cant-embed"))
            return
        try:
            case = cases[0]
            user = await self.bot.fetch_user(case.user)
            mod = await self.bot.fetch_user(case.mod)
            u = "{} ({})".format(user,user.id)
            if not isSupport:
                guild = ctx.guild.name
                v = await self.translate(ctx.guild.id,'cases','search-0')
            else:
                guild = "{0.name} ({0.id})".format(self.bot.get_guild(case.guild))
                v = await self.translate(ctx.guild.id,'cases','search-1')
            title = str(await self.translate(ctx.guild.id,"cases","title-search")).format(case.id)
            l = await self.translate(ctx.guild.id,"current_lang","current")
            v = v.format(G=guild,U=u,T=case.type,M=str(mod),R=case.reason,D=await self.bot.cogs['TimeCog'].date(case.date,lang=l,year=True,digital=True))

            emb = self.bot.cogs['EmbedCog'].Embed(title=title,desc=v,color=self.bot.cogs['ServerCog'].embed_color).update_timestamp().set_author(user)
            await ctx.send(embed=emb.discord_embed())
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,ctx)
        

    @case_main.command(name="remove",aliases=["clear","delete"])
    @commands.guild_only()
    async def remove(self,ctx,case:int):
        """Delete a case forever
        Warning: "Forever", it's very long. And no backups are done"""
        if not self.bot.database_online:
            return await ctx.send(await self.translate(ctx.guild.id,'cases','no_database'))
        try:
            c = ["ID="+str(case)]
            if not await self.bot.cogs['AdminCog'].check_if_admin(ctx.author):
                c.append("guild="+str(ctx.guild.id))
            cases = await self.get_case(columns=['ID','user'],criters=c)
        except Exception as e:
            await self.bot.cogs["ErrorsCog"].on_error(e,None)
            return
        if len(cases)!=1:
            await ctx.send(await self.translate(ctx.guild.id,"cases","not-found"))
            return
        case = cases[0]
        await self.delete_case(case['ID'])
        await ctx.send(str(await self.translate(ctx.guild.id,"cases","deleted")).format(case['ID']))
        user = ctx.bot.get_user(case['user'])
        if user==None:
            user = case['user']
        log = await self.translate(ctx.guild.id,"logs","case-del",id=case['ID'],user=str(user))
        await self.bot.cogs["Events"].send_logs_per_server(ctx.guild,"case-edit",log,ctx.author)


def setup(bot):
    bot.add_cog(CasesCog(bot))