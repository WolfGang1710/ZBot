import discord, datetime, json
from discord.ext import commands


class BotEventsCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.file = "bot_events"
        self.current_event = None
        self.current_event_data = {}
        self.updateCurrentEvent()
        try:
            self.translate = bot.cogs['LangCog'].tr
        except:
            pass

    def updateCurrentEvent(self):
        today = datetime.date.today()
        with open("events-list.json",'r') as f:
            events = json.load(f)
        self.current_event = None
        self.current_event_data = {}
        for ev_data in events.values():
            ev_data["begin"] = datetime.datetime.strptime(ev_data["begin"], "%Y-%m-%d")
            ev_data["end"] = datetime.datetime.strptime(ev_data["end"], "%Y-%m-%d")
            if ev_data["begin"].date() <= today and ev_data["end"].date() >= today:
                self.current_event = ev_data["type"]
                self.current_event_data = ev_data
                break

    @commands.group(name="events",aliases=["botevents","botevent","event"])
    async def events_main(self,ctx:commands.Context):
        """When I'm organizing some events"""
        if ctx.subcommand_passed==None:
            await self.bot.cogs['HelpCog'].help_command(ctx,['events'])
    
    @events_main.command(name="info")
    async def event_info(self,ctx:commands.Context):
        """Get info about the current event"""
        events_desc = await self.translate(ctx.channel,"bot_events","events-desc")
        current_event = str(self.bot.current_event) + "-" + str(datetime.datetime.today().year)
        if current_event in events_desc.keys():
            # Title
            try:
                title = (await self.translate(ctx.channel,"bot_events","events-title"))[current_event]
            except:
                title = self.current_event
            # Begin/End dates
            nice_date = self.bot.cogs["TimeCog"].date
            lang = await self.translate(ctx.channel,"current_lang","current")
            begin = await nice_date(self.current_event_data["begin"],lang,year=True,digital=True,hour=False)
            end = await nice_date(self.current_event_data["end"],lang,year=True,digital=True,hour=False)
            if ctx.guild==None or ctx.channel.permissions_for(ctx.guild.me).embed_links:    
                fields = [
                    {"name": (await self.translate(ctx.channel,"keywords","beginning")).capitalize(), 
                    "value": begin,
                    "inline": True
                    },
                    {"name": (await self.translate(ctx.channel,"keywords","end")).capitalize(), 
                    "value": end,
                    "inline": True
                    }]
                # Prices to win
                prices = await self.translate(ctx.channel,"bot_events","events-prices")
                if current_event in prices.keys():
                    points = await self.translate(ctx.channel,"bot_events","points")
                    prices = [f"**{k} {points}:** {v}" for k,v in prices[current_event].items()]
                    fields.append({"name":await self.translate(ctx.channel,"bot_events","events-price-title"), "value":"\n".join(prices)})
                emb = self.bot.cogs["EmbedCog"].Embed(title=title, desc=events_desc[current_event], fields=fields, image=self.current_event_data["icon"], color=self.current_event_data["color"])
                #e = discord.Embed().from_dict(emb.to_dict())
                await ctx.send(embed=emb)
            else:
                txt = f"**{title}**\n\n{events_desc[current_event]}"
                txt += "\n\n__{}:__ {}".format((await self.translate(ctx.channel,"keywords","beginning")).capitalize(),begin)
                txt += "\n__{}:__ {}".format((await self.translate(ctx.channel,"keywords","end")).capitalize(),end)
                await ctx.send(txt)
        else:
            await ctx.send(events_desc["nothing"])
    

    @events_main.command(name="rank")
    async def events_rank(self,ctx:commands.Context,user:discord.User=None):
        """Watch how many xp you already have
        Events points are reset after each event"""
        current_event = str(self.bot.current_event) + "-" + str(datetime.datetime.today().year)
        events_desc = await self.translate(ctx.channel,"bot_events","events-desc")
        if not current_event in events_desc.keys():
            await ctx.send(events_desc["nothing"])
            return
        if user==None:
            user = ctx.author
        user_rank_query = await self.bot.cogs["UtilitiesCog"].get_eventsPoints_rank(ctx.author.id)
        if user_rank_query==None:
            user_rank = await self.translate(ctx.channel,"bot_events","unclassed")
            points = 0
        else:
            total_ranked = await self.bot.cogs["UtilitiesCog"].get_eventsPoints_nbr()
            if user_rank_query['rank'] <= total_ranked:
                user_rank = "{}/{}".format(user_rank_query['rank'], total_ranked)
            else:
                user_rank = await self.translate(ctx.channel,"bot_events","unclassed")
            points = user_rank_query["events_points"]
        title = await self.translate(ctx.channel,"bot_events","rank-title")
        prices = await self.translate(ctx.channel,"bot_events","events-prices")
        if current_event in prices.keys():
            emojis = self.bot.cogs["EmojiCog"].customEmojis["green_check"], self.bot.cogs["EmojiCog"].customEmojis["red_cross"]
            p = list()
            for k,v in prices[current_event].items():
                emoji = emojis[0] if int(k)<=points else emojis[1]
                p.append(f"{emoji}{min(points,int(k))}/{k}: {v}")
            prices = "\n".join(p)
            objectives_title = await self.translate(ctx.channel,"bot_events","objectives")
        else:
            prices = ""
            objectives_title = ""
        rank_total = await self.translate(ctx.channel,"bot_events","rank-total")
        rank_global = await self.translate(ctx.channel,"bot_events","rank-global")
        
        if ctx.guild==None or ctx.channel.permissions_for(ctx.guild.me).embed_links:
            fields = list()
            if objectives_title != "":
                fields.append({"name": objectives_title, "value": prices})
            fields.append({"name": rank_total, "value": str(points), "inline":True})
            fields.append({"name": rank_global, "value": user_rank, "inline":True})
            desc = await self.translate(ctx.channel, "bot_events", "xp-howto")
            emb = self.bot.cogs["EmbedCog"].Embed(title=title,desc=desc,fields=fields,color=4254055,author_name=str(ctx.author),author_icon=str(await self.bot.user_avatar_as(ctx.author,32)))
            await ctx.send(embed=emb)
        else:
            msg = f"**{title}** ({ctx.author})"
            if objectives_title != "":
                msg += "\n\n__{}:__\n{}".format(objectives_title,prices)
            msg += "\n\n__{}:__ {}\n__{}:__ {}".format(rank_total,str(points),rank_global,user_rank)
            await ctx.send(msg)
        

def setup(bot):
    bot.add_cog(BotEventsCog(bot))