from random import randint
import emoji
import discord

def check(msg):
    return msg.content == "y" or msg.content == "n"


async def get_reaction_info(payload,bot):
    chl = bot.get_channel(payload.channel_id)
    msg = await chl.fetch_message(payload.message_id)
    await bot.wait_until_ready()
    user = bot.get_user(payload.user_id)
    return [msg, user]

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
    s = await foot_notes_format(cls, reactions) #here
    msg.embeds[0].set_footer(text=s)
    await msg.edit(embed=msg.embeds[0])
    try:
        await ctx.delete()
    except:
        None
    return msg
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
    try:
        await ctx.delete()
    except:
        None
    return msg
