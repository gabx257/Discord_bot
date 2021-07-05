import json
from time import sleep
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


class Manager_commands(commands.Cog):

    @commands.command(hidden=True)
    async def setup(self, ctx):
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
                return self.setup(ctx)

        with open("configs.json", "r+") as file:
            json_file = json.load(file)
            new_guild = {str(ctx.guild.id): {"channel": channel, "msg": msg}}
            json_file.update(new_guild)
            file.seek(0)
            json.dump(json_file, file, indent=4)

    @commands.command(help="clear the chat of msgs. usage: !clear 'qnt' 'bot only?(True/False)'")
    async def clear(self, ctx, arg=100, arg2=False):
        if ctx.channel.permissions_for(
                ctx.author
        ).manage_messages or ctx.author.id == "289922186247012364":
            if arg2:
                check = lambda x: x.author == bot.user
            else:
                check = None
            await ctx.channel.purge(limit=int(arg), check=check)

    @commands.command(hidden = True)
    async def quit(self, ctx):
        await ctx.message.delete()
        await ctx.guild.leave()

    @commands.command(help="manualy remove a person from the list")
    async def manualremove(self, ctx, nick):
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


class Configure_Event(commands.Cog):

    @commands.command(help="setup the title for the event")
    async def title(self, ctx, arg):
        msg = await check_message(ctx)
        msg.embeds[0].set_field_at(0, name="Title", value=arg)
        await msg.edit(embed=msg.embeds[0])
        try:
            await ctx.message.delete()
        except:
            None

    @commands.command(help="setup the min IP for the event")
    async def ip(self, ctx, arg):
        msg = await check_message(ctx)
        msg.embeds[0].set_field_at(1, name="Min IP", value=arg)
        await msg.edit(embed=msg.embeds[0])
        try:
            await ctx.message.delete()
        except:
            None

    @commands.command(help="setup the date for the event")
    async def date(self, ctx, arg):
        msg = await check_message(ctx)
        msg.embeds[0].set_field_at(2, name="Date", value=arg)
        await msg.edit(embed=msg.embeds[0])
        try:
            await ctx.message.delete()
        except:
            None

    @commands.command(help = "setup the time for the event")
    async def time(self, ctx, arg):
        msg = await check_message(ctx)
        msg.embeds[0].set_field_at(3, name="Time", value=arg)
        await msg.edit(embed=msg.embeds[0])
        try:
            await ctx.message.delete()
        except:
            None

    @commands.command(help="setup a new class needed for the event. Ex: !clas 'name' 'qnt'")
    async def clas(self, ctx, name, qnt):
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
        try:
            await ctx.message.delete()
        except:
            None


class Create_Your_Event(commands.Cog):

    @commands.command(help="start the event configuration")
    async def event(self, ctx):
        msg = await event_manager.createConfig(ctx)
        updateMsg(msg)

    @commands.command(help="add the current event on the template list for reuse")
    async def createtemplate(self, ctx):
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

    @commands.command(help="load a template from its title")
    async def loadtemplate(self, ctx, name):
        with open("templates.json") as file:
            templates = json.load(file)
            tmsg = await event_manager.createConfig(ctx, list(templates[name].values()))
            updateMsg(tmsg)
        await ctx.message.delete()

    @commands.command(help="list of all the available templates")
    async def templates(self, ctx):
        with open("templates.json") as file:
            json_file = json.load(file)
        for entry in json_file:
            await event_manager.createConfig(ctx, list(json_file[entry].values()))
        await ctx.message.delete()


@bot.event
async def on_raw_reaction_add(payload):
    await bot.wait_until_ready()
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
                await msg.edit(embed=embed)

            elif str(payload.emoji) == msg.reactions[2].emoji:  # stop--------------
                loot_split.end_event(str(msg.id), embed.fields[0].value)
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
                loot_split.leaving(nick, str(msg.id))
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

bot.add_cog(Configure_Event())
bot.add_cog(Manager_commands())
bot.add_cog(Create_Your_Event())

for i in bot.commands:
    if i.name != "setup":
        i.add_check(checkChannel)
    elif i.name == "manualremove":
        i.add_check(checkChannel)
        i.add_check(checkUser)

@bot.command()
async def tutorial(ctx):
    await ctx.channel.send("Hello! this is a quick tutorial on how to use this bot.",delete_after=60)
    sleep(2)
    await ctx.channel.send("for starters if you want to create you event type !event",delete_after=60)
    sleep(2)
    await bot.get_command("event").__call__(ctx)
    await ctx.channel.send("now if you see this new message you can see 5 diferent categories",delete_after=60)
    sleep(2)
    await ctx.channel.send("you can use the commands: !title, !ip, !date, !time,\
    !clas to setup how you want the event to be",delete_after=60)
    sleep(2)
    await bot.get_command("title").__call__(ctx, "Tutorial event")
    sleep(2)
    await bot.get_command("ip").__call__(ctx, "1200")
    sleep(2)
    await bot.get_command("date").__call__(ctx, "10/05")
    sleep(2)
    await bot.get_command("time").__call__(ctx, "19:30")
    sleep(2)
    await ctx.channel.send("the !clas commands is used like this !clas 'name of the class' 'qnt of people on it'",delete_after=60)
    sleep(2)
    await bot.get_command("clas").__call__(ctx, "Tank", "1")
    sleep(2)
    await bot.get_command("clas").__call__(ctx, "Healer", "1")
    sleep(2)
    await bot.get_command("clas").__call__(ctx, "Dps", "3")
    sleep(2)
    await ctx.channel.send("now that we are ok with the configuration we react on the type of the event\
    we want,splitting loot or not. splitting loot for now at least can only have one class,\
    it will split the loot based on the time the person spent on the event",delete_after=60)
    sleep(5)
    msg1 = await check_message(ctx)
    msg = await event_manager.finalTemplateGenerator(msg1)
    updateMsg(msg)
    await ctx.channel.send("now people can react accordingly to what they will play on the event",delete_after=60)
    sleep(2)
    await ctx.channel.send("you can use the commands !createtemplate to save the event to reuse later,\
    !loadtemplate to load a template from its title (usage: !loadtemplate 'title') and !templates\
    to see the list of all available templates",delete_after=60)
    sleep(2)
    await ctx.channel.send("for more commands or a quick list of all the commands type !help",delete_after=60)


keep_alive()
bot.run(token)
