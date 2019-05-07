from discord.ext import commands

import discord
from discord.ext.commands.cooldowns import BucketType
import asyncio
from PIL import Image, ImageEnhance, ImageSequence
import PIL
#pip install Pillow
from io import BytesIO
import io
import datetime
import aiohttp
import copy
import sys
import time
from resizeimage import resizeimage
#pip install python-resize-image
import math



class BlurpleCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.file = 'blurple'
        try:
            self.translate = self.bot.cogs["LangCog"].tr
        except:
            pass
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.translate = self.bot.cogs["LangCog"].tr

    @commands.command(name="isblurple",aliases=['blurple'])
    @commands.cooldown(rate=1, per=180, type=BucketType.user)
    async def blurple_cmd(self,ctx, url = None):
        """Be part of the best birthday of the WORLD, and check if you're enough blurple to be cool!
        You can either give a user or an image URL in argument, or attach an image to your message. Plz don't forget to be cool."""
        picture = None

        start = time.time()
        if url != None:
            try:
                user = await commands.UserConverter().convert(ctx,url)
                picture = str(user.avatar_url)
            except Exception:
                picture = url
        else:
            link = ctx.message.attachments
            if len(link) != 0:
                for image in link:
                    picture = image.url

        if picture == None:
            picture = ctx.author.avatar_url_as(size=1024)

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(str(picture)) as r:
                    response = await r.read()
        except ValueError:
            await ctx.send(str(await self.translate(ctx.guild,"blurple","check_invalid")).format(ctx.message.author.mention))
            return

        colourbuffer = 20

        try:
            im = Image.open(BytesIO(response))
        except Exception:
            await ctx.send(str(await self.translate(ctx.guild,"blurple","check_invalid")).format(ctx.message.author.mention))
            return
        
        await ctx.send(str(await self.translate(ctx.guild,"blurple","check_intro")).format(ctx.message.author.mention))

        im = im.convert('RGBA')
        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        maxpixelcount = 1562500

        end = time.time()
        start = time.time()
        if impixels > maxpixelcount:
            downsizefraction = math.sqrt(maxpixelcount/impixels)
            im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
            imsize = list(im.size)
            impixels = imsize[0]*imsize[1]
            end = time.time()
            await ctx.send(str(await self.translate(ctx.guild,"blurple","check_resized")).format(ctx.message.author.mention,round(end-start,2)))
            start = time.time()

        def imager(im):
            global noofblurplepixels
            noofblurplepixels = 0
            global noofwhitepixels
            noofwhitepixels = 0
            global noofdarkblurplepixels
            noofdarkblurplepixels = 0
            global nooftotalpixels
            nooftotalpixels = 0
            global noofpixels
            noofpixels = 0

            blurple = (114, 137, 218)
            darkblurple = (78, 93, 148)
            white = (255, 255, 255)
            
            img = im.load()

            for x in range(imsize[0]):
                i = 1
                for y in range(imsize[1]):
                    pixel = img[x,y]
                    check = 1
                    checkblurple = 1
                    checkwhite = 1
                    checkdarkblurple = 1
                    for i in range(3):
                        if not(blurple[i]+colourbuffer > pixel[i] > blurple[i]-colourbuffer):
                            checkblurple = 0
                        if not(darkblurple[i]+colourbuffer > pixel[i] > darkblurple[i]-colourbuffer):
                            checkdarkblurple = 0
                        if not(white[i]+colourbuffer > pixel[i] > white[i]-colourbuffer):
                            checkwhite = 0
                        if checkblurple == 0 and checkdarkblurple == 0 and checkwhite == 0:
                            check = 0
                    if check == 0:
                        img[x,y] = (0, 0, 0, 255)
                    if check == 1:
                        nooftotalpixels += 1
                    if checkblurple == 1:
                        noofblurplepixels += 1
                    if checkdarkblurple == 1:
                        noofdarkblurplepixels += 1
                    if checkwhite == 1:
                        noofwhitepixels += 1
                    noofpixels += 1

            image_file_object = io.BytesIO()
            im.save(image_file_object, format='png')
            image_file_object.seek(0)
            return image_file_object

        async with aiohttp.ClientSession() as _:
            start = time.time()
            image = await self.bot.loop.run_in_executor(None, imager, im)
            end = time.time()
            image = discord.File(fp=image, filename='image.png')

            blurplenesspercentage = round(((nooftotalpixels/noofpixels)*100), 2)
            percentblurple = round(((noofblurplepixels/noofpixels)*100), 2)
            percentdblurple = round(((noofdarkblurplepixels/noofpixels)*100), 2)
            percentwhite = round(((noofwhitepixels/noofpixels)*100), 2)

            fields_txt = await self.translate(ctx.guild,"blurple","check_fields")
            embed = discord.Embed(Title = "", colour = 0x7289DA, description=fields_txt[5])
            if blurplenesspercentage>=99.99:
                embed.add_field(name=fields_txt[0], value=f"{blurplenesspercentage}% :tada:", inline=False)
            else:
                embed.add_field(name=fields_txt[0], value=f"{blurplenesspercentage}%", inline=False)
            embed.add_field(name=fields_txt[1], value=f"{percentblurple}%", inline=True)
            embed.add_field(name=fields_txt[2], value=f"{percentwhite}%", inline=True)
            embed.add_field(name=fields_txt[3], value=f"{percentdblurple}%", inline=True)
            embed.add_field(name="Guide", value=fields_txt[4], inline=False)
            embed.set_footer(text=fields_txt[6].format(ctx.author))
            embed.set_image(url="attachment://image.png")
            embed.set_thumbnail(url=picture)
            await ctx.send(embed=embed, file=image)


    @commands.command(aliases=['blurplfy', 'blurplefier'])
    @commands.cooldown(rate=1, per=180, type=BucketType.user)
    async def blurplefy(self,ctx, url = None):
        """Be even more cool, and blurpelize your avatar for this coolest birthday of the century.
        You can either give a user or an image URL in argument, or attach an image to your message. Plz don't forget to be cool."""
        picture = None


        if url != None:
            try:
                user = await commands.UserConverter().convert(ctx,url)
                picture = str(user.avatar_url)
            except Exception:
                picture = url
        else:
            link = ctx.message.attachments
            if len(link) != 0:
                for image in link:
                    picture = image.url

        if picture == None:
            picture = ctx.author.avatar_url

        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(str(picture)) as r:
                    response = await r.read()
        except ValueError:
            await ctx.send(str(await self.translate(ctx.guild,"blurple","check_invalid")).format(ctx.message.author.mention))
            return


        try:
            im = Image.open(BytesIO(response))
        except Exception:
            await ctx.send(str(await self.translate(ctx.guild,"blurple","check_invalid")).format(ctx.message.author.mention))
            return

        await ctx.send(str(await self.translate(ctx.guild,"blurple","check_intro")).format(ctx.message.author.mention))

        imsize = list(im.size)
        impixels = imsize[0]*imsize[1]
        maxpixelcount = 1562500

        try:
            _ = im.info["version"]
            isgif = True
            gifloop = int(im.info["loop"])
        except Exception:
            isgif = False


        if impixels > maxpixelcount:
            downsizefraction = math.sqrt(maxpixelcount/impixels)
            im = resizeimage.resize_width(im, (imsize[0]*downsizefraction))
            imsize = list(im.size)
            impixels = imsize[0]*imsize[1]

        def imager(im):
            im = im.convert(mode='L')
            im = ImageEnhance.Contrast(im).enhance(1000)
            im = im.convert(mode='RGB')

            img = im.load()

            for x in range(imsize[0]-1):
                for y in range(imsize[1]-1):
                    pixel = img[x,y]

                    if pixel != (255, 255, 255):
                        img[x,y] = (114, 137, 218)

            image_file_object = io.BytesIO()
            im.save(image_file_object, format='png')
            image_file_object.seek(0)
            return image_file_object

        def gifimager(im, gifloop):
            frames = [frame.copy() for frame in ImageSequence.Iterator(im)]
            newgif = []

            for frame in frames:

                frame = frame.convert(mode='L')
                frame = ImageEnhance.Contrast(frame).enhance(1000)
                frame = frame.convert(mode='RGB')

                img = frame.load()

                for x in range(imsize[0]):
                    for y in range(imsize[1]):
                        pixel = img[x,y]

                        if pixel != (255, 255, 255):
                            img[x,y] = (114, 137, 218)

                newgif.append(frame)

            image_file_object = io.BytesIO()

            gif = newgif[0]
            gif.save(image_file_object, format='gif', save_all=True, append_images=newgif[1:], loop=0)

            image_file_object.seek(0)
            return image_file_object


        async with aiohttp.ClientSession() as _:
            if isgif == False:
                image = await self.bot.loop.run_in_executor(None, imager, im)
            else:
                image = await self.bot.loop.run_in_executor(None, gifimager, im, gifloop)
            if isgif == False:
                image = discord.File(fp=image, filename='image.png')
            else:
                image = discord.File(fp=image, filename='image.gif')
            try:
                embed = discord.Embed(Title = "", colour = 0x7289DA)
                embed.set_author(name=await self.translate(ctx.guild,'blurple','create_title'))
                if isgif == False:
                    embed.set_image(url="attachment://image.png")
                    embed.set_footer(text=str(await self.translate(ctx.guild,'blurple','create_footer_1')).format(ctx.author))
                else:
                    embed.set_image(url="attachment://image.gif")
                    embed.set_footer(text=str(await self.translate(ctx.guild,'blurple','create_footer_2')).format(ctx.author))
                embed.set_thumbnail(url=picture)
                await ctx.send(embed=embed, file=image)
            except Exception:
                await ctx.send(str(await self.translate(ctx.guild,'blurple','create_footer_2')).format(ctx.author.mention))


def setup(bot):
    bot.add_cog(BlurpleCog(bot))