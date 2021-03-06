import discord
from discord.ext import commands

async def can_mute(ctx):
    """Check if someone can mute"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"mute")
    else:
        return ctx.channel.permissions_for(ctx.author).manage_roles

async def can_warn(ctx):
    """Check if someone can warn"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"warn")
    else:
        return ctx.channel.permissions_for(ctx.author).manage_roles

async def can_kick(ctx):
    """Check if someone can kick"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"kick")
    else:
        return ctx.channel.permissions_for(ctx.author).kick_members

async def can_ban(ctx):
    """Check if someone can ban"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"ban")
    else:
        return ctx.channel.permissions_for(ctx.author).ban_members

async def can_slowmode(ctx):
    """Check if someone can use slowmode"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"slowmode")
    else:
        return ctx.channel.permissions_for(ctx.author).manage_channels

async def can_clear(ctx):
    """Check if someone can use clear"""
    if ctx.bot.database_online:
        return await ctx.bot.cogs["ServerCog"].staff_finder(ctx.author,"clear")
    else:
        return ctx.channel.permissions_for(ctx.author).manage_messages

async def has_admin(ctx):
    """Check if someone can see the banlist"""
    return ctx.channel.permissions_for(ctx.author).administrator or await ctx.bot.cogs["AdminCog"].check_if_god(ctx)

async def has_manage_msg(ctx):
    """... if someone can pin a message"""
    return ctx.channel.permissions_for(ctx.author).manage_messages or await ctx.bot.cogs["AdminCog"].check_if_god(ctx)

async def has_manage_guild(ctx):
    """... if someone can manage the server"""
    return ctx.channel.permissions_for(ctx.author).manage_guild or await ctx.bot.cogs['AdminCog'].check_if_god(ctx)

async def has_manage_roles(ctx):
    """... if someone can manage the roles"""
    return ctx.channel.permissions_for(ctx.author).manage_roles or await ctx.bot.cogs['AdminCog'].check_if_god(ctx)

async def has_manage_nicknames(ctx):
    """... if someone can change nicknames"""
    return ctx.channel.permissions_for(ctx.author).manage_nicknames or await ctx.bot.cogs['AdminCog'].check_if_god(ctx)

async def has_embed_links(ctx:commands.Context):
    """... if someone can send embeds"""
    if not isinstance(ctx.author,discord.Member):
        return True
    return ctx.channel.permissions_for(ctx.author).embed_links or await ctx.bot.cogs['AdminCog'].check_if_god(ctx)

async def verify_role_exists(ctx:commands.Context):
    """Check if the verify role exists"""
    if ctx.guild==None:
        return False
    roles_raw = await ctx.bot.cogs['ServerCog'].find_staff(ctx.guild.id,"verification_role")
    if roles_raw==None:
        return False
    roles = [r for r in [ctx.guild.get_role(int(x)) for x in roles_raw.split(';') if x.isnumeric() and len(x)>0] if r!=None]
    return len(roles) > 0

async def database_connected(ctx:commands.Context):
    "Check if the database is online and accessible"
    return ctx.bot.database_online

async def is_fun_enabled(ctx,self=None):
    if self == None:
        if hasattr(ctx, 'bot'):
            self = ctx.bot.get_cog("FunCog")
        else:
            return False
    if ctx.guild == None:
        return True
    if not ctx.bot.database_online and not ctx.guild.channels[0].permissions_for(ctx.author).manage_guild:
        return False
    ID = ctx.guild.id
    if str(ID) not in self.fun_opt.keys():
        fun = await ctx.bot.cogs["ServerCog"].find_staff(ID,"enable_fun")
        self.fun_opt[str(ID)] = fun
    else:
        fun = self.fun_opt[str(ID)]
        if fun==None:
            fun = await ctx.bot.cogs["ServerCog"].find_staff(ID,"enable_fun")
            if fun!=None:
                self.fun_opt[str(ID)] = fun
    return fun == 1 or fun == True

async def is_a_cmd(msg: discord.Message, bot: commands.Bot) -> bool:
    "Check if a message is a command"
    pr = await bot.get_prefix(msg)
    is_cmd = False
    for p in pr:
        is_cmd = is_cmd or msg.content.startswith(p)
    return is_cmd