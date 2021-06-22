from datetime import datetime
import discord
import json

def joining(name, event_id,initial_time=datetime.now()):
  with open("event_list.json","r+") as file:
    event_list = json.load(file)
    ctx_event = event_list[event_id]
    names = [i["name"] for i in ctx_event["participants"]]
    if name not in names:
      ctx_event["participants"].append({"name":name,"start_time":initial_time,"end_time":None,"loot":0})
      event_list[event_id] = ctx_event
      file.seek()
      json.dump(event_list,file)
    else:
      pass #add bot msg?

def leaving(name, event_id, leaving_time=datetime.now()):
  with open("event_list.json","r+") as file:
      event_list = json.load(file)
      ctx_event = event_list[event_id]
      names = [i["name"] for i in ctx_event["participants"]]
      if name in names:
        i = names.index(name)
        ctx_event["participants"][i]["end_time"] = leaving_time
        event_list[event_id] = ctx_event
        file.seek()
        json.dump(event_list,file)
      else:
        pass #add bot msg?

def event_start(start,owner,id,guild):
  with open("event_list.json","r+") as file:
    event_list = json.load(file)
    event_list[id] = {"guild":guild,"creator":owner,"start":start,"loot":0,"participants":[]}
    file.seek()
    json.dump(event_list,file)



def split(event_id):
    with open("event_list.json","r+") as file:
      event_list = json.load(file)
      ctx_event = event_list[event_id]
      loot = ctx_event["loot"]
      participants = ctx_event["participants"]
      total_time = sum([x["end_time"]-x["start_time"] for x in participants])
      loot_per_time = loot/total_time
      for p in participants:
        p["loot"] = (p["end_time"]-p["start_time"])*loot_per_time
      event_list[event_id] = ctx_event
      file.seek()
      json.dump(event_list,file)

def end_event(event_id,end_time=datetime.now()):
  with open("event_list.json","r+") as file:
    event_list = json.load(file)
    ctx_event = event_list[event_id]
    participants = ctx_event["participants"]
    for person in participants:
      leaving(person["name"],event_id)
    split(event_id)