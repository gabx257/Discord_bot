from random import randint
import emoji
import discord
import json

def check(msg):
  return msg.content == "y" or msg.content == "n"


async def setup(ctx,bot):
  await ctx.channel.send("which channel should i use?",delete_after = 20)
  channel = "None"
  msg2 = await bot.wait_for('message')
  if msg2.author == ctx.author:
    if msg2.content in [i.name for i in ctx.guild.channels]:
      channel = msg2.content
      await ctx.channel.send("got it",delete_after = 10)
      await msg2.delete()
    else:
      await ctx.channel.send("cant find this channel, please choose another one",delete_after = 10)
      return setup(ctx)
      
  with open("configs.json", "r+") as file:
      json_file = json.load(file)
      new_guild = {str(ctx.guild.id):{"channel":channel,"msg":msg}}
      json_file.update(new_guild)
      file.seek(0)
      json.dump(json_file, file, indent=4)

async def get_reaction_info(payload,bot):
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


def inputConfigValue(posicao, name, valor,msg):
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
async def finalTemplateGenerator(ctx,bot,msg):
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
    s = await foot_notes_format(cls, reactions)
    msg.embeds[0].set_footer(text=s)
    await msg.edit(embed=msg.embeds[0])
    try:
      await ctx.delete()
    except:
      None
#---------------------------template loader------------------------------
def avalonTemplateGenerator(templates):
    inputConfigValue(0, "Title", templates["Title"])
    inputConfigValue(1, "Min IP", templates["Min IP"])
    inputConfigValue(2, "Date", templates["Date"])
    inputConfigValue(3, "Time", templates["Time"])
    inputConfigValue(4, "Classes", templates["Classes"])

#---------------------------template creation------------------------------
async def createTemplate(ctx,bot,msg):
    with open("templates.json", "r+") as file:
        json_file = json.load(file)
        dict_building = {i.name: i.value for i in msg.embeds[0].fields}
        if dict_building["Title"] in json_file:
            await ctx.channel.send(
                "this title is already used, do you want to update it?(y/n)",delete_after = 20)
            msg2 = await bot.wait_for('message', check=check)
            if msg2.content == "n" and msg2.author == ctx.author:
                await ctx.channel.send("please choose another title")
                await msg2.delete()
                return
            elif msg2.content == "y" and msg2.author == ctx.author:
                new_entry = {dict_building["Title"]: dict_building}
                json_file.update(new_entry)
                file.seek(0)
                json.dump(json_file, file, indent=4)
                await msg2.delete()
        else:
            new_entry = {dict_building["Title"]: dict_building}
            json_file.update(new_entry)
            file.seek(0)
            json.dump(json_file, file, indent=4)

#---------------------------config msg creation------------------------------
async def createConfig(ctx,configs=["-"]*5):
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
    return msg

#---------------------------class creation------------------------------
async def classCreation(ctx,msg):
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
