from random import randint

import discord
import emoji
import loot_split


def check(msg):
    return msg.content == "y" or msg.content == "n"


async def get_reaction_info(payload, bot):
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


# ---------------------------final message creator------------------------------
async def add_reactions(msg, cls):
    emoji_list = open("emoji list.txt").read()
    emoji_list = emoji_list.split("\n")
    reactions = []
    for i in range(len(cls)):
        r = randint(0, len(emoji_list) - 1)
        while r in reactions:
            r = randint(0, len(emoji_list) - 1)
        reactions.append(r)
        await msg.add_reaction(emoji.emojize(emoji_list[r], use_aliases=True))
    s = await foot_notes_format(cls, reactions)  # here
    msg.embeds[0].set_footer(text=s)
    await msg.edit(embed=msg.embeds[0])


# ---------------------------final message creator------------------------------
async def finalMsgSplit(msg):
    embed = msg.embeds[0]
    cls = ["join", "start", "stop"]
    message_1 = discord.Embed(title=embed.fields[0].value,
                              description="IP: " + embed.fields[1].value +
                                          "+" + "\nDate: " + embed.fields[2].value +
                                          "\nTime: " + embed.fields[3].value + "\nLoot split is enabled")

    message_1.add_field(name="Participants", value="---")
    msg2 = await msg.channel.send(embed=message_1)
    await msg.delete()
    await add_reactions(msg2, cls)
    return msg2


async def finalTemplateGenerator(msg):
    embed = msg.embeds[0]
    string_to_list = [i.rsplit(" ",1) for i in embed.fields[4].value.split("\n")]
    cls = list(map(lambda x: x[0], string_to_list))
    qnt = list(map(lambda x: int(x[1]), string_to_list))
    message_1 = discord.Embed(title=embed.fields[0].value,
                              description="IP: " + embed.fields[1].value +
                                          "+" + "\nDate: " + embed.fields[2].value +
                                          "\nTime: " + embed.fields[3].value + "\nLoot split is disabled")
    for i, number in enumerate(qnt):
        t = ["---" for i in range(number)]
        message_1.add_field(name=cls[i], value="\n".join(t))
    msg2 = await msg.channel.send(embed=message_1)
    await msg.delete()
    await add_reactions(msg2, cls)
    return msg2


# ---------------------------config msg creation------------------------------
async def createConfig(ctx, configs=["-"] * 5):
    embed = discord.Embed(title="EVENT CONFIGURATION",
                          description="configure your dungeon")
    embed.add_field(name="Title", value=configs[0])
    embed.add_field(name="Min IP", value=configs[1])
    embed.add_field(name="Date", value=configs[2])
    embed.add_field(name="Time", value=configs[3])
    embed.add_field(name="Classes", value=configs[4])
    embed.set_footer(text="Classes should be on format 'Name quantity'")

    msg = await ctx.channel.send(embed=embed)
    await add_reactions(msg, ["splitting loot", "no splitting loot"])
    return msg


async def updateMembers(payload, reactions, msg, nick, user):
    i = reactions.index(str(payload.emoji))
    embed = msg.embeds[0]
    fields = embed.fields
    names = [i.name for i in fields]
    values = [i.value for i in fields]
    for value in values:
        if nick in value:
            await msg.reactions[i].remove(user)
            return
    if str(payload.emoji) in reactions:
        v = values[i].replace("---", nick, 1)
        if v == values[i]:
            await msg.reactions[i].remove(user)
            return
        embed.set_field_at(i, name=names[i], value=v)
        await msg.edit(embed=embed)


async def updateMembersSplit(payload, reactions, msg, nick, user):
    embed = msg.embeds[0]
    field = embed.fields[0]
    if "Event is running" not in embed.description:
        await msg.reactions[0].remove(user)
        return
    if nick in field.value:
        await msg.reactions[0].remove(user)
        return
    if str(payload.emoji) == reactions[0]:
        if field.value == "---":
            field.value = ""
        v = field.value + "\n"+nick
        embed.set_field_at(0, name=field.name, value=v)
        loot_split.joining(nick, str(msg.id))
        await msg.edit(embed=embed)
