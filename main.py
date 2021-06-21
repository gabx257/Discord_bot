import discord
from random import randint
import emoji
from Ping import keep_alive
import json

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
bot_removed = False
msg = None
bot_add = False
last_guild = None
channel = None


def check(msg):
  return msg.content == "y" or msg.content == "n"


async def setup(ctx):
  await ctx.channel.send("which channel should i use?",delete_after = 20)
  channel = "None"
  msg2 = await bot.wait_for('message')
  if msg2.author == ctx.author:
    if msg2.content in [i.name for i in ctx.guild.channels]:
      channel = msg2.content
      await ctx.channel.send("got it",delete_after = 10)
      msg2.delete()
    else:
      await ctx.channel.send("cant find this channel, please choose another one",delete_after = 10)
      return setup(ctx)
      
  with open("configs.json", "r+") as file:
      json_file = json.load(file)
      new_guild = {str(ctx.guild.id):{"channel":channel}}
      json_file.update(new_guild)
      file.seek(0)
      json.dump(json_file, file, indent=4)

async def get_reaction_info(payload):
    chl = bot.get_channel(payload.channel_id)
    msg = await chl.fetch_message(payload.message_id)
    await bot.wait_until_ready()
    user = bot.get_user(payload.user_id)
    return [msg, user]


async def atualizaConfig(msg, ctx):
    await msg.edit(embed=msg.embeds[0])
    try:
      await ctx.delete()
    except:
      return


def inputConfigValue(posicao, name, valor):
    global msg
    msg.embeds[0].set_field_at(posicao, name=name, value=valor)


async def foot_notes_format(clas, emotes):
    emoji_list = open("emoji list.txt").read()
    emoji_list = emoji_list.split("\n")
    end_string = ""
    for em, cl in zip(emotes, clas):
        e = emoji.emojize(emoji_list[em], use_aliases=True)
        line = "  " + cl + " = " + e
        end_string += line
    return end_string

#---------------------------final message creator------------------------------
async def finalTemplateGenerator(ctx):
    global msg
    global bot_add
    bot_add = True
    embed = msg.embeds[0]
    string_to_list = [i.split(" ") for i in embed.fields[4].value.split("\n")]
    cls = list(map(lambda x: x[0], string_to_list))
    qnt = list(map(lambda x: int(x[1]), string_to_list))
    message_1 = discord.Embed(title=embed.fields[0].value,
                              description="IP: " + embed.fields[1].value +
                              "+" + "\nDate: " + embed.fields[2].value +
                              "\nTime: " + embed.fields[3].value)
    for i, number in enumerate(qnt):
        t = ["---" for i in range(number)]
        message_1.add_field(name=cls[i], value="\n".join(t))
    try:
      await msg.delete()
    except:
      None
    msg = await ctx.channel.send(embed=message_1)
    emoji_list = open("emoji list.txt").read()
    emoji_list = emoji_list.split("\n")
    reactions = []
    for i in range(len(cls)):
        r = randint(0, len(emoji_list) - 1)
        while r in reactions:
            r = randint(0, len(emoji_list) - 1)
        reactions.append(r)
        await bot.wait_until_ready()
        await msg.add_reaction(emoji.emojize(emoji_list[r], use_aliases=True))
    bot_add = False
    s = await foot_notes_format(cls, reactions)
    msg.embeds[0].set_footer(text=s)
    await msg.edit(embed=msg.embeds[0])
    await ctx.delete()

#---------------------------template loader------------------------------
def avalonTemplateGenerator(templates):
    inputConfigValue(0, "Title", templates["Title"])
    inputConfigValue(1, "Min IP", templates["Min IP"])
    inputConfigValue(2, "Date", templates["Date"])
    inputConfigValue(3, "Time", templates["Time"])
    inputConfigValue(4, "Classes", templates["Classes"])

#---------------------------template creation------------------------------
async def createTemplate(ctx):
    global msg
    with open("templates.json", "r+") as file:
        json_file = json.load(file)
        dict_building = {i.name: i.value for i in msg.embeds[0].fields}
        if dict_building["Title"] in json_file:
            await ctx.channel.send(
                "this title is already used, do you want to update it?(y/n)",delete_after = 20)
            msg2 = await bot.wait_for('message', check=check)
            if msg2.content == "n" and msg2.author == ctx.author:
                await ctx.channel.send("please choose another title")
                msg2.delete()
                return
            elif msg2.content == "y" and msg2.author == ctx.author:
                new_entry = {dict_building["Title"]: dict_building}
                json_file.update(new_entry)
                file.seek(0)
                json.dump(json_file, file, indent=4)
                msg2.delete()
        else:
            new_entry = {dict_building["Title"]: dict_building}
            json_file.update(new_entry)
            file.seek(0)
            json.dump(json_file, file, indent=4)

#---------------------------config msg creation------------------------------
async def createConfig(ctx,configs=["-"]*5):
    global msg
    embed = discord.Embed(title="EVENT CONFIGURATION",
                          description="configure your dungeon")
    embed.add_field(name="Title", value=configs[0])
    embed.add_field(name="Min IP", value=configs[1])
    embed.add_field(name="Date", value=configs[2])
    embed.add_field(name="Time", value=configs[3])
    embed.add_field(name="Classes", value=configs[4])
    embed.set_footer(text="Classes should be on format 'Name quantity'")

    msg = await ctx.channel.send(embed=embed)
    await atualizaConfig(msg, ctx)

#---------------------------class creation------------------------------
async def classCreation(ctx):
  if ctx.content.split(" ", 1)[-1].split(" ")[-1].isdecimal():
    desc_now = msg.embeds[0].fields[4].value
    desc = ctx.content.split(" ", 1)[-1]
    if desc_now == "-": desc_now = ""
    if not desc.split(" ")[0] in desc_now:
        desc_now = desc_now + "\n" + desc
    else:
        i = desc_now.find(desc.split(" ")[0])
        j = desc_now.find("\n", i)
        if j == -1: j = 0
        desc_now = desc_now.replace(
            desc.split(" ")[0] + " " + desc_now[j - 1], desc)

    msg.embeds[0].set_field_at(4,
                                name="Classes",
                                value=desc_now)
    await atualizaConfig(msg, ctx)

@bot.event
async def on_message(ctx):
    global last_guild
    global channel
    if ctx.guild.id != last_guild:
      with open("configs.json") as file:
        json_file = json.load(file)
        if str(ctx.guild.id) in list(json_file.keys()):
          channel = json_file[str(ctx.guild.id)]["channel"]
          last_guild = ctx.guild.id
    if ctx.channel.name == channel or channel == None:
        if ctx.author != bot.user:
            title = ctx.content.split(" ", 1)[-1]
            size = len(ctx.content.split(" ", 1)[-1].split(" "))
            if ctx.content == "!setchannel":
                channel = ctx.channel.id
                ctx.delete()
            if ctx.content.startswith("!event"):
                await createConfig(ctx)
            elif ctx.content.startswith("!title"):
                inputConfigValue(0, "Title", title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!ip") and size == 1:
                inputConfigValue(1, "Min IP", title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!date") and size == 1:
                msg.embeds[0].set_field_at(2, name="Date", value=title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!time") and size == 1:
                msg.embeds[0].set_field_at(3, name="Time", value=title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!class") and size == 2:
               await classCreation(ctx)
            elif ctx.content == "!finish":
                await finalTemplateGenerator(ctx)
            elif ctx.content.startswith("!clear") and len(
                    ctx.content.split(" ")) <= 3:
                if ctx.channel.permissions_for(
                        ctx.author
                ).manage_messages or ctx.author.name == "Tomate":
                    t = ctx.content.split(" ")[1:]
                    if len(t) == 1: await ctx.channel.purge(limit=int(t[0]))
                    elif len(t) == 2:
                        await ctx.channel.purge(
                            limit=int(t[0]),
                            check=lambda x: x.author == bot.user)
                    else:
                        await ctx.channel.purge()

            elif ctx.content.startswith("!createTemplate"):
                await createTemplate(ctx)
            elif ctx.content.startswith("!loadTemplate"):
                i = ctx.content.find(" ")
                name = ctx.content[i + 1:]
                with open("templates.json") as file:
                    templates = json.load(file)
                    await createConfig(ctx,list(templates[name].values()))
                    await ctx.channel.send("confirm this template?(y/n)",delete_after = 10)
                    msg2 = await bot.wait_for('message',check=check)
                    if msg2.content == "y":
                      msg2.delete()
                      await finalTemplateGenerator(ctx)
            elif ctx.content == "!quit":
                await ctx.delete()
                await ctx.guild.leave()
            elif ctx.content == "!setup":
              await setup(ctx)
            elif ctx.content == "!templates":
              with open("templates.json") as file:
                json_file = json.load(file)
              for entry in json_file:
                await createConfig(ctx,list(json_file[entry].values()))


@bot.event
async def on_raw_reaction_add(payload):
    global bot_removed
    global bot_add
    if not bot_add:
        info = await get_reaction_info(payload)
        msg = info[0]
        user = info[1]
        member = await msg.guild.fetch_member(user.id)
        if member.nick != None:
          nick = member.nick 
        else: nick = user.name
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
                    if user.name in field.value:
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
        info = await get_reaction_info(payload)
        msg = info[0]
        user = info[1]
        member = await msg.guild.fetch_member(user.id)
        if member.nick != None:
          nick = member.nick 
        else: nick = user.name
        if msg.author == bot.user:
            embed = msg.embeds[0]
            fields = embed.fields
            for i, field in enumerate(fields):
                if user.name in field.value:
                    name = field.name
                    value = field.value.replace(nick, "---")
                    embed.set_field_at(i, name=name, value=value)

            await msg.edit(embed=embed)
    bot_removed = False


keep_alive()
bot.run('NzgxNTEyNzg5MTg0MjE3MDkw.X7-ugA.TFKmoAI8ASIE8v7Q8e-5A1D19zk')