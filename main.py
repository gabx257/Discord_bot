import json

import discord
from discord.ext import commands

import event_manager
import loot_split
from ping import keep_alive

token = "ODU3OTM4NDkxOTAzNTc0MDI2.YNW3fA.BZRjvufi2QwDbLciFI6RqHGK8oA"
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)


def updateMsg(msg):
    with open("configs.json", "r+") as file:
        configs = json.load(file)
        try:
            configs[str(msg.guild.id)]["msg"] = msg.id
        except:
            configs[str(msg.guild.id)]["msg"] = None
        file.seek(0)
        json.dump(configs, file, indent=4)


async def check_message(ctx):
    guild_id = str(ctx.guild.id)
    with open("configs.json", "r+") as file:
        configs = json.load(file)
        try:
            msg = await ctx.channel.fetch_message(configs[guild_id]["msg"])
            return msg
        except:
            return None


def checkChannel(ctx):
    guild_id = str(ctx.guild.id)
    with open("configs.json") as file:
        configs = json.load(file)
        if guild_id in list(configs.keys()):
            return ctx.channel.name == configs[guild_id]["channel"]
        else:
            return False


def checkUser():
    async def predicate(ctx):
        return ctx.author.id == 289922186247012364

    return commands.check(predicate)


@bot.command()
async def setup(ctx):
    msg = check_message(ctx)
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
async def event(ctx):
    msg = await event_manager.createConfig(ctx)
    updateMsg(msg)


@bot.command()
async def title(ctx, arg):
    msg = await check_message(ctx)
    msg.embeds[0].set_field_at(0, name="Title", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
async def ip(ctx, arg):
    msg = await check_message(ctx)
    msg.embeds[0].set_field_at(1, name="Min IP", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
async def date(ctx, arg):
    msg = await check_message(ctx)
    msg.embeds[0].set_field_at(2, name="Date", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
async def time(ctx, arg):
    msg = await check_message(ctx)
    msg.embeds[0].set_field_at(3, name="Time", value=arg)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
async def clas(ctx, name, qnt):
    msg = await check_message(ctx)
    desc_now = msg.embeds[0].fields[4].value
    if desc_now == "-": desc_now = ""
    if not name in desc_now:
        desc_now = desc_now + "\n" + name + " " + qnt
    else:
        i = desc_now.find(name)
        j = desc_now.find("\n", i)
        if j == -1: j = len(desc_now)
        desc_now = desc_now.replace(
            desc_now[i:j], name + " " + qnt)

    msg.embeds[0].set_field_at(4,
                               name="Classes",
                               value=desc_now)
    await msg.edit(embed=msg.embeds[0])
    await ctx.message.delete()


@bot.command()
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
async def createtemplate(ctx):
    msg = await check_message(ctx)
    with open("templates.json", "r+") as file:
        json_file = json.load(file)
        dict_building = {i.name: i.value for i in msg.embeds[0].fields}
        if dict_building["Title"] in json_file:
            await ctx.channel.send(
                "this title is already used, do you want to update it?(y/n)", delete_after=20)
            msg2 = await bot.wait_for('message', check=event_manager.check)
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
    await ctx.message.delete()


@bot.command()
async def loadtemplate(ctx, name):
    with open("templates.json") as file:
        templates = json.load(file)
        tmsg = await event_manager.createConfig(ctx, list(templates[name].values()))
        updateMsg(tmsg)
    await ctx.message.delete()


@bot.command()
async def templates(ctx):
    with open("templates.json") as file:
        json_file = json.load(file)
    for entry in json_file:
        await event_manager.createConfig(ctx, list(json_file[entry].values()))
    await ctx.message.delete()


@bot.command()
async def quit(ctx):
    await ctx.message.delete()
    await ctx.guild.leave()


@bot.command()
async def manualremove(ctx, nick):
    msg = await check_message(ctx)
    embed = msg.embeds[0]
    for i, field in enumerate(embed.fields):
        if nick in field.value:
            name = field.name
            value = field.value.replace(nick, "---")
            embed.set_field_at(i, name=name, value=value)
            await msg.edit(embed=embed)
            break
        elif i == len(embed.fields) - 1:
            await ctx.channel.send("not found", delete_after=10)
    await ctx.message.delete()


@bot.event
async def on_raw_reaction_add(payload):
    await bot. wait_until_ready()
    info = await event_manager.get_reaction_info(payload, bot)
    msg = info[0]
    user = info[1]
    member = await msg.guild.fetch_member(user.id)
    reactions = [i.emoji for i in msg.reactions]
    embed = msg.embeds[0]
    if member.nick is not None:
        nick = member.nick
    else:
        nick = user.name

    if bot.user != user and msg.author == bot.user:  # not bot reaction-------------
        if msg.embeds[0].title == "EVENT CONFIGURATION":  # config msg------------
            if reactions[0] == str(payload.emoji):  # split---------------
                msg = await event_manager.finalMsgSplit(msg)
                await bot.wait_until_ready()
                updateMsg(msg)
            elif reactions[1] == str(payload.emoji):  # nosplit------------
                msg = await event_manager.finalTemplateGenerator(msg)
                await bot.wait_until_ready()
                updateMsg(msg)

        elif "Loot split is enabled" in msg.embeds[0].description:  # lootSplit-----------

            if str(payload.emoji) == reactions[0]:  # join-----------
                await event_manager.updateMembersSplit(payload, reactions, msg, nick, user)

            elif str(payload.emoji) == msg.reactions[1].emoji:  # start------------
                loot_split.event_start(nick, str(msg.id), msg.guild)
                embed.description += "\nEvent is running"
                await msg.edit(embed = embed)

            elif str(payload.emoji) == msg.reactions[2].emoji:  # stop--------------
                loot_split.end_event(str(msg.id))
                embed.description = embed.description.replace("Event is running", "Event is over")
                await msg.edit(embed=embed)

        elif msg.embeds[0].description.split("\n")[-1] == "Loot split is disabled":
            await event_manager.updateMembers(payload, reactions, msg, nick, user)

@bot.event
async def on_raw_reaction_remove(payload):
    await bot.wait_until_ready()
    info = await event_manager.get_reaction_info(payload, bot)
    msg = info[0]
    user = info[1]
    member = await msg.guild.fetch_member(user.id)
    reactions = [i.emoji for i in msg.reactions]
    i = reactions.index(str(payload.emoji))
    if member.nick is not None:
        nick = member.nick
    else:
        nick = user.name
    if msg.author == bot.user:
        embed = msg.embeds[0]
        fields = embed.fields
        if "Loot split is enabled" in msg.embeds[0].description:
            if str(payload.emoji) == reactions[0]:
                value = msg.embeds[0].fields[0].value.replace(nick, "")
                if value == "":
                    value = "---"
                name = msg.embeds[0].fields[0].name
                embed.set_field_at(0, name=name, value=value)
            if str(payload.emoji) == reactions[1]:
                pass
            if str(payload.emoji) == reactions[2]:
                pass
        else:
            if nick in fields[i].value:
                name = fields[i].name
                value = fields[i].value.replace(nick, "---")
                embed.set_field_at(i, name=name, value=value)
            else:
                pass

        await msg.edit(embed=embed)


for i in bot.commands:
    if i.name != "setup":
        i.add_check(checkChannel)
    elif i.name == "manualremove":
        i.add_check(checkChannel)
        i.add_check(checkUser)
keep_alive()
bot.run(token)
