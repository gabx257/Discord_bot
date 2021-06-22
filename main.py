import discord
from random import randint
import emoji
from Ping import keep_alive
import json
import os
from event_manager import *

token = os.environ['Token']

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
bot_removed = False
msg = None
bot_add = False
last_guild = None
channel = None


@bot.event
async def on_message(ctx):
    global last_guild
    global channel
    global msg
    global bot_add
    if ctx.guild.id != last_guild:
      with open("configs.json") as file:
        json_file = json.load(file)
        if str(ctx.guild.id) in list(json_file.keys()):
          channel = json_file[str(ctx.guild.id)]["channel"]
          if json_file[str(ctx.guild.id)]["msg"] != None:
            try:
              msg = await ctx.channel.fetch_message(json_file[str(ctx.guild.id)]["msg"])
            except:
              msg = None
          last_guild = ctx.guild.id
    if ctx.channel.name == channel or channel == None:
        if ctx.author != bot.user:
            title = ctx.content.split(" ", 1)[-1]
            size = len(ctx.content.split(" ", 1)[-1].split(" "))
            if ctx.content.startswith("!event"):
                msg = await createConfig(ctx)
            elif ctx.content.startswith("!title"):
                inputConfigValue(0, "Title", title,msg)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!ip") and size == 1:
                inputConfigValue(1, "Min IP", title,msg)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!date") and size == 1:
                msg.embeds[0].set_field_at(2, name="Date", value=title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!time") and size == 1:
                msg.embeds[0].set_field_at(3, name="Time", value=title)
                await atualizaConfig(msg, ctx)
            elif ctx.content.startswith("!class") and size == 2:
               await classCreation(ctx,msg)
            elif ctx.content == "!finish":
                bot_add = True
                await finalTemplateGenerator(ctx,bot,msg)
                bot_add = False
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
                await createTemplate(ctx,bot,msg)
                await ctx.delete()
            elif ctx.content.startswith("!loadTemplate"):
                i = ctx.content.find(" ")
                name = ctx.content[i + 1:]
                with open("templates.json") as file:
                    templates = json.load(file)
                    msg = await createConfig(ctx,list(templates[name].values()))
                    await ctx.channel.send("confirm this template?(y/n)",delete_after = 10)
                    msg2 = await bot.wait_for('message',check=check)
                    if msg2.content == "y":
                      await msg2.delete()
                      bot_add = True
                      await finalTemplateGenerator(ctx,bot,msg)
                      bot_add = False
            elif ctx.content == "!quit":
                await ctx.delete()
                await ctx.guild.leave()
            elif ctx.content == "!setup":
              await setup(ctx,bot)
            elif ctx.content == "!templates":
              with open("templates.json") as file:
                json_file = json.load(file)
              for entry in json_file:
                msg = await createConfig(ctx,list(json_file[entry].values()))
            elif ctx.content.startswith("!manualRemove") and ctx.author.name == "Tomate":
              i = ctx.content.find(" ")
              nick = ctx.content[i + 1:]
              embed = msg.embeds[0]
              for i, field in enumerate(embed.fields):
                if nick in field.value:
                  name = field.name
                  value = field.value.replace(nick, "---")
                  embed.set_field_at(i, name=name, value=value)
                  await msg.edit(embed=embed)
                elif i == len(embed.fields)-1:
                  await ctx.channel.send("not found",delete_after=10)
        with open("configs.json","r+") as file:
          configs = json.load(file)
          configs[str(ctx.guild.id)]["msg"] = str(msg.id)
          file.seek(0)
          json.dump(configs, file, indent=4)
          


@bot.event
async def on_raw_reaction_add(payload):
    global bot_removed
    global bot_add
    if not bot_add:
        info = await get_reaction_info(payload,bot)
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
        info = await get_reaction_info(payload,bot)
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
bot.run(token)