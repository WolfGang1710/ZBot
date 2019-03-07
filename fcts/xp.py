import discord, random, time, asyncio
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageTk
import requests, io, time

class XPCog:

    def __init__(self,bot):
        self.bot = bot
        self.cache = dict()
        self.levels = [0]
        self.table = 'xp_beta' if bot.beta else 'xp'
        self.cooldown = 10
        self.minimal_size = 5
        self.spam_rate = 0.35
        self.xp_per_char = 0.4
        self.file = 'xp'
        bot.add_listener(self.add_xp,'on_message')
        try:
            self.translate = bot.cogs['LangCog'].tr
        except:
            pass
    
    async def on_ready(self):
        self.translate = self.bot.cogs['LangCog'].tr
        self.table = 'xp_beta' if self.bot.beta else 'xp'

    async def add_xp(self,msg):
        """Attribue un certain nombre d'xp à un message"""
        if msg.author.id in self.cache.keys():
            if time.time() - self.cache[msg.author.id] < self.cooldown:
                return
        content = msg.clean_content
        if len(content)<self.minimal_size or await self.check_spam(content) or msg.author.bot or await self.check_cmd(msg):
            return
        await self.bdd_set_xp(msg.author.id,await self.calc_xp(msg),'add')


    async def check_cmd(self,msg):
        """Vérifie si un message est une commande"""
        pr = await self.bot.get_prefix(msg)
        is_cmd = False
        for p in pr:
            is_cmd = is_cmd or msg.content.startswith(p)
        return is_cmd

    async def check_spam(self,text):
        """Vérifie si un text contient du spam"""
        d = dict()
        for c in text:
            if c in d.keys():
                d[c] += 1
            else:
                d[c] = 1
        for v in d.values():
            if v/len(text) > self.spam_rate:
                return True
        return False

    async def calc_xp(self,msg):
        """Calcule le nombre d'xp correspondant à un message"""
        return round(len(msg.clean_content)*self.xp_per_char)

    async def calc_level(self,xp):
        """Calcule le niveau correspondant à un nombre d'xp"""
        if xp > max(self.levels):
            needed_xp = 0
            current_lvl = 0
            self.levels = [0]
            while needed_xp<xp:
                temp = round(current_lvl**2+100)
                self.levels.append(self.levels[-1]+temp)
                needed_xp = self.levels[-1]
                current_lvl += 1
            return current_lvl,self.levels[-1]
        elif xp == max(self.levels):
            return len(self.levels)-1,(await self.calc_level(xp+1))[1]
        else:
            for e in range(len(self.levels)):
                if self.levels[e]>xp:
                    return e,self.levels[e]

    async def bdd_set_xp(self,userID,points,Type='add'):
        """Ajoute/reset de l'xp à un utilisateur dans la database générale"""
        try:
            cnx = self.bot.cogs['ServerCog'].connect()
            cursor = cnx.cursor(dictionary = True)
            if Type=='add':
                query = ("INSERT INTO `{t}` (`userID`,`xp`) VALUES ('{u}','{p}') ON DUPLICATE KEY UPDATE xp = xp + '{p}';".format(t=self.table,p=points,u=userID))
            else:
                query = ("INSERT INTO `{t}` (`userID`,`xp`) VALUES ('{u}','{p}') ON DUPLICATE KEY UPDATE xp = '{p}';".format(t=self.table,p=points,u=userID))
            cursor.execute(query)
            cnx.commit()
            cnx.close()
            return True
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,None)
            return False
    
    async def bdd_get_xp(self,userID):
        try:
            cnx = self.bot.cogs['ServerCog'].connect()
            cursor = cnx.cursor(dictionary = True)
            query = ("SELECT `xp` FROM `{}` WHERE `userID`={}".format(self.table,userID))
            cursor.execute(query)
            liste = list()
            for x in cursor:
                liste.append(x)
            cnx.close()
            return liste
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_error(e,None)
    

    async def get_image_from_url(self,url):
        return ImageTk.PhotoImage(await self.get_raw_image(url))

    async def get_raw_image(self,url,size=282):
        image_byt = requests.get(url,timeout=7).content
        im = io.BytesIO(image_byt)
        im = Image.open(im).resize(size=(size,size),resample=Image.BICUBIC)
        return im

    async def calc_pos(self,text,font,x,y,align='center'):
        w,h = font.getsize(text)
        if align=='center':
            return x-w/2,y-h/2
        elif align=='right':
            return x-w,y-h/2

    async def create_card(self,user,style,xp,rank=[1,0]):
        """Crée la carte d'xp pour un utilisateur"""
        card = Image.open("../cards/model/{}.png".format(style))
        pfp = await self.get_raw_image(user.avatar_url)

        img = Image.new('RGBA', (card.width, card.height), color = (250,250,250,0))
        img.paste(pfp, (20, 29))
        img.paste(card, (0, 0),card)
        card.close()

        name_fnt = ImageFont.truetype('/Library/Fonts/Roboto-Medium.ttf', 40)
        xp_fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 24)
        NIVEAU_fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 42)
        levels_fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf', 65)
        rank_fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf',29)
        RANK_fnt = ImageFont.truetype('/Library/Fonts/Verdana.ttf',23)
        colors = {'name':(124, 197, 118),'xp':(124, 197, 118),'NIVEAU':(255, 224, 77),'rank':(105, 157, 206)}

        d = ImageDraw.Draw(img)
        d.text(await self.calc_pos(user.name,name_fnt,610,68), user.name, font=name_fnt, fill=colors['name'])
        levels_info = await self.calc_level(xp)
        temp = '{} / {} xp'.format(xp,levels_info[1])
        d.text((await self.calc_pos(temp,xp_fnt,625,237)), temp, font=xp_fnt, fill=colors['xp'])
        d.text((380,140), 'NIVEAU', font=NIVEAU_fnt, fill=colors['NIVEAU'])
        d.text((await self.calc_pos(str(levels_info[0]),levels_fnt,740,160,'right')), str(levels_info[0]), font=levels_fnt, fill=colors['xp'])
        temp = '{x[0]}/{x[1]}'.format(x=rank)
        d.text((await self.calc_pos('RANG',RANK_fnt,893,147,'center')), 'RANG', font=RANK_fnt, fill=colors['rank'])
        d.text((await self.calc_pos(temp,rank_fnt,893,180,'center')), temp, font=rank_fnt, fill=colors['rank'])

        img.save('../cards/global/{}-{}.png'.format(user.id,xp))
        return discord.File('../cards/global/{}-{}.png'.format(user.id,xp))


    @commands.command(name='rank',hidden=True)
    @commands.cooldown(1,15,commands.BucketType.user)
    async def rank(self,ctx,*,user:discord.User=None):
        """Display a user XP.
        If you don't send any user, I'll display your own XP"""
        try:
            if user==None:
                user = ctx.author
            xp = await self.bdd_get_xp(user.id)
            if xp==None or len(xp)==0:
                return await ctx.send("Ce membre ne possède pas d'xp !")
            xp = xp[0]['xp']
            style = await self.bot.cogs['UtilitiesCog'].get_xp_style(user)
            await ctx.send(file=await self.bot.cogs['XPCog'].create_card(user,style,xp))
        except Exception as e:
            await self.bot.cogs['ErrorsCog'].on_command_error(ctx,e)


def setup(bot):
    bot.add_cog(XPCog(bot))