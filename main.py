import discord
import emoji
import json
import os
from ping import keep_alive
from discord.ext import commands
from event_manager import *
from random import randint

token = "ODU3OTM4NDkxOTAzNTc0MDI2.YNW3fA.BZRjvufi2QwDbLciFI6RqHGK8oA"

test_guild_id = 849727553111064576
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot_removed = False
msg = None
bot_add = False


def updateMsg(ctx):
    with open("configs.json", "r+") as file:
        configs = json.load(file)
        try:
            configs[str(ctx.guild.id)]["msg"] = msg.id
        except:
            configs[str(ctx.guild.id)]["msg"] = None
        file.seek(0)
        json.dump(configs, file, indent=4)


def checkChannel():
    def predicate(ctx):
        guild_id = str(ctx.guild.id)
        with open("configs.json") as file:
            configs = json.load(file)
            if guild_id in list(configs.keys()):
                channel = configs[guild_id]["channel"]
            else:
                return False
        return ctx.channel.name == channel

    return commands.check(predicate)

@bot.command()
async def setup(ctx):
    await ctx.channel.send("which channel should i use?", delete_after=20)
    channel = None
    msg2 = await bot.wait_for('message')
    if msg2.author == ctx.author:
        if msg2.content in [i.name for i in ctx.guild.channels]:
            channel = msg2.content
            await ctx.channel.send("got it", delete_after=10)
            await msg2.delete()
        else:
            await ctx.channel.send("cant find this channel, please choose another one", delete_after=10)
            return setup(ctx)

    with open("configs.json", "r+") as file:
        json_file = json.load(file)
        new_guild = {str(ctx.guild.id): {"channel": channel, "msg": msg}}
        json_file.update(new_guild)
        file.seek(0)
        json.dump(json_file, file, indent=4)


@bot.command()
@checkChannel()
async def event(ctx):
    global msg
    msg = await createConfig(ctx)
    updateMsg(ctx)


@bot.command()
@checkChannel()
async def title(ctx, arg):
    global msg
    msg.embeds[0].set_field_at(0, name="Title", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
@checkChannel()
async def ip(ctx, arg):
    global msg
    msg.embeds[0].set_field_at(1, name="Min IP", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.delete()


@bot.command()
@checkChannel()
async def Date(ctx, arg):
    global msg
    msg.embeds[0].set_field_at(2, name="Date", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.delete()


@bot.command()
@checkChannel()
async def time(ctx, arg):
    global msg
    msg.embeds[0].set_field_at(3, name="Time", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.delete()


@bot.command()
@checkChannel()
async def clas(ctx, name, qnt):
    global msg
    desc_now = msg.embeds[0].fields[4].value
    if desc_now == "-": desc_now = ""
    if not name in desc_now:
        desc_now = desc_now + "\n" + name + " " + qnt
    else:
        i = desc_now.find(name)
        j = desc_now.find("\n", i)
        desc_now = desc_now.replace(
            desc_now[i:j], name + " " + qnt)

    msg.embeds[0].set_field_at(4,
                               name="Classes",
                               value=desc_now)
    await msg.edit(embed=msg.embeds[0])
    await ctx.delete()


@bot.command()
@checkChannel()
async def finish(ctx):
    global bot_add
    global msg
    bot_add = True
    msg = await finalTemplateGenerator(ctx, bot, msg)
    bot_add = False
    updateMsg(ctx)


@bot.command()
@checkChannel()
async def clear(ctx, arg=100, arg2=False):
    if ctx.channel.permissions_for(
            ctx.author
    ).manage_messages or ctx.author.name == "Tomate":
        if arg2:
            check = lambda x: x.author == bot.user
        else:
            check = None
        await ctx.channel.purge(limit=int(arg), check=check)


@bot.command()
@checkChannel()
async def createtemplate(ctx):
    with open("templates.json", "r+") as file:
        json_file = json.load(file)
        dict_building = {i.name: i.value for i in msg.embeds[0].fields}
        if dict_building["Title"] in json_file:
            await ctx.channel.send(
                "this title is already used, do you want to update it?(y/n)", delete_after=20)
            msg2 = await bot.wait_for('message', check=check)
            if msg2.content == "n" and msg2.author == ctx.author:
                await ctx.channel.send("please choose another title", delete_after=20)
                await msg2.delete()
                return
            elif msg2.content == "y" and msg2.author == ctx.author:
                new_entry = {dict_building["Title"]: dict_building}
                json_file.update(new_entry)
                file.seek(0)
                json.dump(json_file, file, indent=4)
                await ctx.channel.send("saved successfully", delete_after=20)
                await msg2.delete()
        else:
            new_entry = {dict_building["Title"]: dict_building}
            json_file.update(new_entry)
            file.seek(0)
            json.dump(json_file, file, indent=4)
            await ctx.channel.send("saved successfully", delete_after=20)
    await ctx.delete()


@bot.command()
@checkChannel()
async def loadtemplate(ctx, name):
    global msg
    global bot_add
    with open("templates.json") as file:
        templates = json.load(file)
        tmsg = await createConfig(ctx, list(templates[name].values()))
        await ctx.channel.send("confirm this template?(y/n)", delete_after=10)
        msg2 = await bot.wait_for('message', check=check)
        if msg2.content == "y":
            await msg2.delete()
            bot_add = True
            await finalTemplateGenerator(ctx, bot, msg)
            bot_add = False
            msg = tmsg
            updateMsg(ctx)


@bot.command()
@checkChannel()
async def templates(ctx):
    with open("templates.json") as file:
        json_file = json.load(file)
    for entry in json_file:
        await createConfig(ctx, list(json_file[entry].values()))


@bot.command()
@checkChannel()
async def quit(ctx):
    await ctx.delete()
    await ctx.guild.leave()


@bot.command()
@checkChannel()
async def manualremove(ctx, nick):
    for i, field in enumerate(embed.fields):
        if nick in field.value:
            name = field.name
            value = field.value.replace(nick, "---")
            embed.set_field_at(i, name=name, value=value)
            await msg.edit(embed=embed)
            break
        elif i == len(embed.fields) - 1:
            await ctx.channel.send("not found", delete_after=10)


@bot.event
async def on_raw_reaction_add(payload):
    global bot_removed
    global bot_add
    if not bot_add:
        info = await get_reaction_info(payload, bot)
        msg = info[0]
        user = info[1]
        member = await msg.guild.fetch_member(user.id)
        if member.nick != None:
            nick = member.nick
        else:
            nick = user.name
        await bot.wait_until_ready()
        if user != bot.user:
            reactions = [i.emoji for i in msg.reactions]
            i = reactions.index(str(payload.emoji))
            if msg.author == bot.user:
                embed = msg.embeds[0]
                fields = embed.fields
                names = []
                values = []
                for field in fields:
                    names.append(field.name)
                    values.append(field.value)
                    if nick in field.value:
                        bot_removed = True
                        await msg.reactions[i].remove(user)
                        return
                if str(payload.emoji) in reactions:
                    v = values[i].replace("---", nick, 1)
                    if v == values[i]:
                        bot_removed == True
                        await msg.reactions[i].remove(user)
                        return
                    embed.set_field_at(i, name=names[i], value=v)

            await msg.edit(embed=embed)


@bot.event
async def on_raw_reaction_remove(payload):
    global bot_removed
    await bot.wait_until_ready()
    if not bot_removed:
        info = await get_reaction_info(payload, bot)
        msg = info[0]
        user = info[1]
        member = await msg.guild.fetch_member(user.id)
        if member.nick != None:
            nick = member.nick
        else:
            nick = user.name
        if msg.author == bot.user:
            embed = msg.embeds[0]
            fields = embed.fields
            for i, field in enumerate(fields):
                if nick in field.value:
                    name = field.name
                    value = field.value.replace(nick, "---")
                    embed.set_field_at(i, name=name, value=value)

            await msg.edit(embed=embed)
    bot_removed = False

keep_alive()
bot.run(token)
